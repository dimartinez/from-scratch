## Context

El CLI instala archivos desde el catálogo hacia `~/.claude/` y registra lo instalado en `~/.claude/from-scratch/.state.json`. Además, el installer (`install.sh`) deja el código del tool en `~/.from-scratch/` y un wrapper ejecutable en `~/.local/bin/from-scratch`. Hasta ahora no existe forma de deshacer ninguna de estas tres capas.

## Goals / Non-Goals

**Goals:**

- Implementar `from-scratch uninstall` como espejo completo de `init`.
- Borrar los tres niveles: archivos del catálogo, state, y el tool mismo (directorio + wrapper).
- Mostrar preview de lo que se va a borrar y pedir confirmación antes de actuar.
- Si el state no existe, salir limpiamente con mensaje informativo (ya desinstalado).

**Non-Goals:**

- Desinstalación parcial o selectiva de archivos individuales.
- Preservar archivos modificados por el usuario (un uninstall completo los borra igual).
- Flag `--force` — el comando es destructivo por diseño; la confirmación es el contrato.

## Decisions

### 1. Borrar todos los `installed_files` sin chequear hash

**Decisión**: el uninstall borra todo lo que figure en `installed_files`, independientemente de si el hash coincide (es decir, aunque el usuario haya modificado el archivo).

**Alternativa descartada**: verificar hash y omitir archivos modificados (comportamiento análogo a `user_modified` en diff). Se descartó porque quien ejecuta `uninstall` quiere un entorno limpio completo; la protección de archivos modificados es una garantía de `init`/`update`, no de `uninstall`.

### 2. Orden de borrado: catálogo → state → tool → wrapper

**Decisión**: primero se borran los archivos del catálogo, luego el directorio de state, luego `~/.from-scratch/`, finalmente el wrapper. El proceso Python ya tiene todo cargado en memoria al momento de borrarse a sí mismo.

**Rationale**: si el proceso interrumpiera entre el state y el wrapper, quedaría un wrapper que apunta a un directorio inexistente — fácil de limpiar manualmente. Al revés (borrar el wrapper primero), el state quedaría huérfano, lo que es más confuso.

### 3. Limpiar directorios vacíos bajo `~/.claude/`

**Decisión**: después de borrar los archivos del catálogo, recorrer los directorios afectados de hoja a raíz y eliminar los que quedaron vacíos. Solo se consideran candidatos a borrado los directorios padre de rutas en `installed_files` — es decir, directorios que from-scratch sabe que usó. Nunca se borran directorios no relacionados con las rutas instaladas.

**Rationale**: `commands/from-scratch/` fue creado exclusivamente para from-scratch. Si borramos `sync-skills.md` y el directorio queda vacío, dejarlo es ruido. Restringir el barrido a directorios derivados de `installed_files` garantiza que un directorio como `~/.claude/commands/mi-proyecto/` que el usuario creó por su cuenta nunca sea tocado, aunque accidentalmente quedara vacío por otra razón.

**Límite**: solo se borran directorios vacíos que queden *dentro* de `~/.claude/`; nunca `~/.claude/` en sí.

### 4. Manejo de `StateCorruptError` durante uninstall

**Decisión**: si `read_state` lanza `StateCorruptError` (el archivo existe pero es JSON inválido o tiene formato inesperado), el comando imprime el error con su remediación habitual y retorna exit code 1. No intenta borrar nada sin una lista confiable de `installed_files`.

**Rationale**: un state corrupto es evidencia de una condición anómala. Proceder con un borrado parcial sin saber qué archivos se instalaron podría dejar `~/.claude/` en un estado peor. La remediación existente de `StateCorruptError` ("rm ~/.claude/from-scratch/.state.json && from-scratch init") sigue siendo accionable: el usuario puede borrar el state manualmente y luego re-instalar.

**Alternativa descartada**: ofrecer un modo degradado que borre solo el state dir, tool dir y wrapper sin tocar los archivos del catálogo. Se descartó por complejidad añadida sin caso de uso claro.

### 5. Borrado del state dir mediante `shutil.rmtree`

**Decisión**: `run_uninstall` usa `shutil.rmtree` directamente para borrar el state dir (`~/.claude/from-scratch/`). No pasa por `src/sync/copy_file`.

**Rationale**: `copy_file` en `src/sync/` está diseñado para escrituras atómicas, no para borrado de árboles. No existe una primitiva `delete_dir` en el proyecto. Dado que el state dir solo contiene `.state.json` (archivos que from-scratch creó), el borrado directo con `shutil.rmtree` es justificado. El `PermissionError` se captura y acumula igual que para los demás elementos.

**Límite arquitectural**: esta es la única excepción al patrón "solo `src/sync/` toca `~/.claude/`". Aplica únicamente al state dir y al tool dir (`~/.from-scratch/`), no a los archivos del catálogo (que se borran con `unlink`).

