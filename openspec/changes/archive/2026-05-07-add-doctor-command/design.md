## Context

`from-scratch` instala archivos en `~/.claude/` y registra lo que instaló en `~/.claude/from-scratch/.state.json` (hashes SHA256). Hoy no hay forma de verificar si esa instalación sigue siendo coherente. Los usuarios reportan problemas sin datos concretos; los agentes de IA no pueden auto-diagnosticar.

El módulo `src/sync/diff.py` ya implementa la lógica de comparar estado contra disco (`compute_diff`). El doctor reutiliza esa misma lógica en modo lectura.

## Goals / Non-Goals

**Goals:**
- Nuevo subcomando `from-scratch doctor` offline.
- Tres formatos de output: texto plano (default), JSON (`--json`), Markdown (`--markdown`).
- Exit codes semánticos: `0` OK, `1` warnings, `2` errores.
- Cubrir los checks: estado del binario, `.state.json`, integridad de archivos en disco, archivos `.tmp.*` huérfanos, acumulación de `.bak.*`.
- Log rotante best-effort en `~/.claude/from-scratch/doctor.log` (JSON Lines, últimas 20 entradas).
- Slash command `/from-scratch:doctor` en el catálogo para usar desde Claude Code.

**Non-Goals:**
- Auto-reparación — `init` y `update` ya hacen eso.
- Verificación de URLs remotas / `template_url` — mantener el diagnóstico offline.
- Inspección del contenido de los archivos instalados (links en markdown).

## Decisions

### 1. Reutilizar `compute_diff` vs. lógica propia

`compute_diff` compara el catálogo remoto contra el estado local para proponer cambios. El doctor necesita algo diferente: comparar el *estado registrado* contra el *disco actual* sin involucrar el catálogo.

**Decisión:** lógica propia en `doctor.py`. La función es simple (iterar `installed_files`, comparar hashes) y acoplarla al pipeline de sync generaría dependencias innecesarias.

### 2. Formato de output

Tres formatos, mutuamente excluyentes (se toma el último flag si se pasan varios):

- **Texto** (default): secciones con etiquetas `[ESTADO]`, `[ARCHIVOS]`, etc. + `=== RESUMEN ===` al final. Para pegar en terminal o chat.
- **JSON** (`--json`): objeto con `schema_version`, `timestamp`, `status`, `checks`, `summary`. Para consumo programático sin regex.
- **Markdown** (`--markdown`): tablas y headers markdown. Rinde bien cuando se pega en Claude chat o se incluye en un issue de GitHub — más legible que el texto plano en interfaces que renderizan markdown.

Ejemplo de output `--markdown`:

```
# from-scratch doctor (2026-05-06T20:15:00)

## Estado del sistema
| Check | Estado | Detalle |
|-------|--------|---------|
| Binario | ✓ OK | `/usr/local/bin/from-scratch` |
| State file | ✓ OK | Última sync: 2026-05-06T20:11:41 · 3 archivos |

## Archivos instalados
| Archivo | Estado |
|---------|--------|
| `commands/new-project.md` | ✓ OK |

## Residuos
| Tipo | Estado |
|------|--------|
| .tmp huérfanos | ✓ OK |

## Resumen
**estado: OK** — la instalación está en buen estado.
```

Los tres formatos exponen los mismos datos — solo cambia la presentación.

### 3. Severidades

Tres niveles, siguiendo la convención de herramientas como `eslint` y `tsc`:

| Nivel | Exit code | Ejemplos |
|-------|-----------|---------|
| OK | 0 | Todo en orden |
| WARN | 1 | `.bak` acumulados, sync incompleto recuperado |
| ERROR | 2 | Archivo faltante en disco, `.state.json` corrupto, `.tmp` huérfano |

Los `.tmp.*` huérfanos son ERROR porque indican una escritura interrumpida que puede haber dejado el disco en estado inconsistente.

### 4. Checks a realizar (en orden)

