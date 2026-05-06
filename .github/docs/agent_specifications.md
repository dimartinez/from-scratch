# Agent Specifications — from-scratch

Convención de nombres para skills según scope:

- **Globales** (transversales a tecnologías): sin prefijo (ej. `security`, `testing`, `python-3-8`)
- **Internos de Despegar** (compartidos entre apps): prefijo `desp-` (ej. `desp-eva-ui`, `desp-skill-creator`)
- **Internos de la app** (específicos de una aplicación): prefijo del nombre de la app (ej. `fs-catalog`, `fs-state-sync`)

Prefijo de la app actual: `fs-` (de `from-scratch`).

## Stack Tecnológico Detectado

### Backend

- **Python** `>=3.8` — detectado en `pyproject.toml`
- **setuptools (legacy backend)** — detectado en `pyproject.toml` (`build-backend = "setuptools.backends.legacy:build"`)
- **Standard library only (cero dependencias runtime)** — detectado en `pyproject.toml` (no se declara la sección `dependencies`). El CLI usa solo `argparse`, `json`, `hashlib`, `pathlib`, `subprocess`, `threading`, `unittest.mock`.

### Frontend

- **No aplica.** El proyecto es un CLI puro. No existe capa de UI web (HTML/JS/TS). El directorio `node_modules/` que se observa en el workspace es residual de una implementación TypeScript abandonada en el commit `fa966cb` ("Rewrite CLI in Python"); ningún archivo del código actual lo referencia y no hay `package.json` en raíz.

### Infraestructura / Tooling

- **Bash** — detectado en `install.sh` (instalador `curl | bash` con preconditions, clone/pull, generación de wrapper).
- **pytest** `~implícito` — detectado en `pyproject.toml` (`[tool.pytest.ini_options]`); convención `test_*.py` en `tests/`.
- **Git** — usado como mecanismo de distribución (`git clone` / `git pull --ff-only` desde `~/.from-scratch/`) y como dependencia runtime invocada por `subprocess`.
- **OpenSpec** (spec-driven workflow) — detectado en `openspec/config.yaml` (`schema: spec-driven`). Los skills/agents en `.claude/` (propose, apply, archive, ux-reviewer, agentic-reviewer, tdd-reviewer) son la dogfood interna del proyecto.
- **Claude Code Catalog Format** — detectado en `catalog/catalog.json` y `catalog/{commands,stacks}/*.md`. Es el formato de payload que el CLI distribuye a `~/.claude/`.
- **Sin CI, sin Docker, sin Makefile/justfile, sin linters configurados.** El único pipeline de calidad declarado es `pytest` + revisión por agentes OpenSpec.

## Skills Indispensables

### Backend

- **fs-catalog**: Conocer el contrato del catálogo (`catalog/catalog.json` + frontmatter YAML plano). Cada `entry` tiene `kind` (`command` | `stack`) y `source`; los `stack` exigen exactamente `name`, `description`, `template_url` en frontmatter; `command` exige al menos `description`. Una entrada mal formada se filtra silenciosamente o falla — fricción real porque el formato no es estándar de ningún ecosistema.
- **fs-state-sync**: Entender la política de diff de 6 categorías (`added`, `modified`, `unchanged`, `user_modified`, `unowned_conflict`, `removed`) y el rol del `.state.json` con hashes SHA256. Los hashes representan "lo que el CLI instaló", no "lo que hay en disco hoy"; esa distinción habilita la detección de drift y es contraintuitiva para quien venga de gestores de paquetes tradicionales.
- **fs-yaml-frontmatter**: El parser YAML de `src/catalog/yaml_frontmatter.py` es **hand-written y rechaza deliberadamente claves anidadas y listas**. No se puede usar `key:\n  nested: val` ni `- item`. Cualquier contributor que asuma YAML completo escribirá frontmatter inválido.
- **fs-error-contract**: Toda excepción hereda de `FromScratchError` y debe llevar `code` (SCREAMING_SNAKE_CASE) + `remediation` (comando ejecutable). Los tests validan accionabilidad; lanzar una excepción sin `remediation` rompe el contrato de UX y los tests asociados.
- **python-stdlib-only**: Convención dura: **prohibido agregar dependencias runtime**. El proyecto se distribuye vía `curl | bash` y debe correr en Python 3.8+ sin pip install adicional. Cualquier funcionalidad nueva (HTTP, YAML, hashing, atomic writes) debe implementarse con stdlib o copiarse inline.
- **python-3-8**: Mantener compatibilidad con Python 3.8 — sin `match`/`case`, sin `|` en type hints, sin `tomllib`, sin `dict | dict` merge.

### Infraestructura / Tooling

- **fs-install-wrapper**: El binario `from-scratch` no se versiona; se genera dinámicamente por `install.sh` en `~/.local/bin/from-scratch` exportando `PYTHONPATH=$HOME/.from-scratch`. Modificar el layout de `src/` rompe el wrapper. Cualquier nuevo entry-point debe contemplar esta indirección.
- **fs-atomic-writes**: Toda escritura sobre `~/.claude/` y `.state.json` se hace vía temp + `rename` con cleanup de `.tmp.{pid}` huérfanos. Saltarse este patrón en una operación nueva deja el sistema en estado inconsistente si el proceso muere a mitad. Es no-negociable y los tests lo verifican.
- **testing-no-mocks-fs**: La suite usa `tmp_path` (pytest) para filesystem real e `unittest.mock.patch` solo en bordes (subprocess, run_init/run_update). No hay `conftest.py`; cada `test_*.py` define helpers locales (`make_catalog`, `make_git_repo`, etc.). Newcomer que cree un `conftest.py` rompe la convención de aislamiento por archivo.
- **desp-spanish-ux**: Todo texto user-facing (errores, hints, descripciones de CLI, README) está en español; código y nombres de variables en inglés. Aplicable a Despegar en general y verificable en `src/ui/hints.py`, `src/ui/errors.py`, `install.sh`.
- **openspec-workflow**: El proyecto se desarrolla bajo OpenSpec. Cualquier cambio no trivial pasa por `propose → apply → archive` y es revisado por los tres agentes (`ux-reviewer`, `agentic-reviewer`, `tdd-reviewer`) antes de mergear. Cargar contexto desde `openspec/changes/` antes de implementar features nuevas.

