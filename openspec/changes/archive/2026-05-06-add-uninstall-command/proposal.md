## Why

El CLI tiene un comando `init` para instalar el catálogo en `~/.claude/`, pero no tiene forma de deshacerlo. Sin un comando de desinstalación, el usuario no puede limpiar completamente su entorno ni volver a un estado virgen para hacer un `init` limpio.

## What Changes

- Nuevo subcomando `from-scratch uninstall` en el CLI.
- Borra todos los archivos listados en `installed_files` del state file (sin importar si fueron modificados por el usuario).
- Limpia directorios vacíos que queden bajo `~/.claude/` tras el borrado.
- Borra el directorio de state (`~/.claude/from-scratch/`).
- Borra el directorio del tool (`~/.from-scratch/`).
- Borra el wrapper (`~/.local/bin/from-scratch`).
- Muestra preview de lo que va a borrar y pide confirmación antes de actuar.

## Capabilities

### New Capabilities

- `uninstall-command`: Comando que revierte completamente la instalación de from-scratch — archivos del catálogo, state, tool y wrapper — dejando el sistema como si nunca se hubiera instalado.
- Preview detallada antes de confirmar: lista de archivos a borrar con recuento, rutas del state dir, tool dir y wrapper.
- Errores de permisos no abortan el proceso: el comando borra lo que puede e informa al final los elementos que fallaron con su remediación (`sudo rm <ruta>`).
- Hints de próximo paso en todos los mensajes terminales ("Para volver a instalarlo: from-scratch init").

### Modified Capabilities

## Impact

- **`src/cli.py`**: registrar el nuevo subcomando `uninstall`.
- **`src/commands/`**: nuevo módulo `uninstall.py` con `run_uninstall`.
- **`src/ui/hints.py`**: copias en español para la preview y confirmación del uninstall.
- **`tests/commands/`**: nuevo `test_uninstall.py`.
- **No hay cambios en `src/catalog/`, `src/sync/`, ni `src/state/`** — el uninstall usa primitivas ya existentes (`read_state`, operaciones de `pathlib`).
