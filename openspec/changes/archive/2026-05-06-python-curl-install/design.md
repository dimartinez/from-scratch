## Context

`from-scratch` es una CLI de ~1300 LOC TypeScript que copia archivos de un catálogo (en GitHub) a `~/.claude/`. La distribución actual vía `npm i -g github:dimartinez/from-scratch` está rota en su único entorno objetivo: las laptops corporativas de Despegar tienen un AV que borra todo archivo con extensión `.js`, dejando huérfanos los `.d.ts` después del install. El problema NO es npm, NO es la conectividad, NO es la firma — es el match por extensión de archivo.

La herramienta es plomería: `init`/`update` descargan un manifest JSON, leen archivos del catálogo, los copian al filesystem del usuario con detección de conflictos y backup. No abre sockets persistentes, no tiene cómputo pesado, no depende de capacidades exclusivas de Node. Cualquier lenguaje de scripting con HTTP, JSON y filesystem la cubre.

Audiencia: ~400 devs internos de Despegar. Manejan sus propias laptops y saben lo que hacen — el constraint de seguridad/MDM solo aplica al borrado de `.js`, no al instalar runtimes o agregar paths.

Una sesión de exploración previa cerró tres decisiones (registradas abajo): el modelo `curl | bash` + clone-and-run, Python como lenguaje, y un update flow donde `from-scratch update` pullea el repo antes de sincronizar.

## Goals / Non-Goals

**Goals:**
- Distribución que sobrevive al AV: ningún archivo `.js` queda en disco después del install, en ningún momento del ciclo.
- Un solo comando para instalar (`curl ... | bash`), un solo comando para actualizar (`from-scratch update`).
- Cero dependencias en runtime (más allá de `python3`, `git` y `bash` que son universales en Macs de devs).
- Preservar el contrato externo de la herramienta: misma UX de `init`/`update`/`--help`/`--force`, mismo formato de catálogo, misma estructura de `~/.claude/`, mismo state file.
- Reducir overhead operacional del repo: sin `dist/` committeado, sin transpile step, sin pre-commit hook que builda.

**Non-Goals:**
- Soportar Windows. La audiencia es Mac/Linux corporativos; el AV específico es de Despegar; el alcance se mantiene en POSIX.
- Publicar al PyPI. La distribución sigue siendo el repo de GitHub.
- Empaquetar como binario único (PyInstaller, Nuitka, Go rewrite). Discutido y descartado en exploración: binarios sin firmar tienden a disparar EDR corporativo más que scripts; agregar notarización Apple es overhead por un beneficio marginal.
- Reescribir el formato del catálogo. El catálogo es contrato con humanos que escriben stacks/commands; cambiarlo es un eje ortogonal.
- Migrar `~/.claude/from-scratch/.state.json`. El formato se preserva tal cual.

## Decisions

### Decisión 1: Lenguaje del rewrite — Python 3 con stdlib

**Elegido:** Python 3 sin dependencias externas (`pip install` prohibido).

**Alternativas consideradas:**
- *Bash puro*: descartado. La CLI tiene flujos suficientemente ramificados (handshake → diff → confirmación → backup → state update, con resume de sync incompleto) que en bash se vuelven frágiles. Además requiere `jq` para JSON (dependencia adicional, no garantizada en una laptop corporate).
- *Go/Rust binario único*: descartado. Un binario desconocido y sin firmar es generalmente *más* sospechoso para un EDR corporativo que un script. Notarización Apple ($99/año + ceremonia) agrega overhead por un beneficio marginal sobre Python.
- *Deno o Bun ejecutando TypeScript*: descartado. Re-introduce la incertidumbre del runtime corporativo y los `.ts` que importen otros archivos pueden generar `.js` cacheados.

**Por qué Python:**
- Viene preinstalado en macOS (las laptops de Despegar son Macs de devs).
- Stdlib cubre todo lo necesario: `urllib.request` (HTTP, aunque casi no se usa porque `git pull` reemplaza fetch), `subprocess` (para git), `json`, `argparse`, `pathlib`, `shutil`, `difflib`, `hashlib`, `tempfile`.
- Los `.py` no caen en el match del AV.
- Lectura cómoda para devs senior que no son Pythonistas full-time — la sintaxis es lo bastante predecible.

