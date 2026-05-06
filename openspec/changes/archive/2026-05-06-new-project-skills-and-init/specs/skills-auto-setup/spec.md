## ADDED Requirements

### Requirement: El skills sync analiza el proyecto y genera AGENTS.md

Durante la creación de un proyecto con `/new-project`, Claude SHALL ejecutar los Prompts 1 y 2 del repositorio `despegar/agent-rules-and-skills`: analizar el proyecto para determinar qué skills son relevantes y sincronizarlos, generando `AGENTS.md` en la raíz del proyecto. La sección auto-managed de `AGENTS.md` (tabla de skills, descripciones de cada skill compartido) SHALL estar delimitada por marcadores HTML (ej. `<!-- AUTO-GENERATED: skills-start -->` y `<!-- AUTO-GENERATED: skills-end -->`) para soportar merge en re-sincronizaciones futuras.

#### Scenario: Sync exitoso

- **WHEN** el template del proyecto fue clonado y configurado correctamente y el repositorio `despegar/agent-rules-and-skills` está accesible
- **THEN** Claude ejecuta el análisis del proyecto, copia los skills relevantes a `.claude/skills/` (o la carpeta correspondiente al stack), y genera `AGENTS.md` en la raíz del proyecto con la tabla de skills envuelta por los marcadores auto-generated.

#### Scenario: Repositorio de skills inaccesible

- **WHEN** el repositorio `despegar/agent-rules-and-skills` no está accesible durante la ejecución
- **THEN** Claude omite el paso de skills sync, reporta al usuario que el sync no pudo completarse, y continúa con los pasos siguientes del flujo de `new-project`.

### Requirement: El Prompt 3 no se ejecuta durante new-project

Durante la creación del proyecto, Claude SHALL NOT ejecutar el Prompt 3 de generación de skills customizados desde el codebase. Este prompt requiere que el proyecto tenga historia de código real.

#### Scenario: Proyecto recién creado

- **WHEN** `/new-project` finaliza el setup del template
- **THEN** el directorio del proyecto contiene skills compartidos (de los Prompts 1+2) pero no contiene skills generados desde el codebase (Prompt 3).
