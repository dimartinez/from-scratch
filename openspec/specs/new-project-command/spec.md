## ADDED Requirements

### Requirement: El comando `/new-project` se instala globalmente en Claude Code

Tras ejecutar `from-scratch init`, el archivo `~/.claude/commands/new-project.md` SHALL existir y, tras un reinicio de Claude Code, el slash command `/new-project` SHALL estar disponible en cualquier proyecto.

#### Scenario: Disponibilidad tras init y reinicio

- **WHEN** el usuario ejecuta `from-scratch init` exitosamente y reinicia Claude Code
- **THEN** al tipear `/` dentro de Claude Code aparece `/new-project` en la lista de comandos disponibles.

### Requirement: El comando es un prompt, no un script

El archivo `commands/new-project.md` SHALL ser un documento markdown en lenguaje natural que define un **rol** y un **objetivo** para Claude, no una secuencia imperativa de pasos.

#### Scenario: Estructura del comando

- **WHEN** se inspecciona el contenido del archivo `~/.claude/commands/new-project.md`
- **THEN** el archivo describe en lenguaje natural el rol que Claude debe adoptar (desarrollador senior preparando ambiente), las acciones esperadas (listar stacks, preguntar al usuario, clonar el template, leer README, ejecutar setup), y el resultado esperado (proyecto listo para usar), sin contener código ejecutable.

### Requirement: Listado de stacks disponibles desde el catálogo local

Al invocarse, `/new-project` SHALL leer los stacks instalados en `~/.claude/from-scratch/stacks/` y SHALL presentarlos al usuario como una lista interactiva.

#### Scenario: Lista visible al invocar el comando

- **WHEN** el usuario ejecuta `/new-project` y existen los stacks `java.md` (y eventualmente otros) en `~/.claude/from-scratch/stacks/`
- **THEN** Claude muestra una lista con cada stack representado por su nombre visible y descripción corta, y le pide al usuario elegir uno.

#### Scenario: No hay stacks disponibles

- **WHEN** el usuario ejecuta `/new-project` y la carpeta `~/.claude/from-scratch/stacks/` está vacía o no existe
- **THEN** Claude informa al usuario que no hay stacks instalados y sugiere ejecutar `from-scratch init` o `from-scratch update`.

### Requirement: Recolección de inputs mínimos al usuario

Antes de comenzar el scaffolding, `/new-project` SHALL recolectar al menos:

- El stack elegido por el usuario.
- El nombre del proyecto.

Otros inputs (configuraciones específicas del template) SHALL ser solicitados por Claude solo si el README del template los requiere.

#### Scenario: Pregunta por stack y nombre

- **WHEN** el usuario invoca `/new-project`
- **THEN** Claude pregunta primero qué stack usar y luego el nombre del proyecto, antes de iniciar cualquier acción sobre el sistema de archivos.

### Requirement: Delegación con rol de desarrollador senior

Una vez recolectados los inputs, `/new-project` SHALL instruir a Claude a actuar como un desarrollador senior que prepara el ambiente, no como un ejecutor mecánico de pasos. Claude SHALL clonar el template indicado por el stack, leer su README, y armar el proyecto siguiendo esas instrucciones, validando coherencia con el código.

#### Scenario: Setup exitoso con README claro

- **WHEN** Claude clona el template Java, lee su README, y todas las instrucciones son claras y aplicables
- **THEN** Claude ejecuta los pasos necesarios y reporta al usuario un proyecto listo para usar, indicando los siguientes pasos sugeridos.

#### Scenario: Ambigüedad o conflicto en el README

- **WHEN** Claude detecta una ambigüedad, una inconsistencia entre el README y el código del template, o un paso que requiere información del usuario
- **THEN** Claude pausa la ejecución, le explica al usuario qué encontró, y pide aclaración antes de continuar.

### Requirement: Reporte final al usuario

Al terminar exitosamente, `/new-project` SHALL reportar al usuario qué hizo y cómo continuar.

#### Scenario: Resumen de cierre

- **WHEN** la creación del proyecto termina sin errores
- **THEN** Claude muestra un resumen breve que incluye la ruta del proyecto creado, las acciones principales que realizó, y al menos una sugerencia clara de qué hacer a continuación (por ejemplo, "abrí el proyecto y corré los tests").