### Decisión 2: Cero dependencias externas, incluido YAML

**Elegido:** Todo el código (incluido el parser de YAML frontmatter) usa solo stdlib. No hay `requirements.txt` ni venv.

**Por qué:**
- `pip install` introduce los mismos vectores de fricción que estamos esquivando con npm: proxies, cache local, archivos `.py` cacheados que el AV podría tocar (no es el caso hoy, pero el principio es no agregar superficie nueva).
- Hace `install.sh` trivialmente robusto: si `python3` y `git` están, todo funciona; no hay estado adicional que validar.
- El YAML usado es del subset más simple imaginable (`key: value` planos en frontmatter, sin nesting, sin listas, sin types). Un parser casero de ~20 líneas (split por línea, split por primer `:`, strip de comillas) es suficiente y deterministic.

**Trade-off aceptado:** un parser YAML casero es más frágil que PyYAML si alguien escribe frontmatter con listas o nested objects. Lo manejamos por contrato: la spec del catálogo ya restringe el frontmatter al subset plano. Cualquier intento de usar YAML más complejo falla con error claro.

### Decisión 2.1: Forward-compat del manifest — kinds desconocidos se ignoran con warning

**Elegido:** Cuando el parser de `catalog.json` encuentra una entrada con un `kind` que no reconoce (futuros `agent`, `skill`, `hook`, etc.), la entrada se ignora con un `WARN` a stderr ("Ignoré entrada con kind desconocido `<kind>` en `catalog.json`. Probablemente tu CLI está desactualizada; corré `from-scratch update`."). El sync continúa con las entradas restantes.

**Por qué no fallar duro:**
- Eliminamos `requires_binary` apostando a que código y catálogo viajan juntos. Pero el modelo de evolución del catálogo importa igual: si un PR agrega un kind nuevo y modifica el código del parser en el mismo commit, todo OK; si por alguna razón un usuario corre `from-scratch update` con una working copy que tiene catálogo nuevo y código viejo (e.g., revirtieron `src/` localmente), no queremos romper el sync de los kinds que sí entiende.
- Permite agregar kinds nuevos sin spec change ceremoniosa cada vez. La capability `installer-cli` declara que kinds desconocidos se ignoran; los kinds soportados se documentan en el README.

**Trade-off:** un typo en el `kind` (e.g., `comand` en vez de `command`) se ignora silenciosamente con warning en lugar de fallar. Aceptable: el warning es visible, el catálogo se versiona en git y review humano lo cazaría antes de merge.

### Decisión 3: Update flow α — `from-scratch update` hace `git pull` primero

**Elegido:** `from-scratch update` ejecuta `git pull --ff-only` en `~/.from-scratch/`, después sincroniza `~/.claude/`. Un solo comando actualiza código y catálogo.

**Alternativas consideradas:**
- *β: separar* — `curl | bash` actualiza código, `from-scratch update` solo sincroniza catálogo. Más explícito pero impone dos comandos para "estar al día"; la herramienta es plomería, los usuarios no quieren pensar en eso.
- *γ: chequear y avisar* — `update` informa que hay commits nuevos pero no pullea solo. Híbrido conservador, agrega un paso manual sin agregar control real.

**Por qué α:**
- Mental model "un comando para estar al día" es la más simple posible.
- Como el catálogo y el código viven en el mismo repo, un `git pull --ff-only` es atómico — si rompe algo, hay un commit exacto al cual culpar y al cual hacer revert.
- `--ff-only` impide merge weirdo si alguien por error hace cambios locales en `~/.from-scratch/`. En ese caso, `update` falla con mensaje claro y el usuario decide.
- Si en el futuro aparece un caso de "querer pinear el código mientras se actualiza el catálogo", se agrega un flag (`--no-self-update`) — pero no se construye preventivamente.

