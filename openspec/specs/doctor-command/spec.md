## ADDED Requirements

### Requirement: Invocación del comando doctor
El CLI SHALL exponer un subcomando `doctor` accesible via `from-scratch doctor`.

#### Scenario: Invocación básica sin flags
- **WHEN** el usuario ejecuta `from-scratch doctor`
- **THEN** el sistema imprime un reporte de salud en texto estructurado a stdout y termina con exit code según la severidad más alta encontrada

#### Scenario: Invocación con --json
- **WHEN** el usuario ejecuta `from-scratch doctor --json`
- **THEN** el sistema imprime un objeto JSON válido a stdout con todos los checks y termina con el mismo exit code que el modo texto

#### Scenario: Invocación con --markdown
- **WHEN** el usuario ejecuta `from-scratch doctor --markdown`
- **THEN** el sistema imprime el reporte en formato Markdown (tablas, headers) a stdout y termina con el mismo exit code que los otros modos

#### Scenario: Flag --help
- **WHEN** el usuario ejecuta `from-scratch doctor --help`
- **THEN** el sistema imprime la descripción del comando y sus flags disponibles

---

### Requirement: Formato Markdown del reporte
El doctor SHALL soportar un flag `--markdown` que produce output en Markdown válido, optimizado para renderizado en interfaces que soporten Markdown (Claude chat, GitHub issues).

#### Scenario: Estructura del reporte Markdown
- **WHEN** el doctor corre con `--markdown`
- **THEN** el output contiene un header H1 con timestamp, secciones H2 por categoría de checks, tablas markdown con columnas `Check`, `Estado`, `Detalle`, y una sección H2 `## Resumen` al final con el status global en negrita

#### Scenario: Checks con problemas en Markdown
- **WHEN** un check tiene status WARN o ERROR
- **THEN** la fila correspondiente en la tabla incluye la remediación en la columna `Detalle`

#### Scenario: Markdown válido en cualquier escenario
- **WHEN** el doctor encuentra cualquier combinación de estados
- **THEN** el output es Markdown bien formado (tablas con separadores correctos, sin caracteres especiales sin escapar)

---

### Requirement: Exit codes semánticos
El comando doctor SHALL terminar con exit codes que reflejen la severidad del diagnóstico, para uso programático por agentes y scripts.

#### Scenario: Instalación sin problemas
- **WHEN** todos los checks pasan sin advertencias ni errores
- **THEN** el proceso termina con exit code `0`

#### Scenario: Solo warnings presentes
- **WHEN** hay al menos un warning (ej. archivos .bak acumulados) y ningún error
- **THEN** el proceso termina con exit code `1`

#### Scenario: Al menos un error presente
- **WHEN** hay al menos un error (ej. archivo instalado faltante en disco)
- **THEN** el proceso termina con exit code `2`

---

### Requirement: Check del wrapper/binario
El doctor SHALL verificar que el binario `from-scratch` es localizable en el entorno del usuario.

#### Scenario: Binario encontrado en PATH
- **WHEN** `shutil.which("from-scratch")` retorna una ruta
- **THEN** el check reporta OK con la ruta encontrada

#### Scenario: Binario no encontrado en PATH
- **WHEN** `shutil.which("from-scratch")` retorna None
- **THEN** el check reporta WARN con una remediación que indica cómo reinstalar

---

### Requirement: Check del state file
El doctor SHALL verificar que `~/.claude/from-scratch/.state.json` existe, es parseable, y no indica una sync incompleta.

#### Scenario: State file válido y sync completa
- **WHEN** el state file existe, es JSON válido, y `has_incomplete_sync` es false
- **THEN** el check reporta OK con la fecha de última sync y cantidad de archivos registrados

#### Scenario: State file no existe
- **WHEN** el archivo no existe en la ruta esperada
- **THEN** el check reporta ERROR con remediación `from-scratch init`

#### Scenario: State file corrupto
- **WHEN** el archivo existe pero no es JSON válido o no es un dict
- **THEN** el check reporta ERROR con remediación `from-scratch init --force`

#### Scenario: Sync incompleta detectada
- **WHEN** `has_incomplete_sync` es true en el state
- **THEN** el check reporta WARN con remediación `from-scratch update`

---

### Requirement: Check de integridad de archivos instalados
El doctor SHALL verificar que cada archivo registrado en `installed_files` del state existe en disco y que su hash SHA256 coincide con el hash registrado.