1. **Wrapper/binario**: existe `/usr/local/bin/from-scratch` o el binario en `PATH` y es ejecutable.
2. **State file**: `~/.claude/from-scratch/.state.json` existe y es parseable; flag `has_incomplete_sync`.
3. **Integridad de archivos**: por cada entrada en `installed_files`, verificar que el archivo existe en `~/.claude/` y que su hash SHA256 coincide con el registrado.
4. **Orphans `.tmp.*`**: buscar `*.tmp.*` bajo `~/.claude/`.
5. **Backups `.bak.*`**: contar `*.bak.*` bajo `~/.claude/` — warning si hay más de 5 por archivo.

### 5. Versionado del schema JSON

El campo `status` del output JSON y la estructura de cada objeto en `checks` son la interfaz pública del doctor para consumo por agentes. Para soportar evolución sin romper parsers existentes, el objeto raíz incluye un campo `schema_version` con valor `"1"` (string, no número, para evitar ambigüedad de tipo en JSON).

```json
{
  "schema_version": "1",
  "timestamp": "...",
  "status": "ok",
  "checks": [...],
  "summary": { "error_count": 0, "warn_count": 0 }
}
```

Si en el futuro se agregan campos (ej. `environment`, `catalog_version`) o se cambia la estructura de `checks`, se incrementa `schema_version`. Los consumidores que no reconocen la versión pueden emitir warning en lugar de parsear incorrectamente.

### 6. Log rotante

El doctor escribe una entrada de log en `~/.claude/from-scratch/doctor.log` al finalizar cada ejecución. El propósito es permitir detectar regresiones entre runs ("¿cuándo empezó a aparecer este ERROR?") y dar contexto histórico en sesiones de soporte.

**Formato:** JSON Lines — un objeto JSON por línea:
```
{"timestamp": "2026-05-06T20:15:00Z", "status": "ok", "error_count": 0, "warn_count": 0}
```
Se almacena solo el resumen (no la lista completa de checks) para mantener el archivo pequeño.

**Rotación:** antes de appender, leer el archivo, conservar las últimas 19 líneas no vacías y escribir con la nueva entrada al final. Límite: 20 entradas. Escritura atómica (tmp + rename), igual que `.state.json`.

**Best-effort:** si la escritura falla por cualquier razón (`PermissionError`, disco lleno, directorio inexistente), el doctor captura la excepción silenciosamente y termina con el exit code que corresponde al diagnóstico — el fallo del log nunca degrada el resultado del diagnóstico.

### 7. Slash command en catálogo

`catalog/commands/from-scratch/doctor.md` es una entrada de catálogo (igual que `new-project.md` y `sync-skills.md`) que `from-scratch init`/`update` instala en `~/.claude/commands/from-scratch/doctor.md`.

El contenido del archivo es un prompt de sistema que instruye al agente Claude Code a:
1. Ejecutar `from-scratch doctor` (preferiblemente con `--markdown` para un output más legible).
2. Interpretar el reporte e identificar los problemas.
3. Explicar qué significa cada issue y qué comando correr para remediarlo.

No requiere código Python nuevo — es exclusivamente un archivo de catálogo markdown con frontmatter `description`.

### 8. Ubicación del código

```
src/commands/doctor.py     ← orquestador + formato de output
src/ui/doctor.py           ← strings de presentación (Spanish)
```

`src/ui/` ya tiene un módulo por comando (`hints.py`, `errors.py`). El doctor sigue el mismo patrón.

### Contrato con `StateCorruptError`

`check_state_file()` no debe reimplementar el parseo de JSON ni capturar `json.JSONDecodeError` directamente. Debe llamar a `read_state()` de `src/state/state.py` y capturar `StateCorruptError` (definido en `src/errors.py`). Esto garantiza que el doctor reutiliza la misma lógica de validación que el resto del CLI y mantiene el error dentro de la jerarquía `FromScratchError`.

