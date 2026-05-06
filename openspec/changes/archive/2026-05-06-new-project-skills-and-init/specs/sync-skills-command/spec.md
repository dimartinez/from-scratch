## ADDED Requirements

### Requirement: El comando /from-scratch:sync-skills está disponible en Claude Code

Tras ejecutar `from-scratch init` o `from-scratch update`, el slash command `/from-scratch:sync-skills` SHALL estar disponible globalmente en Claude Code.

#### Scenario: Disponibilidad tras init

- **WHEN** el usuario ejecuta `from-scratch init` exitosamente y reinicia Claude Code
- **THEN** el comando `/from-scratch:sync-skills` aparece en la lista de slash commands disponibles.

### Requirement: sync-skills ejecuta los 3 Prompts de agent-rules-and-skills

Al invocarse, `/from-scratch:sync-skills` SHALL ejecutar los tres prompts de inicialización del repositorio `despegar/agent-rules-and-skills` en orden: análisis del proyecto, sync de skills compartidos, y generación de skills customizados desde el codebase actual.

#### Scenario: Sync completo en proyecto con historia

- **WHEN** el usuario ejecuta `/from-scratch:sync-skills` en un proyecto con código existente
- **THEN** Claude ejecuta los 3 prompts en orden, actualiza `AGENTS.md` con los skills disponibles (compartidos y customizados), y reporta un resumen de qué skills fueron agregados, actualizados o removidos.

#### Scenario: Proyecto sin historia de código

- **WHEN** el usuario ejecuta `/from-scratch:sync-skills` en un proyecto recién creado sin código relevante
- **THEN** Claude ejecuta los Prompts 1 y 2, advierte que el Prompt 3 no generó skills customizados por falta de codebase, y sugiere volver a correr el comando cuando el proyecto tenga más código.

### Requirement: El progreso de /from-scratch:sync-skills es visible mediante TodoWrite

Claude SHALL usar la herramienta TodoWrite al inicio de la ejecución de `/from-scratch:sync-skills` para mostrar todos los pasos del flujo (análisis del proyecto, sync de skills compartidos, generación de skills customizados, actualización de AGENTS.md, regeneración de CLAUDE.md cuando aplique), y SHALL actualizar el estado de cada paso conforme avanza. Esta es la aplicación concreta del principio general definido en design D12.

#### Scenario: Checklist visible durante ejecución

- **WHEN** el usuario invoca `/from-scratch:sync-skills` en un proyecto válido
- **THEN** aparece un TodoWrite con todos los pasos del flujo y cada ítem se marca completado a medida que termina, igual que ocurre con `/new-project`.

### Requirement: sync-skills regenera CLAUDE.md automáticamente cuando AGENTS.md cambia

Si el sync resultó en cambios a `AGENTS.md`, `/from-scratch:sync-skills` SHALL regenerar la sección auto-managed de `CLAUDE.md` automáticamente, sin pedir confirmación, y reportar la regeneración en el resumen de cierre. La regeneración SHALL preservar las secciones de `CLAUDE.md` escritas a mano por el usuario.

#### Scenario: AGENTS.md actualizado

- **WHEN** el sync modifica `AGENTS.md` (se agregaron o removieron skills)
- **THEN** Claude regenera la sección auto-managed de `CLAUDE.md`, preserva las secciones escritas a mano por el usuario, y reporta en el cierre que `CLAUDE.md` fue actualizado.

#### Scenario: Sin cambios en AGENTS.md

- **WHEN** el sync no produce cambios en `AGENTS.md`
- **THEN** Claude reporta que los skills ya están actualizados y no toca `CLAUDE.md`.
