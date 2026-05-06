### Requirement: Mostrar preview y pedir confirmación antes de borrar

El sistema SHALL listar todos los elementos que va a eliminar y pedir confirmación explícita al usuario antes de ejecutar cualquier operación de borrado.

#### Scenario: El usuario confirma el uninstall

- **WHEN** el usuario ejecuta `from-scratch uninstall` y responde afirmativamente
- **THEN** el sistema procede con el borrado completo

#### Scenario: El usuario cancela el uninstall

- **WHEN** el usuario ejecuta `from-scratch uninstall` y no confirma
- **THEN** el sistema cancela sin borrar nada y retorna exit code 2

---

### Requirement: Borrar todos los archivos del catálogo instalados

El sistema SHALL eliminar todos los archivos registrados en `installed_files` del state, sin verificar si fueron modificados por el usuario.

#### Scenario: Archivos presentes en disco

- **WHEN** se confirma el uninstall y un archivo de `installed_files` existe en `~/.claude/`
- **THEN** el sistema lo elimina del disco

#### Scenario: Archivos ausentes en disco

- **WHEN** se confirma el uninstall y un archivo de `installed_files` ya no existe en `~/.claude/`
- **THEN** el sistema lo omite sin error (missing_ok)

---

### Requirement: Limpiar directorios vacíos bajo `~/.claude/`

Tras borrar los archivos del catálogo, el sistema SHALL eliminar todo directorio que haya quedado vacío dentro de `~/.claude/`, recorriendo de hoja a raíz. El directorio `~/.claude/` en sí NUNCA debe ser borrado.

#### Scenario: Directorio queda vacío tras el uninstall

- **WHEN** después del borrado de archivos un directorio bajo `~/.claude/` no tiene contenido
- **THEN** el sistema elimina ese directorio

#### Scenario: Directorio tiene contenido ajeno a from-scratch

- **WHEN** después del borrado un directorio bajo `~/.claude/` aún contiene archivos no instalados por from-scratch
- **THEN** el sistema lo deja intacto

---

### Requirement: Eliminar el directorio de state

El sistema SHALL eliminar el directorio `~/.claude/from-scratch/` y todo su contenido (incluyendo `.state.json`).

#### Scenario: El directorio de state existe

- **WHEN** se confirma el uninstall y `~/.claude/from-scratch/` existe
- **THEN** el sistema elimina el directorio y su contenido completo

---

### Requirement: Eliminar el directorio del tool

El sistema SHALL eliminar el directorio `~/.from-scratch/` y todo su contenido.

#### Scenario: El directorio del tool existe

- **WHEN** se confirma el uninstall y `~/.from-scratch/` existe
- **THEN** el sistema elimina el directorio recursivamente

---

### Requirement: Eliminar el wrapper ejecutable

El sistema SHALL eliminar el archivo `~/.local/bin/from-scratch`.

#### Scenario: El wrapper existe

- **WHEN** se confirma el uninstall y `~/.local/bin/from-scratch` existe
- **THEN** el sistema elimina el wrapper

#### Scenario: El wrapper no existe

- **WHEN** se confirma el uninstall y `~/.local/bin/from-scratch` no existe
- **THEN** el sistema continúa sin error

---

### Requirement: Salida limpia si ya está desinstalado

Si no existe el state file, el sistema SHALL mostrar un mensaje informativo y salir con exit code 0 sin intentar borrar nada.

#### Scenario: No hay state file

- **WHEN** el usuario ejecuta `from-scratch uninstall` y `~/.claude/from-scratch/.state.json` no existe
- **THEN** el sistema muestra que ya está desinstalado y retorna exit code 0

---

### Requirement: Informar resultado al usuario

Al finalizar el borrado completo, el sistema SHALL mostrar un mensaje de éxito en español.

#### Scenario: Uninstall completado

- **WHEN** todos los elementos han sido eliminados exitosamente
- **THEN** el sistema imprime un mensaje de confirmación y retorna exit code 0