### 7. No se reutiliza `run_init` ni la diff engine

**Decisión**: `run_uninstall` lee el state directamente con `read_state` y usa `pathlib` para borrar. No pasa por `compute_diff` ni `copy_file`.

**Rationale**: el uninstall no necesita la lógica de diff — la lista canónica de qué borrar está en `installed_files`. Usar la diff engine añadiría complejidad sin beneficio.

### 8. Sin flag `--force`

**Decisión**: no hay `--force`. La confirmación interactiva es el único gate.

**Rationale**: no existe un escenario en el que sea necesario saltear la confirmación sin ser interactivo (scripts de CI no tendrían from-scratch instalado en primer lugar).

## Risks / Trade-offs

- **[Riesgo] Auto-borrado del tool** → el proceso Python borra su propio source mientras corre. En la práctica esto es seguro porque los módulos ya están cargados en memoria. El orden garantiza que el borrado de `~/.from-scratch/` ocurra al final, después de todo el trabajo.

- **[Riesgo] Interrupción a mitad del uninstall** → si el proceso muere entre el borrado de archivos del catálogo y el borrado del state, al re-ejecutar `uninstall` el state aún existe y lista archivos que ya no están en disco. Los `unlink(missing_ok=True)` manejan este caso sin error.

- **[Trade-off] No hay rollback** → el uninstall no hace backups. Es consistente con el diseño intencional ("quiero borrarlo todo"), pero significa que un `uninstall` accidental requiere un `init` posterior para restaurar.

---

## UX del comando

### Feedback durante el borrado

El borrado de archivos del catálogo es una operación síncrona y sub-segundo para catálogos de tamaño normal (decenas de archivos). No se muestra spinner ni contador durante el borrado. El feedback al usuario se concentra en dos momentos: la preview antes de confirmar y el mensaje de éxito al finalizar.

### Formato de la preview

Antes de pedir confirmación, el comando muestra:

```
Los siguientes elementos serán eliminados permanentemente:

  Archivos del catálogo (N):
    ~/.claude/commands/from-scratch/sync-skills.md
    ~/.claude/commands/from-scratch/...

  Directorios vacíos que se limpiarán:
    ~/.claude/commands/from-scratch/

  Estado de from-scratch:
    ~/.claude/from-scratch/  (directorio completo)

  Tool y wrapper:
    ~/.from-scratch/         (directorio completo)
    ~/.local/bin/from-scratch

¿Confirmar desinstalación? Esta acción no se puede deshacer. [s/N]
```

La confirmación es `s` / `S` para proceder, cualquier otra respuesta (incluyendo Enter vacío) cancela. El default es no confirmar.

### Mensajes de error accionables

Cada error que puede producir el comando debe responder: qué falló, por qué, y qué hacer.

| Situación | Mensaje | Remediación que se muestra |
|---|---|---|
| No se puede borrar un archivo (permisos) | "No se pudo eliminar `<ruta>`: permiso denegado" | `sudo rm <ruta>` |
| No se puede borrar el tool dir (permisos) | "No se pudo eliminar `~/.from-scratch/`: permiso denegado" | `sudo rm -rf ~/.from-scratch/` |
| No se puede borrar el wrapper (permisos) | "No se pudo eliminar `~/.local/bin/from-scratch`: permiso denegado" | `sudo rm ~/.local/bin/from-scratch` |

Los errores de permisos no abortan el proceso — el comando continúa borrando lo que puede, y lista al final los elementos que no pudo eliminar con sus remediaciones.

### Idempotencia y recuperación ante interrupción

Re-ejecutar `from-scratch uninstall` después de una interrupción es seguro: el state file sigue presente (si no se borró aún), los `unlink(missing_ok=True)` no fallan sobre archivos ya ausentes, y el resumen final refleja el estado real. El comando no deja archivos temporales ni estado corrupto.

### Cancelación con Ctrl+C

Si el usuario interrumpe con Ctrl+C durante el borrado (después de haber confirmado):

- Los archivos ya borrados no se restauran (no hay rollback, por diseño).
- El proceso termina con exit code 130 (convención SIGINT).
- El state file puede quedar en un estado parcial. Al re-ejecutar `uninstall`, el state sigue listando los archivos que restan y el comando procede normalmente.

No se usan archivos temporales durante el borrado, por lo que no puede quedar un `.tmp.*` huérfano.

### Output final

Tras borrado completo exitoso:

```
from-scratch desinstalado correctamente.
Para volver a instalarlo: from-scratch init
```

Tras cancelación:

```
Desinstalación cancelada.
```

Tras detectar que ya estaba desinstalado:

```
from-scratch no está instalado en este equipo.
Para instalarlo: from-scratch init
```

### Descripción en `--help`

El subcomando debe registrarse con la descripción:

```
uninstall   Desinstala from-scratch y elimina todos los archivos instalados
```