**Detalle subtle:** después del `git pull`, el código `cli.py` ya cargado en memoria es la versión vieja. Para esta corrida, sigue siendo el comportamiento viejo. Lo aceptamos: el sync que se ejecuta a continuación lleva el catálogo nuevo, y la próxima invocación ya usa el código nuevo. Para evitar confusión, si `git pull` trajo cambios en `src/`, el comando lo informa al final ("Se actualizó el código de la CLI; la próxima ejecución usará la versión nueva").

### Decisión 4: Wrapper bash de 3 líneas, no symlink

**Elegido:**

```bash
#!/usr/bin/env bash
exec python3 "$HOME/.from-scratch/src/cli.py" "$@"
```

en `~/.local/bin/from-scratch` con `chmod +x`.

**Alternativas consideradas:**
- *Symlink directo a `cli.py`* con shebang `#!/usr/bin/env python3`: más elegante, menos archivos, aprovecha que Python pone `sys.path[0]` en el directorio del script resuelto. Frágil ante reorganización: si renombramos `cli.py` o lo movemos, el symlink se rompe silenciosamente.
- *Función shell exportada en `.zshrc`/`.bashrc`*: invasivo, modifica archivos del usuario, requiere reload de shell.

**Por qué wrapper bash:**
- El usuario que abra `~/.local/bin/from-scratch` curioso ve exactamente qué hace: 3 líneas obvias.
- Tolera reorganización interna del repo (el wrapper apunta a un path estable; cambios dentro de `src/` no afectan al wrapper).
- Es lo que herramientas como pyenv hacen.

### Decisión 5: Migración desde npm — detectar y avisar, no auto-ejecutar

**Elegido:** `install.sh` ejecuta `npm root -g 2>/dev/null` y, si la salida contiene un directorio `from-scratch`, imprime:

```
Detecté una instalación previa de from-scratch vía npm.
Antes de continuar, ejecutá:

    npm uninstall -g from-scratch

Después volvé a correr este install.
```

Y sale con código no-cero.

**Alternativas consideradas:**
- *Auto-ejecutar `npm uninstall -g from-scratch`*: descartado. Un script bash bajado por curl ejecutando comandos npm con privilegios sobre el global node_modules es exactamente la clase de cosa que dispara alarmas de seguridad — y razonablemente. La fricción de un comando manual es aceptable.
- *Ignorar la versión vieja y simplemente sobreescribir el wrapper*: descartado. Deja el binario npm-managed huérfano en `$(npm bin -g)`, y el `from-scratch` que el usuario ejecute depende del orden del PATH; comportamiento indeterminista.

### Decisión 6: UX de la CLI — patrones consistentes y seguros

**Elegido:** Un conjunto de patrones de UX que se aplican uniformemente en todos los subcomandos, derivados de las heurísticas que ya usaba la versión TS pero ahora documentados explícitamente porque el rewrite es la oportunidad para hacerlos contrato.

**Feedback durante operaciones lentas.** Cualquier operación que pueda exceder ~1 segundo muestra un indicador textual con un mensaje descriptivo. Las operaciones que llevan feedback son: (a) `git clone` y `git pull` durante `install.sh` y `update`, (b) la lectura/parseo del manifest del catálogo cuando hay muchos archivos, (c) la fase de copia/backup al sincronizar `~/.claude/`. El indicador es un spinner simple basado en stdlib (`threading` + carácter rotando o, en TTYs no interactivas, una línea de log por paso) — no usa caracteres Unicode exóticos para no romper en terminales corporativas.

**Confirmaciones antes de modificar disco.** La regla: nunca tocar `~/.claude/` sin que el usuario haya visto antes la lista exacta de archivos que se van a tocar. Antes de cualquier prompt de confirmación, la CLI imprime un *preview* con: (a) cantidad de archivos por categoría (`+ N nuevos`, `~ N modificados`, `= N sin cambios`, y cuando aplique `! N en conflicto`), (b) la lista completa con el prefijo correspondiente y el path destino, (c) si va a crear backups, los paths exactos de los `.bak.<timestamp>`. El prompt es un sí/no explícito (default `n`). Aplica a: `init` (en directorio limpio igualmente, para que el usuario vea qué se va a instalar), `init --force` (con énfasis en los archivos que serán pisados), `update` (incluso cuando solo hay archivos modificados). `install.sh` no pide confirmación porque el efecto está acotado a `~/.from-scratch/` y `~/.local/bin/from-scratch` y se imprime exactamente qué se creó.

