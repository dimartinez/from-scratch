## Why

El AV de las laptops corporativas de Despegar borra archivos con extensión `.js` por extensión, dejando huérfanos los `.d.ts` después de `npm i -g github:dimartinez/from-scratch`. La distribución actual está rota en su único entorno objetivo y no hay arreglo posible que mantenga JavaScript en disco. Necesitamos un canal de distribución alternativo, escrito en un lenguaje cuya extensión no esté en la lista del AV, que cualquier dev de Despegar pueda ejecutar sin pelearse con seguridad ni con package managers.

## What Changes

- **BREAKING**: Reescribir la CLI en Python 3 usando solo stdlib — sin `pip install`, sin transpile step, sin archivos `.js` en disco.
- **BREAKING**: Reemplazar `npm i -g github:dimartinez/from-scratch` por `curl -fsSL .../install.sh | bash` como único método de instalación.
- **BREAKING**: Eliminar el handshake `requires_binary` del catálogo. Como código y catálogo viajan juntos en cada `git pull`, no existe el escenario de binario desactualizado.
- Layout en disco del usuario: clone del repo en `~/.from-scratch/`, wrapper bash de 3 líneas en `~/.local/bin/from-scratch` (`exec python3 ~/.from-scratch/src/cli.py "$@"`).
- `from-scratch update` ejecuta `git pull --ff-only` en `~/.from-scratch/` antes de sincronizar `~/.claude/` — un solo comando actualiza código y catálogo.
- `install.sh` detecta una instalación previa vía npm (revisa `$(npm root -g)/from-scratch`) y pide al usuario ejecutar `npm uninstall -g from-scratch` manualmente antes de continuar; no toca npm automáticamente.
- Parsear YAML frontmatter con un mini-parser casero (~20 líneas, formato plano `key: value`) en lugar de depender de PyYAML.
- Eliminar `dist/`, `package.json`, `package-lock.json`, `tsconfig.json`, `vitest.config.ts`, `node_modules/`, el script `scripts/add-shebang.js`, y el git hook de pre-commit que compila TypeScript.
- Migrar los tests de vitest al runner Python elegido (decisión cerrada en design.md).
- Actualizar `README.md`: reemplazar la sección de instalación, eliminar "¿Por qué `dist/` está en el repo?", reescribir "Desarrollo de la CLI" sin npm/build, eliminar o re-explicar "Política de versionado y handshake".
- Hacer contrato explícito (en design.md) los patrones de UX que la versión TS aplicaba parcialmente: feedback visual en operaciones largas, preview obligatorio antes de cada confirmación, mensajes de error con remediación accionable, garantía de idempotencia y de cancelación segura (escrituras atómicas con temp+rename), output consistente y hints contextuales que enseñan el próximo paso.
- Hacer contrato explícito que `~/.claude/` es directorio compartido: `from-scratch` solo toca archivos rastreados en su state file y nunca asume control exclusivo. Detectar drift (archivos rastreados modificados a mano por el usuario) vía hash y bloquear el overwrite sin `--force`. No tocar archivos en `~/.claude/agents/`, `~/.claude/skills/`, `~/.claude/settings.json` ni cualquier otro subdirectorio fuera de los paths del catálogo.
- Manejar forward-compat del catálogo: el parser de `catalog.json` ignora con `WARN` cualquier `kind` desconocido (futuros `agent`, `skill`, `hook`) y procesa los reconocidos. Permite agregar tipos de artefacto nuevos sin breaking change del lado del binario.

## Capabilities

### New Capabilities

Ninguna. El cambio reshape el cómo del instalador, no agrega comportamientos nuevos al usuario.

### Modified Capabilities

- `installer-cli`: cambia completamente el mecanismo de distribución (npm → curl|bash + clone), redefine el flujo de update para incorporar `git pull --ff-only` antes de sincronizar, elimina el handshake de versión, y reemplaza la dependencia explícita en `@clack/prompts` por un equivalente en stdlib Python.

## Impact

- **Código de la CLI**: `src/` reescrito íntegro de TypeScript a Python. La separación en módulos (`cli`, `commands`, `sync`, `state`, `catalog`, `ui`) se preserva conceptualmente pero los archivos cambian.
- **Distribución**: nuevo `install.sh` en la raíz del repo. README rehecho en las secciones afectadas.
- **Test runner**: vitest fuera, pytest o stdlib `unittest` adentro (definido en design.md).
- **Catálogo** (`catalog/catalog.json`, `catalog/commands/`, `catalog/stacks/`): sin cambios de formato. Solo cambia quién lo lee.
- **State file** (`~/.claude/from-scratch/.state.json`): sin cambios de formato. La compatibilidad con instalaciones previas se preserva.
- **Usuarios con instalación npm previa**: necesitan ejecutar `npm uninstall -g from-scratch` manualmente antes de correr el nuevo `install.sh`. El script lo detecta y se los indica.
- **Capability spec `installer-cli`**: requiere delta importante (varias requirements MODIFIED, una REMOVED).
