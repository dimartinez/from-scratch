## ADDED Requirements

### Requirement: El repo de GitHub es la fuente de verdad del catálogo

El repositorio `dimartinez/from-scratch` SHALL ser la única fuente de verdad del catálogo. La copia local en `~/.claude/` SHALL ser un espejo de ese catálogo.

#### Scenario: Solo el repo decide qué hay en el catálogo

- **WHEN** el repo declara los archivos `commands/new-project.md` y `from-scratch/stacks/java.md`
- **THEN** una instalación limpia (`init`) coloca exactamente esos dos archivos en `~/.claude/`, ni más ni menos.

#### Scenario: Cambios solo se propagan vía init/update

- **WHEN** el autor agrega un nuevo archivo al repo
- **THEN** ese archivo aparece en la máquina del usuario solo después de ejecutar `from-scratch init` o `from-scratch update`.

### Requirement: Separación entre archivos de Claude Code y archivos internos

La CLI SHALL respetar dos zonas claramente separadas dentro de `~/.claude/`:

- Archivos consumidos directamente por Claude Code (slash commands, skills) van en sus carpetas estándar (`~/.claude/commands/`, `~/.claude/skills/`).
- Archivos internos de `from-scratch` (catálogo de stacks, metadata, configuración) van en `~/.claude/from-scratch/`.

#### Scenario: Un slash command se instala donde Claude Code lo busca

- **WHEN** el catálogo declara `commands/new-project.md`
- **THEN** la CLI lo coloca en `~/.claude/commands/new-project.md`.

#### Scenario: Un stack se instala en la zona interna

- **WHEN** el catálogo declara `stacks/java.md`
- **THEN** la CLI lo coloca en `~/.claude/from-scratch/stacks/java.md` y NO en `~/.claude/stacks/`.

### Requirement: Operación de sincronización idempotente

La operación de sincronización SHALL ser idempotente: ejecutar `from-scratch update` dos veces seguidas sin cambios remotos SHALL dejar el sistema en el mismo estado.

#### Scenario: Doble update sin cambios remotos

- **WHEN** el usuario corre `from-scratch update`, no hay cambios, y vuelve a correr `from-scratch update`
- **THEN** ambos comandos terminan exitosamente y no se modifica ningún archivo entre ejecuciones.

### Requirement: Diff claro antes de aplicar cambios

Antes de aplicar cambios sobre `~/.claude/`, la CLI SHALL mostrar un diff legible que indique qué archivos serán agregados, modificados o eliminados.

#### Scenario: Visualización de cambios pendientes

- **WHEN** hay cambios entre el repo y la copia local
- **THEN** la CLI imprime cada archivo afectado con un símbolo claro (`+` para agregado, `~` para modificado, `-` para eliminado) antes de pedir confirmación.

### Requirement: Sobreescritura de archivos del catálogo en v1

En esta versión, la CLI SHALL sobreescribir incondicionalmente los archivos del catálogo local con los del repo cuando hay cambios. No SHALL existir lógica de detección de modificaciones manuales del usuario sobre el catálogo en v1.

#### Scenario: Archivo modificado por el usuario es sobreescrito

- **WHEN** el usuario editó manualmente `~/.claude/from-scratch/stacks/java.md` y luego corre `from-scratch update`
- **THEN** la CLI sobreescribe el archivo con la versión del repo sin advertencia adicional, asumiendo el contrato documentado de que esos archivos no deben editarse a mano.

### Requirement: Funcionamiento offline tras `init`

Una vez completado `from-scratch init`, los comandos instalados SHALL operar sin requerir conexión a internet.

#### Scenario: Uso sin red tras instalación

- **WHEN** el usuario ya hizo `init` en una máquina conectada y luego pierde conectividad
- **THEN** los slash commands instalados (por ejemplo `/new-project`) siguen estando disponibles dentro de Claude Code, aunque las acciones que los comandos disparen puedan a su vez requerir red para clonar templates.