Cuando `read_state()` lanza `StateCorruptError`, el doctor reporta ERROR con remediación `from-scratch init --force`. No propaga la excepción al orquestador principal — el doctor nunca debe terminar con una traza no controlada por un state file corrupto.

## UX: Comportamiento del usuario

### Feedback durante la ejecución

El doctor es un comando offline que opera sobre archivos locales pequeños (<50 KB). No muestra spinner ni progress bar. Sí imprime cada sección a medida que la completa (output progresivo por sección), de modo que el usuario ve actividad sin necesidad de esperar al bloque `=== RESUMEN ===`.

### Output en el caso feliz

Cuando todos los checks pasan sin warnings ni errores, el bloque `=== RESUMEN ===` muestra:

```
=== RESUMEN ===
estado: OK — la instalación está en buen estado.
Consejo: ejecutá `from-scratch doctor` periódicamente o cuando algo no funcione como esperás.
```

No se omite el resumen cuando todo está bien — el usuario debe ver confirmación explícita de que el diagnóstico se completó.

### Hints contextuales al finalizar con problemas

El bloque `=== RESUMEN ===` siempre termina con un hint de próximo paso, ajustado al estado global:

- **Solo warnings:** `Tip: ejecutá \`from-scratch update\` para sincronizar la instalación.`
- **Errores presentes:** `Tip: ejecutá \`from-scratch init\` o \`from-scratch update\` para reparar los errores listados arriba.`

El hint aparece una sola vez al final (no se repite por cada item en error). Los items individuales con ERROR o WARN ya llevan su `remediation` inline.

### Remediaciones explícitas por tipo de check

| Check | STATUS | Remediación que se imprime |
|-------|--------|---------------------------|
| `.tmp.*` huérfanos | ERROR | `rm ~/.claude/**/*.tmp.*` |
| `.bak.*` acumulados | WARN | `rm ~/.claude/**/*.bak.*` (solo si el usuario decide limpiarlos; se informa la cantidad) |
| Archivo faltante en disco | ERROR | `from-scratch update` |
| State file inexistente | ERROR | `from-scratch init` |
| State file corrupto | ERROR | `from-scratch init --force` |
| Sync incompleta | WARN | `from-scratch update` |
| Binario no en PATH | WARN | Re-ejecutar el instalador: `curl -fsSL <url> \| bash` |

Cada item de check en el output texto incluye la remediación inline cuando el status no es OK. En JSON, el campo `remediation` es `null` cuando el status es `ok`.

### Destino del output

- El reporte (texto o JSON) va siempre a **stdout** — incluso cuando hay errores. Esto permite que `from-scratch doctor --json | jq` funcione sin sorpresas.
- Trazas de excepción internas (bugs del propio doctor, `PermissionError` no capturado) van a **stderr** y no contaminan el JSON.

### Idempotencia

El diagnóstico en sí es idempotente: los mismos checks producen el mismo output para el mismo estado del sistema. La única excepción es el log rotante — cada run agrega una entrada — pero eso es un efecto de observabilidad, no una mutación del sistema diagnosticado. El estado de `~/.claude/` nunca cambia como consecuencia de correr `doctor`.

## Risks / Trade-offs

- **Hash de archivos grandes**: calcular SHA256 de archivos instalados es O(n·tamaño). Los archivos del catálogo son markdown pequeños (<50 KB), por lo que el impacto es despreciable. Si el catálogo crece significativamente, considerar leer solo los primeros N bytes.
- **Path del binario**: el wrapper puede instalarse en ubicaciones no estándar. El doctor busca via `shutil.which("from-scratch")` — si no está en `PATH`, reporta warning en vez de error (el usuario puede estar corriendo el CLI directo con `python -m cli`).
- **Permisos**: si `~/.claude/` tiene permisos restrictivos, la lectura puede fallar. Capturar `PermissionError` como ERROR con remediación.
