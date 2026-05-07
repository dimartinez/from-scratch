## Why

Los usuarios y agentes de IA no tienen forma de inspeccionar el estado de lo que `from-scratch` instaló. Cuando algo falla, no hay punto de partida para el diagnóstico: ni el usuario ni un agente puede saber qué archivos faltan, qué hashes cambiaron, o si la sincronización quedó incompleta.

## What Changes

- Nuevo subcomando `from-scratch doctor` que diagnostica el estado de la instalación.
- Tres formatos de output: texto plano (default), JSON (`--json`), Markdown (`--markdown`).
- Exit codes: `0` (OK), `1` (warnings), `2` (errores) para uso programático.
- Log rotante best-effort en `~/.claude/from-scratch/doctor.log` (JSON Lines, últimas 20 entradas).
- Nuevo comando de catálogo `/from-scratch:doctor` que se instala junto con `init`/`update`.
- Sin acceso a red — diagnóstico offline, rápido y predecible.

## Capabilities

### New Capabilities

- `doctor-command`: Comando que verifica el estado de la instalación e imprime un reporte estructurado con severidades, adecuado para consumo por humanos y agentes de IA; registra cada ejecución en un log rotante.
- `doctor-catalog-command`: Entrada de catálogo `catalog/commands/from-scratch/doctor.md` que expone `/from-scratch:doctor` como slash command de Claude Code para ejecutar el diagnóstico desde dentro de una sesión de IA.

### Modified Capabilities

## Impact

- `src/commands/`: nuevo módulo `doctor.py`.
- `src/cli.py`: registro del subcomando `doctor`.
- `src/ui/`: nuevas strings de salida para el reporte del doctor.
- `catalog/commands/from-scratch/`: nueva entrada `doctor.md`.
- `~/.claude/from-scratch/doctor.log`: archivo creado en el primer run (escritura best-effort, no falla el comando si no puede escribir).