**Errores accionables.** Cada excepción que la CLI propaga al usuario incluye tres piezas: *qué falló* (una línea descriptiva), *por qué* (causa subyacente cuando es no-obvia), y *qué hacer ahora* (un comando concreto o paso). Mapeo concreto:
- `NetworkError` (al ejecutar `git pull` o `git clone`): "No pude contactar GitHub. Verificá tu conectividad o el proxy. Reintentá con: `from-scratch update`".
- `GitFastForwardError`: "Tu clone en `~/.from-scratch` tiene cambios locales. Revisalos con: `cd ~/.from-scratch && git status`. Para descartarlos y volver al estado limpio: `cd ~/.from-scratch && git reset --hard origin/main`".
- `ManifestParseError`: "El catálogo (`catalog/catalog.json`) no parsea. Línea `<N>`: `<razón>`. Reportá el commit en `#from-scratch-help` si es responsabilidad del catálogo, o re-cloná con: `rm -rf ~/.from-scratch && curl -fsSL ...`".
- `StateCorruptError`: "El archivo de estado `~/.claude/from-scratch/.state.json` está corrupto. Para regenerarlo desde cero perdiendo el tracking previo: `rm ~/.claude/from-scratch/.state.json && from-scratch init`".
- `FileNotFoundError` en catálogo: "Falta el archivo `<path>` referenciado por `catalog.json`. Si acabás de hacer `update`, intentá: `from-scratch update` de nuevo; si persiste, re-cloná con `rm -rf ~/.from-scratch && curl -fsSL ...`".
- `python3 < 3.8` o `python3` ausente desde `install.sh`: "Necesito Python 3.8+. Instalalo con: `brew install python@3.12`".
- `git` ausente desde `install.sh`: "Necesito `git`. Instalalo con: `xcode-select --install` (Mac) o tu package manager".

Los errores van a stderr; los mensajes informativos a stdout. Exit codes: `0` éxito, `1` error de validación o de runtime, `2` cancelación por usuario (Ctrl+C o `n` a confirmación), `3` precondición faltante (binarios, versión).

**Idempotencia y recuperación.** Garantía explícita: ejecutar `install.sh` o `from-scratch <cmd>` dos veces seguidas con el mismo input deja el sistema en el mismo estado, sin duplicar archivos ni romper. Mecánica:
- `install.sh` detecta `~/.from-scratch/` existente y hace `git pull` en lugar de clonar de nuevo. Detecta `~/.local/bin/from-scratch` existente y lo re-escribe (idempotente).
- `init` consulta el state file; si existe y refleja una instalación completa, informa "ya inicializado, usá `from-scratch update` para sincronizar" y sale sin tocar nada.
- `init` consulta el state file; si refleja un sync incompleto (`hasIncompleteSync == true`), informa "detecté una instalación incompleta de la corrida previa", muestra qué archivos faltaban y ofrece reanudar.
- `update` re-ejecutado sin cambios remotos imprime "todo al día" y sale 0.

**Cancelación segura (Ctrl+C).** Garantía: en cualquier momento del flujo, una interrupción deja el sistema en estado consistente. Implementación:
- Toda escritura a un path destino se hace primero a un archivo temporal en el mismo directorio (`<destino>.tmp.<pid>`) y se mueve con `os.rename` (atómico en POSIX) al final. Si el proceso muere antes del rename, el destino queda intacto.
- El backup `.bak.<timestamp>` se crea ANTES de la escritura del nuevo contenido. Si la escritura falla o se interrumpe, el `.bak` permanece y permite recuperación manual.
- El state file se escribe con la misma técnica (temp + rename); nunca queda truncado a la mitad.
- Un `signal handler` para SIGINT imprime "Cancelado por el usuario." en stderr, sale con exit code 2, y deja archivos `.tmp.*` huérfanos que la próxima invocación limpia.
- Cualquier escritura en curso al momento de Ctrl+C se aborta antes del rename atómico; el destino queda como estaba.