#### Scenario: Todos los archivos presentes y sin modificar
- **WHEN** cada archivo en `installed_files` existe en disco y su SHA256 coincide con el hash registrado
- **THEN** el check reporta OK listando cada archivo con status `OK`

#### Scenario: Archivo faltante en disco
- **WHEN** un archivo registrado en `installed_files` no existe en `~/.claude/<path>`
- **THEN** el check reporta ERROR para ese archivo con remediación `from-scratch update`

#### Scenario: Archivo modificado por el usuario
- **WHEN** un archivo existe en disco pero su SHA256 difiere del hash registrado
- **THEN** el check reporta WARN para ese archivo indicando que fue modificado manualmente

---

### Requirement: Check de archivos .tmp huérfanos
El doctor SHALL detectar archivos con patrón `*.tmp.*` bajo `~/.claude/` que puedan indicar escrituras atómicas interrumpidas.

#### Scenario: Sin archivos .tmp huérfanos
- **WHEN** no hay archivos que coincidan con `**/*.tmp.*` bajo `~/.claude/`
- **THEN** el check reporta OK

#### Scenario: Archivos .tmp presentes
- **WHEN** existen uno o más archivos con patrón `*.tmp.*` bajo `~/.claude/`
- **THEN** el check reporta ERROR listando cada archivo y con remediación para eliminarlos manualmente

---

### Requirement: Check de acumulación de backups .bak
El doctor SHALL contar archivos con patrón `*.bak.*` bajo `~/.claude/` e informar si se acumularon.

#### Scenario: Sin archivos .bak
- **WHEN** no hay archivos que coincidan con `**/*.bak.*` bajo `~/.claude/`
- **THEN** el check reporta OK

#### Scenario: Archivos .bak presentes
- **WHEN** existen uno o más archivos `*.bak.*` bajo `~/.claude/`
- **THEN** el check reporta WARN con la cantidad total y la lista de archivos

---

### Requirement: Estructura del reporte en texto
El output en texto SHALL tener secciones claramente delimitadas legibles tanto por humanos como por agentes de IA.

#### Scenario: Formato de secciones
- **WHEN** el doctor corre en modo texto
- **THEN** el output incluye un header con timestamp, secciones entre corchetes (`[ESTADO]`, `[ARCHIVOS]`, `[RESIDUOS]`), y un bloque `=== RESUMEN ===` final con status global y lista de problemas con sus remediaciones

#### Scenario: Formato de cada item en secciones
- **WHEN** el doctor reporta un check individual
- **THEN** cada línea sigue el formato `<clave>: <valor> → <STATUS>` donde STATUS es uno de `OK`, `WARN`, `ERROR`

---

### Requirement: Log rotante de ejecuciones
El doctor SHALL escribir una entrada de log en `~/.claude/from-scratch/doctor.log` al finalizar cada ejecución exitosa, independientemente del formato de output elegido.

#### Scenario: Escritura de entrada de log
- **WHEN** el doctor completa un diagnóstico
- **THEN** agrega una línea JSON al final de `~/.claude/from-scratch/doctor.log` con campos `timestamp`, `status`, `error_count`, `warn_count`

#### Scenario: Rotación al superar 20 entradas
- **WHEN** el archivo de log ya tiene 20 o más entradas
- **THEN** el doctor conserva solo las últimas 19 antes de agregar la nueva, manteniendo el archivo en máximo 20 líneas

#### Scenario: Fallo de escritura del log
- **WHEN** el log no puede escribirse (directorio inexistente, `PermissionError`, disco lleno)
- **THEN** el doctor termina igualmente con el exit code correcto y no imprime ningún error a stdout ni stderr — la escritura del log es best-effort

#### Scenario: Escritura atómica del log
- **WHEN** el doctor escribe el log
- **THEN** usa escritura atómica (tmp + rename) para evitar corrupción ante interrupciones

---

### Requirement: Estructura del reporte en JSON
El output en JSON SHALL ser un objeto con campos predecibles para consumo programático.

#### Scenario: Estructura del objeto JSON
- **WHEN** el doctor corre con `--json`
- **THEN** el JSON contiene: `timestamp` (ISO 8601), `status` (`ok`/`warn`/`error`), `checks` (array de objetos con `name`, `status`, `detail`, `remediation`), y `summary` con `error_count` y `warn_count`

#### Scenario: JSON válido en cualquier escenario
- **WHEN** el doctor encuentra cualquier combinación de estados
- **THEN** el output es siempre JSON válido (no se mezcla con texto ni trazas de error)
