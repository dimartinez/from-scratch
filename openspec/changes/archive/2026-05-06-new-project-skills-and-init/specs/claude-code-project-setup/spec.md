## ADDED Requirements

### Requirement: Se crea o se mergea .claude/settings.json con permisos base

Durante la creación del proyecto, Claude SHALL escribir `.claude/settings.json` con un conjunto de permisos base que evitan prompts de confirmación innecesarios para operaciones comunes. Si el template ya incluye un `settings.json`, Claude SHALL hacer merge JSON: agrega los permisos del catálogo y preserva los del template.

#### Scenario: Proyecto sin settings.json previo

- **WHEN** el template clonado no incluye `.claude/settings.json`
- **THEN** Claude crea `.claude/settings.json` con permisos base para el stack elegido (ej. comandos de build, test, y git).

#### Scenario: Template ya incluye settings.json sin conflictos

- **WHEN** el template clonado ya incluye `.claude/settings.json` y no hay keys con valores distintos a los del catálogo
- **THEN** Claude hace merge JSON sin pedir confirmación: las keys nuevas del catálogo se agregan, las del template se preservan.

#### Scenario: Conflicto real en settings.json

- **WHEN** el template ya incluye `.claude/settings.json` y existe al menos una key con valor distinto al del catálogo
- **THEN** Claude muestra al usuario las keys en conflicto y pide confirmación explícita sobre cuál valor mantener antes de aplicar el merge.

### Requirement: CLAUDE.md se genera con referencia a AGENTS.md y secciones delimitadas

Después de que el skills sync completó y existe `AGENTS.md`, Claude SHALL ejecutar el equivalente al comando `/init` de Claude Code para generar `CLAUDE.md` en la raíz del proyecto. La instrucción SHALL incluir explícitamente que si existe `AGENTS.md`, debe ser referenciado en el `CLAUDE.md` como fuente de documentación de skills disponibles. La sección auto-managed de `CLAUDE.md` SHALL estar delimitada por marcadores HTML (ej. `<!-- AUTO-GENERATED: claude-init-start -->` y `<!-- AUTO-GENERATED: claude-init-end -->`) para que ejecuciones futuras de `sync-skills` puedan regenerar solo esa sección sin tocar el contenido escrito a mano por el usuario.

#### Scenario: Generación post-skills sync

- **WHEN** el skills sync completó y `AGENTS.md` existe en el proyecto
- **THEN** el `CLAUDE.md` generado contiene una referencia explícita a `AGENTS.md`, describe cómo usarlo, y la sección auto-managed está envuelta por los marcadores HTML.

#### Scenario: Skills sync no completó

- **WHEN** el skills sync falló o fue omitido y no existe `AGENTS.md`
- **THEN** Claude genera `CLAUDE.md` de igual manera (con marcadores) pero sin la referencia a `AGENTS.md`.

### Requirement: El setup de Claude Code ocurre después del skills sync

El paso de configuración de Claude Code (settings.json + CLAUDE.md) SHALL ejecutarse después de que el skills sync haya completado, para que el `CLAUDE.md` refleje el estado final del proyecto incluyendo los skills instalados.

#### Scenario: Orden de ejecución

- **WHEN** `/new-project` ejecuta todos sus pasos
- **THEN** la secuencia es: (1) clone + configuración del template, (2) skills sync, (3) settings.json, (4) generación de CLAUDE.md.

### Requirement: El usuario recibe educación sobre .claude/settings.json en dos momentos

`/new-project` SHALL educar al usuario sobre el rol y el mantenimiento de `.claude/settings.json` en dos lugares complementarios: el mensaje de cierre del comando (atención alta, una vez) y una sección permanente en el `CLAUDE.md` generado (referencia futura + contexto para Claude). El contenido SHALL incluir: para qué sirve el archivo, cómo agregar un comando nuevo con un ejemplo concreto, qué NO pre-aprobar (estado compartido, producción, destructivos), y la idea de que el archivo se afina con el uso.

#### Scenario: Mensaje de cierre incluye la educación

- **WHEN** `/new-project` finaliza exitosamente
- **THEN** el mensaje de cierre incluye un bloque que explica `.claude/settings.json`: qué es, por qué afecta la velocidad de desarrollo, ejemplo de cómo agregar un comando seguro, y la lista de categorías de comandos que NO se deben pre-aprobar.

#### Scenario: CLAUDE.md generado incluye la sección permanente

- **WHEN** `CLAUDE.md` se genera al final del flujo de `/new-project`
- **THEN** la sección auto-managed contiene una subsección sobre `.claude/settings.json` con el mismo contenido educativo (para qué sirve, cómo mantenerlo, qué no pre-aprobar), de manera que la información sobreviva a la sesión inicial y quede como contexto cargado en cada sesión futura de Claude Code.