**Output consistente.** Patrones canónicos:
- Líneas informativas: prefijo `→` (flecha simple ASCII no, usar `->` o ninguno; spec elige `->` para mantener portabilidad).
- Éxito: prefijo `OK` y mensaje breve.
- Advertencia: prefijo `WARN` a stderr.
- Error: prefijo `ERROR` a stderr, seguido por línea de "qué hacer ahora".
- Diff de archivos: `+ path` (nuevo), `~ path` (modificado), `= path` (sin cambios), `! path` (conflicto).
- Resumen final: bloque de una línea por categoría con conteos, seguido por una línea de "próximo paso" cuando aplica.
- Sin emojis, sin colores forzados (la stdlib de Python no incluye un módulo robusto y los terminales corporativos varían). Se respeta `NO_COLOR` por convención si en el futuro se agregan colores.

**Discoverability.** La CLI enseña el siguiente paso al usuario en momentos clave:
- Final de `install.sh`: "Listo. Probá `from-scratch init` para instalar el catálogo en `~/.claude/`".
- Final de `init` exitoso: "Listo. Cuando quieras sincronizar con cambios del catálogo: `from-scratch update`".
- `init` invocado en directorio ya inicializado: "Ya está inicializado. Para sincronizar usá: `from-scratch update`. Para reinstalar pisando todo: `from-scratch init --force`".
- `update` cuando no hay cambios: "Todo al día. (Última sincronización: <fecha del state file>)".
- `from-scratch` sin args muestra `--help`. `from-scratch <subcomando-invalido>` sugiere el más cercano (`Levenshtein` casero a partir de los subcomandos válidos) y muestra la lista.
- `--help` global lista los subcomandos con una línea de descripción cada uno y un ejemplo. `--help` por subcomando incluye qué archivos toca, qué confirmaciones pide y qué exit codes devuelve.

**Por qué documentarlo en design en lugar de dejarlo a "buen criterio":** la versión TS tenía estos comportamientos parcialmente — el rewrite es la oportunidad de hacerlos contrato chequeable. Sin esto, el rewrite Python podría perder calidad de UX silenciosamente.

### Decisión 6.1: Co-existencia con el resto de `~/.claude/`

**Elegido:** La CLI declara explícitamente que `~/.claude/` es un directorio compartido — Claude Code mismo lo usa, otros instaladores pueden usarlo, el usuario crea archivos a mano. `from-scratch` solo toca lo que está registrado en `~/.claude/from-scratch/.state.json`. Cualquier archivo fuera de ese tracking se considera "no nuestro" y es intocable.

**Reglas concretas:**

1. **Archivos rastreados (presentes en el state file):** la CLI los compara con el contenido del catálogo para decidir si los actualiza. Antes de pisar uno, verifica si el contenido en disco coincide con lo que ella misma instaló en la corrida anterior (hash registrado en el state file). Si NO coincide, lo trata como "modificado por el usuario": muestra el diff en el preview con prefijo `! path (modificado localmente)` y NO pisa sin `--force`. Con `--force`, hace backup `.bak.<timestamp>` igual.

2. **Archivos no rastreados con el mismo path que un archivo del catálogo:** caso típico, el usuario tenía un `~/.claude/commands/new-project.md` propio antes de correr `init`. La CLI los detecta como conflicto, los lista con prefijo `! path (no instalado por from-scratch)` en el preview, y NO pisa sin `--force`. Con `--force`, hace backup y pisa, pero queda registrado como "instalado por nosotros" desde ahí.

3. **Archivos en `~/.claude/from-scratch/` no rastreados:** si el usuario o un proceso externo creó archivos dentro de `~/.claude/from-scratch/` que no son parte del catálogo (ej. un `stacks/local-experiment.md` propio), la CLI los deja intactos. `update` nunca elimina archivos que no haya instalado ella misma; "limpiar archivos que ya no están en el catálogo" se hace solo sobre los que están registrados en el state file.

