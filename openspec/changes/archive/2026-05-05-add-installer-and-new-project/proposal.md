## Why

Crear proyectos greenfield, sumar skills a proyectos existentes, y otras tareas repetitivas de "arranque" hoy se hacen a mano: cada vez que un desarrollador empieza algo nuevo, repite los mismos pasos de clonar un template, leer su README, ajustar configuración, etc. Queremos delegar ese trabajo a Claude Code, pero para hacerlo necesitamos antes una herramienta que distribuya — y mantenga actualizados — los comandos y skills que Claude Code va a usar para ejecutar esas tareas.

`from-scratch` es esa herramienta: una CLI mínima que instala en `~/.claude/` los comandos que después, dentro de Claude Code, hacen el trabajo de scaffolding. Esta primera versión entrega la CLI y un primer comando concreto (`/new-project`) que permite crear proyectos desde un template — empezando por un template de microservicio Java de Despegar.

## What Changes

- Se agrega una CLI `from-scratch` distribuida vía npm directamente desde el repo de GitHub (`npm i -g github:dimartinez/from-scratch`), sin registry pública.
- La CLI ofrece dos subcomandos:
  - `from-scratch init`: copia los archivos del catálogo del repo a `~/.claude/`.
  - `from-scratch update`: re-sincroniza el catálogo y reporta cambios al usuario.
- Se introduce el concepto de **catálogo**: un conjunto de archivos versionados en el repo que se replican en la máquina del usuario.
- Se introduce el concepto de **stack**: un archivo declarativo (nombre visible, descripción corta, URL de template) que representa una variante de proyecto que `/new-project` puede crear.
- Se entrega el primer stack: `java` (basado en `github.com/despegar/java-template`).
- Se entrega el primer comando de Claude Code instalado por la CLI: `/new-project`, que lista stacks disponibles, pregunta al usuario cuál usar, y delega en Claude la tarea de clonar el template y armar el proyecto siguiendo las instrucciones del README del template.
- Se establece un mecanismo de **handshake de versión** entre el catálogo y el binario: el catálogo declara la versión mínima de binario que requiere; si el binario está desactualizado, se planta y muestra un mensaje claro de cómo actualizarse.
- Se adoptan los formatos idiomáticos del ecosistema Claude Code: los slash commands del catálogo llevan **frontmatter YAML** con `description` (y opcionalmente `argument-hint`), tal como espera Claude Code; los archivos de stack también usan frontmatter YAML con los campos `name`, `description`, `template_url`. No se inventa un formato propio.
- Se establece la **distinción entre archivos propios y archivos del usuario**: la CLI registra en su state file los paths que instaló en zonas compartidas (`~/.claude/commands/`) y NO sobreescribe archivos preexistentes que no instaló ella misma; en caso de colisión de nombre, avisa y exige confirmación con `--force` (que hace backup antes de pisar).
- Se define un **manifest extensible por tipo de artefacto**: cada entrada del manifest declara su `kind` (`command`, `stack`, y a futuro `skill`, `agent`, `hook`), y el binario mapea cada kind a su zona de destino. Catálogos con kinds desconocidos disparan el handshake de versión, no fallas silenciosas.
- Se establece un **contrato de UX explícito** para la CLI (ver `design.md` → "UX de la CLI"): qué operaciones llevan spinner, qué se muestra antes de cada confirmación, formato de mensajes de error accionables (qué falló / por qué / qué hacer), garantías de idempotencia y de cancelación segura (Ctrl+C deja el catálogo consistente vía escritura atómica con `.tmp` + `rename`), formato de resumen final, y hints contextuales que enseñan el próximo paso (`--help`, subcomando inválido, post-`init`, post-`update`).

## Capabilities

### New Capabilities

- `installer-cli`: la herramienta de línea de comandos `from-scratch` con sus subcomandos `init` y `update`, su feedback visual moderno (Clack), y su validación de versión.
- `catalog-sync`: la mecánica de sincronización entre el repo (fuente de verdad) y la carpeta local `~/.claude/`, incluyendo el formato del catálogo, la separación entre archivos de Claude Code (`commands/`) y archivos internos (`from-scratch/`), y el manejo de cambios.
- `stack-system`: el formato y la organización de los stacks (cada stack como un archivo con nombre, descripción y URL de template).
- `new-project-command`: el comando `/new-project` instalado en Claude Code que orquesta la creación de un proyecto a partir de un stack elegido por el usuario, incluyendo el primer stack `java`.

### Modified Capabilities

(No aplica — primer change del proyecto.)

## Impact

- **Código nuevo**: estructura inicial del repo `dimartinez/from-scratch` con `package.json` configurado para ser instalable como CLI global desde GitHub.
- **Dependencias**: Node.js (runtime), TypeScript (lenguaje), `@clack/prompts` (UI de terminal).
- **Sistemas afectados**: el directorio `~/.claude/` del usuario gana nuevos archivos. Específicamente, archivos en `~/.claude/commands/` y un nuevo subdirectorio `~/.claude/from-scratch/`.
- **Workflow del usuario**: una vez instalado, el usuario adquiere un nuevo slash command (`/new-project`) en Claude Code que antes no existía.
- **No hay impacto en proyectos existentes** del usuario más allá del directorio `~/.claude/`. La herramienta no toca código de proyectos.