## Componentes Compartidos (Referencia)

### Catálogo y parsing

- **`parse_manifest`** — [src/catalog/manifest.py](src/catalog/manifest.py)
    - **Propósito**: Cargar y validar `catalog.json`; filtra entradas con `kind` desconocido emitiendo warning.
    - **Uso**: `parse_manifest(path: Path) -> list[dict]`
- **`parse` (frontmatter)** — [src/catalog/yaml_frontmatter.py](src/catalog/yaml_frontmatter.py)
    - **Propósito**: Extraer frontmatter YAML **plano** (rechaza nesting y listas) y devolver el body restante.
    - **Uso**: `parse(content: str) -> tuple[dict, str]`
- **`parse_stack`** — [src/catalog/stack.py](src/catalog/stack.py)
    - **Propósito**: Validar que un archivo de stack contiene `name`, `description`, `template_url`.
    - **Uso**: `parse_stack(content: str) -> dict`

### Estado y sincronización

- **`read_state` / `write_state` / `compute_hash`** — [src/state/state.py](src/state/state.py)
    - **Propósito**: Persistir `~/.claude/from-scratch/.state.json` con detección de corrupción (JSON inválido, tipo inesperado) y atomicidad (temp + rename). Hash SHA256 trackea la versión instalada por el CLI.
    - **Uso**: `read_state(path) -> Optional[dict]`, `write_state(state, path)`, `compute_hash(content) -> str`, `has_incomplete_sync(state) -> bool`
- **`compute_diff`** — [src/sync/diff.py](src/sync/diff.py)
    - **Propósito**: Comparar catálogo entrante vs. estado instalado y categorizar cada path como `added` / `modified` / `unchanged` / `user_modified` / `unowned_conflict` / `removed`. Esta función concentra la política de seguridad del CLI: sin `--force`, los conflictos se omiten.
    - **Uso**: `compute_diff(catalog_entries, installed_files, dest_base) -> dict[str, list]`
- **`copy_file` / `cleanup_orphan_tmp_files`** — [src/sync/copy.py](src/sync/copy.py)
    - **Propósito**: Escritura atómica con backup opcional `.bak.{ms_timestamp}` y barrido de `.tmp.{pid}` dejados por crashes previos.
    - **Uso**: `copy_file(content, dest, backup: bool) -> None`, `cleanup_orphan_tmp_files(dest_base) -> int`
- **`clone_repo` / `pull_ff_only`** — [src/sync/git.py](src/sync/git.py)
    - **Propósito**: Wrap de operaciones git con clasificación de errores (red vs. divergencia) en `FromScratchError`.
    - **Uso**: `clone_repo(url, dest)`, `pull_ff_only(repo) -> dict` (retorna lista de archivos cambiados).

### UI / salida

- **`Spinner` (context manager)** — [src/ui/output.py](src/ui/output.py)
    - **Propósito**: Spinner threaded en TTY, fallback a mensaje plano cuando stdout está pipeado.
    - **Uso**: `with Spinner("Mensaje", out=stdout): ...`
- **`confirm_prompt`** — [src/ui/output.py](src/ui/output.py)
    - **Propósito**: Prompt `y/n` que tolera `EOFError` (input pipeado) devolviendo `False`.
    - **Uso**: `confirm_prompt(message: str, stdin) -> bool`
- **`show_preview`** — [src/ui/preview.py](src/ui/preview.py)
    - **Propósito**: Render tabular del diff + plan de backups + confirmación previa a aplicar cambios.
    - **Uso**: `show_preview(diff, backups, out, stdin) -> bool`
- **`render_error`** — [src/ui/errors.py](src/ui/errors.py)
    - **Propósito**: Render uniforme de `FromScratchError` con `code`, mensaje y `remediation`; devuelve exit code apropiado.
    - **Uso**: `render_error(err, stderr) -> int`
- **`print_hint`** — [src/ui/hints.py](src/ui/hints.py)
    - **Propósito**: Hub de mensajes contextuales en español (`init_success`, `update_no_changes`, etc.). Centraliza copy para no dispersarlo por los comandos.
    - **Uso**: `print_hint(name: str, out, **kwargs)`

### Comandos

- **`run_init`** — [src/commands/init.py](src/commands/init.py)
    - **Propósito**: Instalar el catálogo en destino limpio o con conflictos; orquesta diff → preview → copy → write_state.
    - **Uso**: `run_init(catalog_dir, dest_dir, state_path, force, out, stdin) -> int`
- **`run_update`** — [src/commands/update.py](src/commands/update.py)
    - **Propósito**: `git pull --ff-only` + sync incremental, preservando archivos no-owned y modificaciones del usuario salvo `--force`.
    - **Uso**: `run_update(clone_dir, dest_dir, state_path, force, out, stdin, skip_pull) -> int`

### Errores

- **`FromScratchError` (jerarquía)** — [src/errors.py](src/errors.py)
    - **Propósito**: Base de todas las excepciones del CLI. Cada subclase define `code` y `remediation` para que `render_error` las muestre accionables.
    - **Uso**: `raise NetworkError(message="...", remediation="Reintentá en unos segundos")` (donde `code = "NETWORK_ERROR"` viene definido en la subclase).