4. **Archivos en otros subdirectorios de `~/.claude/` (`~/.claude/agents/`, `~/.claude/skills/`, `~/.claude/settings.json`, etc.):** intocables. La CLI nunca lee ni escribe fuera de los paths declarados en el catálogo.

**Por qué este nivel de detalle:** la audiencia tiene 400 devs; muchos van a tener configuración personalizada en `~/.claude/`. La regla "solo tocamos lo nuestro, identificado por el state file" tiene que ser contrato chequeable, no aspiración. Sin esto, un bug en `update` puede borrar trabajo del usuario silenciosamente y la confianza en la herramienta se erosiona.

### Decisión 6.2: Cancelación durante subprocess `git`

**Elegido:** Cuando la CLI invoca `git clone` / `git pull --ff-only` mediante `subprocess.run`, el handler de SIGINT del proceso padre Python deja que la señal se propague al hijo (comportamiento default cuando no se aísla con `start_new_session`). El hijo `git` termina de manera ordenada, `subprocess.run` propaga `KeyboardInterrupt`, y el handler general del CLI lo convierte en exit code 2 ("Cancelado por el usuario.").

**Por qué importa documentarlo:** sin tomar una decisión explícita, el comportamiento depende de detalles sutiles (`preexec_fn`, grupos de proceso). El default de `subprocess.run` sin `start_new_session=True` en POSIX hace que SIGINT del terminal alcance al hijo automáticamente — eso es lo que queremos. El test correspondiente verifica que cancelar durante `git pull` deja el clone en estado consistente (git mismo es atómico a nivel commit; o pulleó completo o no pulleó).

### Decisión 7: Test runner — pytest, opcional venv solo para dev

**Elegido:** `pytest` para tests (no stdlib `unittest`).

**Alternativas consideradas:**
- *stdlib `unittest`*: mantiene la regla "cero deps externas" incluso para development. Pero `unittest` tiene API más verbosa (clases, `self.assertEqual`), peor descubrimiento de tests, y output menos legible.
- *No tests en el rewrite, copiar manual de los actuales*: descartado, regresión en disciplina; los tests actuales son buena base.

**Por qué pytest:**
- La regla de cero deps aplica al **runtime del usuario final**. Para development, los devs ya manejan venvs y pytest está universalmente conocido.
- pytest es estándar de la industria. Permite assertions con `assert` puro y output bonito.
- Setup mínimo: un `pytest.ini` o `pyproject.toml` con un par de líneas, y un README explicando `python3 -m venv .venv && pip install pytest`.

**Trade-off:** introduce una dep de dev. Es pago aceptable a cambio de DX significativamente mejor para los tests.

## Risks / Trade-offs

- **[Riesgo]** `python3` no apunta a Python 3 en alguna laptop, o apunta a una versión muy vieja (3.6 o anterior).
  → **Mitigación:** `install.sh` ejecuta `python3 --version` y verifica >= 3.8 (que tiene todo lo que usamos: `dataclasses`, `pathlib`, f-strings, `typing` moderno). Si falla, imprime instrucciones claras: "Instalá Python 3.8+, e.g. con `brew install python@3.12`".

- **[Riesgo]** Mini-parser de YAML rompe ante frontmatter ligeramente fuera del subset previsto (alguien escribe `description: "foo: bar"` con `:` en el valor, o usa nested keys).
  → **Mitigación:** parser falla rápido con mensaje específico (`"YAML frontmatter inválido en <archivo>: línea N: <razón>"`). Tests cubren edge cases comunes (comillas dobles/simples, `:` en valores, espacios, líneas vacías). El contrato del catálogo (documentado en README) restringe el formato.

- **[Riesgo]** El comportamiento de "código viejo en memoria + catálogo nuevo en disco" después de `git pull` confunde al usuario.
  → **Mitigación:** detectar si `git pull` cambió archivos en `src/` (parsear su salida) y, al final del comando, imprimir el aviso explícito. Documentar este detalle en el `--help` de `update`.

