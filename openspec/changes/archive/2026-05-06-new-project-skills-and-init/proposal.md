## Why

Cuando un desarrollador crea un proyecto con `/new-project`, el proyecto queda funcional pero "ciego" para Claude Code: sin CLAUDE.md, sin skills instalados, sin configuración de permisos. Configurar todo eso manualmente es carga cognitiva innecesaria, especialmente para quien recién empieza.

## What Changes

- `/new-project` agrega tres pasos automáticos al final del flujo actual: instalación de skills compartidos, configuración Claude Code del proyecto, y generación del CLAUDE.md.
- El skill sync se basa en el repositorio `despegar/agent-rules-and-skills` y corre los prompts de inicialización para analizar el proyecto, copiar los skills relevantes, y generar `AGENTS.md`.
- La generación del CLAUDE.md (vía el `/init` built-in de Claude Code) corre **después** del skill sync, para que pueda leer `AGENTS.md` y referenciarlo.
- Todo el flujo es visible mediante TodoWrite: el usuario ve los pasos pero no necesita saber qué es `agent-rules-and-skills`.
- Se agrega el slash command `/from-scratch:sync-skills` para que los proyectos existentes puedan re-sincronizar skills a medida que el proyecto evoluciona.
- El flujo es seguro de re-ejecutar (idempotente): `sync-skills` detecta el estado actual, muestra preview de cambios antes de tocar el disco, escribe archivos de forma atómica (temp + rename) para que cancelar con Ctrl+C deje el proyecto consistente, y reporta errores accionables (qué falló, por qué, qué hacer).
- `sync-skills` preserva skills que el usuario instaló a mano y no provienen del catálogo de `agent-rules-and-skills`: los detecta como tales y los lista en el preview en una categoría separada ("preservados sin cambios"), nunca los toca.
- Al finalizar `/new-project`, el usuario recibe un resumen escaneable (skills instalados, archivos generados, ruta del proyecto) y un hint sobre `/from-scratch:sync-skills` para resincronizar más adelante.

## Capabilities

### New Capabilities

- `skills-auto-setup`: Instalación automática de skills compartidos desde `despegar/agent-rules-and-skills` durante la creación del proyecto (análisis del proyecto → sync de skills → generación de `AGENTS.md`).
- `claude-code-project-setup`: Configuración automática de Claude Code en el proyecto recién creado: `.claude/settings.json` con permisos base y generación de `CLAUDE.md` via `/init` con referencia a `AGENTS.md`.
- `sync-skills-command`: Nuevo slash command `/from-scratch:sync-skills` que re-ejecuta el sync completo de skills en un proyecto existente, incluyendo la regeneración de `AGENTS.md` y actualización de `CLAUDE.md`.

### Modified Capabilities

- `new-project-command`: El flujo del comando incorpora los tres pasos nuevos y usa TodoWrite para mostrar el progreso completo.

## Impact

- `catalog/commands/new-project.md`: se extiende el prompt con los nuevos pasos.
- `catalog/commands/from-scratch/sync-skills.md`: archivo nuevo (slug con prefijo `from-scratch:`).
- `catalog/catalog.json`: se registra el nuevo comando `sync-skills`.
- No hay cambios al CLI Python ni al sistema de stacks.