- **[Riesgo]** Usuario instala el nuevo `install.sh` SIN haber desinstalado la versión npm primero, ignorando la advertencia, y queda con dos `from-scratch` en PATH.
  → **Mitigación:** `install.sh` falla con exit code 1 y NO escribe nada cuando detecta la versión npm. El usuario tiene que actuar deliberadamente. No hay path en el cual ambos coexistan accidentalmente.

- **[Riesgo]** `git pull --ff-only` falla porque el usuario tocó archivos del clone (e.g., editó `~/.from-scratch/catalog/...` para probar algo).
  → **Mitigación:** capturar el error específico de git, mostrar mensaje "tu clone de ~/.from-scratch tiene cambios locales — hacé `git status` ahí o re-cloná" y salir sin tocar `~/.claude/`. No intentamos auto-resolver.

- **[Trade-off]** El primer `from-scratch update` después del rewrite, para alguien que tenía la versión npm, requiere acción manual: `npm uninstall` + `curl | bash`. Es un paso de fricción, pero one-shot.

- **[Riesgo]** Usuario edita a mano un archivo que la CLI instaló (ej. agrega instrucciones propias a `~/.claude/commands/new-project.md`). En el próximo `update` con cambios remotos, esa edición se pisa sin que el usuario lo perciba.
  → **Mitigación:** el state file guarda el hash del contenido instalado. Antes de pisar, la CLI compara el hash en disco contra el hash registrado; si difiere, el preview marca el archivo como `! path (modificado localmente)` y no procede sin `--force`. Con `--force`, hace backup `.bak.<timestamp>` igual. Documentado en design.md decisión 6.1.

- **[Riesgo]** Catálogo evoluciona y agrega un kind nuevo (ej. `agent`, `skill`, `hook`) en un commit que cambia tanto `catalog.json` como `src/`. Si el usuario hace `git pull` y por alguna razón el código no se actualiza con el catálogo (working copy con mods locales en `src/`, fast-forward parcial extraño, etc.), la CLI vieja encuentra un kind que no entiende.
  → **Mitigación:** el parser de manifest ignora kinds desconocidos con `WARN` en stderr y continúa con el resto. Documentado en design.md decisión 2.1. Tests cubren el caso.

## Migration Plan

1. Implementar el rewrite en una rama, manteniendo verde toda la suite.
2. Tras merge, publicar un tag y actualizar README con el nuevo comando `curl | bash`.
3. Comunicación interna en Despegar: anunciar el cambio, vincular al README. La versión npm sigue funcionando para quien todavía no migró (porque el código viejo no se borra del repo, solo deja de ser el path principal — pero esto importa solo si el código viejo SIGUE funcionando para alguien fuera de Despegar; dentro de Despegar, ya está roto).
4. Instalaciones nuevas: `curl ... | bash`. Instalaciones existentes: `npm uninstall -g from-scratch` + `curl ... | bash`.
5. **Rollback**: si el rewrite tiene un bug crítico post-deploy, los usuarios pueden volver al commit anterior con `cd ~/.from-scratch && git checkout <sha-pre-rewrite>`. Como el código vive en el clone del usuario, cada uno tiene su escape hatch sin necesidad de re-publish. (Nota: el rollback los devuelve al código TS, que en Despegar está roto por el AV; rollback solo es viable fuera de Despegar.)
6. Después de un período razonable (e.g., 2 semanas sin incidentes), eliminar `dist/` y los archivos TS del repo en un commit separado. Hasta entonces se mantienen para facilitar comparación y rollback.

## Open Questions

- ¿Hay devs de Despegar que usan from-scratch en Linux (no Mac)? Si sí, validar que `python3` esté disponible por defecto en sus distros (Ubuntu/Debian sí, distros minimalistas potencialmente no). Por ahora se asume Mac.
- ¿Necesitamos versionar `install.sh` o que viva siempre en `main`? Al ser stdlib y triv ial, vivir en `main` es suficiente; si en el futuro el script crece, podemos pinear con un tag en la URL.
