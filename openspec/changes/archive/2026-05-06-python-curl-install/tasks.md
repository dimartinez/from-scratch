## 1. Setup del proyecto Python

- [x] 1.1 Crear estructura de directorios: `src/` (con `cli.py`, `commands/`, `sync/`, `state/`, `catalog/`, `ui/`, `bin/`), `tests/` con subdirectorios espejo de `src/`. Cada subdir de `src/` y `tests/` con un `__init__.py` vacío. NO eliminar todavía nada del proyecto TS — coexisten hasta el final.
- [x] 1.2 Agregar `pyproject.toml` con configuración mínima de pytest (test discovery en `tests/`) y declarar `python_requires = ">=3.8"`. NO declarar dependencias de runtime.
- [x] 1.3 Verificar que `python3 -m venv .venv && .venv/bin/pip install pytest && .venv/bin/pytest` corre y reporta "no tests ran" (esqueleto vivo).
- [x] 1.4 Actualizar `.gitignore` para incluir `.venv/`, `__pycache__/`, `*.pyc`, `.pytest_cache/`.

## 2. Parser de YAML frontmatter (mini)

- [x] 2.1 Escribir tests en `tests/catalog/test_yaml_parser.py` que cubran: frontmatter plano `key: value`, valores con comillas dobles, valores con comillas simples, valores con `:` adentro entre comillas, líneas en blanco, líneas de comentario `#`, frontmatter ausente, frontmatter mal formado (sin cierre `---`), nested keys (debe fallar con error claro), listas (debe fallar con error claro). Tests rojos.
- [x] 2.2 Implementar `src/catalog/yaml_frontmatter.py` con función `parse(content: str) -> tuple[dict[str, str], str]` que devuelve frontmatter parseado y el resto del cuerpo. Tests verdes.

## 3. Módulo de errores

- [x] 3.1 Escribir tests en `tests/test_errors.py` que verifican que cada excepción custom tiene un código y un mensaje legible (`NetworkError`, `ManifestParseError`, `FileNotFoundError`, `StateCorruptError`, `GitFastForwardError` — los códigos espejan los del [src/errors.ts](src/errors.ts) actual donde aplique). Tests rojos.
- [x] 3.2 Implementar `src/errors.py` con la jerarquía de excepciones. Tests verdes.
- [x] 3.3 Escribir tests en `tests/test_errors_actionable.py` que verifican que cada excepción expone, además del mensaje base, una propiedad `remediation` no vacía con un comando concreto a ejecutar (mapeo según design.md decisión 6: `NetworkError` referencia `from-scratch update`, `GitFastForwardError` referencia `git status` y `git reset --hard origin/main`, `ManifestParseError` referencia el re-clone, `StateCorruptError` referencia el rm + init, `FileNotFoundError` de catálogo referencia el re-update). Tests rojos.
- [x] 3.4 Extender `src/errors.py` para que cada excepción exponga `remediation`. Tests verdes.
- [x] 3.5 Escribir tests en `tests/test_error_render.py` que verifican que el helper que renderiza errores al usuario (a) escribe a stderr (no stdout), (b) imprime una primera línea con prefijo `ERROR`, (c) imprime una segunda línea con la remediation accionable, (d) retorna el exit code esperado por familia (1 para validación/runtime, 2 para cancelación, 3 para precondición). Tests rojos.
- [x] 3.6 Implementar el helper en `src/ui/errors.py` (o donde encaje). Tests verdes.

## 4. Módulo de state

- [x] 4.1 Escribir tests en `tests/state/test_state.py` que cubren: leer state inexistente devuelve `None`, escribir y releer preserva la estructura, detectar sync incompleto (`hasIncompleteSync`), formato del archivo es JSON con keys camelCase compatibles con la versión TS actual ([src/state/state.ts](src/state/state.ts)). Usar `tmp_path` fixture de pytest. Tests rojos.
- [x] 4.2 Implementar `src/state/state.py`. Tests verdes.
- [x] 4.3 Escribir tests en `tests/state/test_state_corrupt.py` que verifican que leer un state file con JSON inválido (truncado, bytes basura, JSON sintácticamente correcto pero con shape inesperada) lanza `StateCorruptError` (no `JSONDecodeError` crudo) y no deja el reader en estado inconsistente. Tests rojos.
- [x] 4.4 Extender `src/state/state.py` para envolver los errores de parseo en `StateCorruptError`. Tests verdes.
- [x] 4.5 Escribir tests en `tests/state/test_state_hash.py` que verifican que cada entrada del state file de archivo instalado guarda un hash del contenido (sha256 o equivalente determinista de stdlib `hashlib`) además del path. Cubren: escribir state con hashes y releer preserva los hashes, hash distinto para contenidos distintos, hash idéntico para contenido idéntico. Tests rojos.
- [x] 4.6 Extender `src/state/state.py` con el campo de hash. Tests verdes.

## 5. Módulo catálogo (manifest + stack)

- [x] 5.1 Escribir tests en `tests/catalog/test_manifest.py` para parsear `catalog.json`: entradas válidas, kinds reconocidos (`command`, `stack`), entrada sin `source` (debe fallar con error claro), `catalog.json` ausente o no-JSON (debe fallar con `ManifestParseError`). Verificar que la presencia o ausencia de `requires_binary` NO afecta el parseo (campo ignorado, sin warning). Tests rojos.
- [x] 5.2 Implementar `src/catalog/manifest.py`. Tests verdes.
- [x] 5.3 Escribir tests en `tests/catalog/test_manifest_unknown_kind.py` que verifican el comportamiento de forward-compat (design.md decisión 2.1): cuando una entrada tiene un `kind` no reconocido (ej. `agent`, `skill`, `hook`, `comand` typo), (a) el parser NO lanza excepción, (b) emite un `WARN` a stderr nombrando el kind y el `source`, (c) la entrada se omite del resultado, (d) las entradas con kinds reconocidos en el mismo `catalog.json` se parsean normalmente. Tests rojos.
- [x] 5.4 Implementar la rama de skip+warn en `src/catalog/manifest.py`. Tests verdes.
- [x] 5.5 Escribir tests en `tests/catalog/test_stack.py` para parsear archivos de stack: frontmatter con `name`, `description`, `template_url` requeridos; archivo sin frontmatter; frontmatter con campo faltante; cuerpo markdown ignorado. Tests rojos.
- [x] 5.6 Implementar `src/catalog/stack.py` apoyándose en `yaml_frontmatter.parse`. Tests verdes.

## 6. Driver de git (reemplaza fetch HTTP)

- [x] 6.1 Escribir tests en `tests/sync/test_git.py` con `tmp_path` y un repo git local: `clone_repo` clona OK; `pull_ff_only` retorna OK cuando no hay cambios; `pull_ff_only` retorna OK y lista de archivos cambiados cuando hay commits remotos; `pull_ff_only` falla con `GitFastForwardError` cuando el local tiene cambios sin commitear; detección de cambios en `src/` vs `catalog/`. Tests rojos.
- [x] 6.2 Implementar `src/sync/git.py` como wrapper de `subprocess.run(["git", ...])`. Tests verdes.
- [x] 6.3 Escribir tests en `tests/sync/test_git_network.py` que verifican el manejo de fallas de conectividad (design.md decisión 6): `clone_repo` contra una URL inalcanzable lanza `NetworkError` (no `CalledProcessError` crudo) y no deja directorios parciales; `pull_ff_only` cuando el remote no responde lanza `NetworkError` y deja el clone local intacto. Simular vía URL bogus o `GIT_SSH_COMMAND=/bin/false`. Tests rojos.
- [x] 6.4 Extender `src/sync/git.py` para envolver fallas de red/transport en `NetworkError`. Tests verdes.
- [x] 6.5 Escribir tests en `tests/sync/test_git_cancel.py` que verifican el contrato de cancelación durante subprocess `git` (design.md decisión 6.2): durante un `pull_ff_only` simulado largo, enviar SIGINT al proceso Python deja el clone local en estado consistente (o se completó el pull, o no se aplicó nada — nunca un estado intermedio); el `KeyboardInterrupt` propaga al caller para que el handler general convierta a exit code 2. Tests rojos.
- [x] 6.6 Verificar que el wrapper `subprocess.run` en `src/sync/git.py` no usa `start_new_session=True` y deja propagar `KeyboardInterrupt`. Tests verdes.

## 7. Diff y copy

- [x] 7.1 Escribir tests en `tests/sync/test_diff.py` que comparan estado local vs catálogo y producen lista de archivos `added`, `modified`, `unchanged`, `removed`. Cubren: archivos idénticos, archivos modificados, archivos nuevos en remoto, archivos solo locales. Tests rojos.
- [x] 7.2 Implementar `src/sync/diff.py`. Tests verdes.
- [x] 7.3 Escribir tests en `tests/sync/test_diff_drift.py` que verifican la detección de drift (design.md decisión 6.1): dado un archivo registrado en el state file con hash `H1` y contenido en disco con hash `H2 != H1`, el diff lo categoriza como `user_modified` (no como `unchanged` ni como `modified` simple); cuando el catálogo además trae cambios para ese archivo, sigue siendo `user_modified` con flag adicional indicando que también hay update remoto pendiente; archivos cuyo hash en disco coincide con el registrado se categorizan normal. Tests rojos.
- [x] 7.4 Extender `src/sync/diff.py` con la categoría `user_modified`. Tests verdes.
- [x] 7.5 Escribir tests en `tests/sync/test_diff_unowned_conflict.py` que verifican: dado un archivo del catálogo cuyo path destino existe en `~/.claude/` pero NO está registrado en el state file (típico: usuario tenía su propio `commands/new-project.md` antes del primer `init`), el diff lo categoriza como `unowned_conflict`. Tests rojos.
- [x] 7.6 Extender `src/sync/diff.py` con la categoría `unowned_conflict`. Tests verdes.
- [x] 7.7 Escribir tests en `tests/sync/test_diff_preserves_user_files.py` que verifican que archivos presentes en `~/.claude/from-scratch/` o `~/.claude/commands/` que NO están en el catálogo NI registrados en el state file se ignoran completamente (no aparecen en ninguna categoría del diff, ni siquiera como `removed`). Caso típico: usuario crea `~/.claude/from-scratch/stacks/local-experiment.md` propio. Tests rojos.
- [x] 7.8 Ajustar `src/sync/diff.py` para que el algoritmo itere solo sobre paths del catálogo y del state file (nunca sobre el contenido del filesystem destino). Tests verdes.
- [x] 7.9 Escribir tests en `tests/sync/test_copy.py` que verifican: copia simple a path destino, creación de directorios intermedios, backup `.bak.<timestamp>` antes de pisar, integridad del contenido copiado. Tests rojos.
- [x] 7.10 Implementar `src/sync/copy.py`. Tests verdes.
- [x] 7.11 Escribir tests en `tests/sync/test_copy_atomic.py` que verifican la garantía de escritura atómica: (a) la escritura usa un archivo temporal `<destino>.tmp.<pid>` en el mismo directorio y se mueve con `os.rename` al final, (b) si se simula un fallo entre la creación del temp y el rename (ej. patcheando rename para que tire excepción), el archivo destino queda intacto en su contenido previo, (c) si el destino no existía, queda inexistente tras el fallo, (d) el backup `.bak.<timestamp>` se crea ANTES de que arranque la escritura del nuevo contenido, (e) el state file se escribe con el mismo patrón temp+rename. Tests rojos.
- [x] 7.12 Refactorizar `src/sync/copy.py` y el writer del state para usar el patrón temp+rename. Tests verdes.
- [x] 7.13 Escribir tests en `tests/sync/test_copy_cleanup.py` que verifican que cuando arranca una operación de sync y existen archivos `<destino>.tmp.<pid>` huérfanos de una corrida previa interrumpida, la nueva corrida los detecta y los limpia antes de empezar. Tests rojos.
- [x] 7.14 Implementar la limpieza de tempfiles huérfanos. Tests verdes.

## 8. Output / UI

- [x] 8.1 Escribir tests en `tests/ui/test_output_prefixes.py` que capturan stdout y verifican que el helper de print de archivos categorizados imprime una línea por archivo con el prefijo correcto: `+ path` para added, `~ path` para modified, `= path` para unchanged, `! path` para conflict. Tests rojos.
- [x] 8.2 Implementar la función de print por categoría en `src/ui/output.py`. Tests verdes.
- [x] 8.3 Escribir tests en `tests/ui/test_output_summary.py` que verifican el formato del resumen final: una línea por categoría con conteos, omitir categorías con conteo 0, orden estable (added, modified, unchanged, conflict). Tests rojos.
- [x] 8.4 Implementar la función de resumen final en `src/ui/output.py`. Tests verdes.
- [x] 8.5 Escribir tests en `tests/ui/test_output_prompt.py` que verifican el prompt de confirmación: lee de stdin, default `n` cuando el usuario aprieta Enter, acepta `s`/`y` como afirmativo, cualquier otro input se interpreta como negativo, no rompe ante EOF (input cerrado) y devuelve negativo en ese caso. Tests rojos.
- [x] 8.6 Implementar la función de prompt en `src/ui/output.py`. Tests verdes.
- [x] 8.7 Escribir tests en `tests/ui/test_output_spinner.py` que verifican el spinner: invocado como context manager arranca un thread daemon que escribe a stderr, el `__exit__` para el thread y limpia la línea, en TTY no interactiva degrada a una línea de log por fase (sin caracteres rotando). Tests rojos.
- [x] 8.8 Implementar el spinner en `src/ui/output.py` (`time`, `threading`, `sys.stderr.isatty()`). Tests verdes.
- [x] 8.9 Escribir tests en `tests/ui/test_output_streams.py` que verifican el split stdout/stderr según design.md decisión 6: líneas informativas y de éxito van a stdout; warnings (prefijo `WARN`) y errores (prefijo `ERROR`) van a stderr; el spinner se renderiza a stderr para no contaminar stdout cuando la salida se redirige a un archivo. Tests rojos.
- [x] 8.10 Ajustar `src/ui/output.py` para respetar el split. Tests verdes.
- [x] 8.11 Escribir tests en `tests/ui/test_preview.py` que verifican el helper de preview pre-confirmación: dada una lista de archivos categorizados, imprime (a) header con conteos (`+ N nuevos, ~ N modificados, = N sin cambios, ! N en conflicto`), (b) cuerpo con cada path prefijado por su símbolo, (c) cuando hay backups planificados, los paths exactos `.bak.<timestamp>`, (d) prompt sí/no con default `n`. Tests rojos.
- [x] 8.12 Implementar `src/ui/preview.py`. Tests verdes.
- [x] 8.13 Escribir tests en `tests/ui/test_signal_handler.py` que verifican que un SIGINT (Ctrl+C) capturado durante un comando: imprime "Cancelado por el usuario." en stderr, sale con exit code 2, y no propaga el `KeyboardInterrupt` con stack trace al usuario. Tests rojos.
- [x] 8.14 Implementar el signal handler en `src/cli.py` (o `src/ui/signal.py` si conviene aislarlo). Tests verdes.
- [x] 8.15 Escribir tests en `tests/ui/test_hints.py` que verifican los hints contextuales: final de `init` exitoso menciona `from-scratch update`; final de `update` sin cambios menciona la última fecha de sync del state file; `from-scratch` sin args muestra `--help`; `from-scratch <subcomando-invalido>` sugiere el subcomando válido más cercano. Tests rojos.
- [x] 8.16 Implementar los hints en los puntos correspondientes de `src/cli.py` y `src/commands/*.py`. Tests verdes.

## 9. Parsing de argumentos CLI

- [x] 9.1 Escribir tests en `tests/test_cli_args.py` que verifican: `from-scratch` sin args muestra help, `from-scratch init`, `from-scratch update`, flag `--force`, `--help`, subcomando inválido produce error con sugerencia, ayuda específica por subcomando (`from-scratch init --help`). Tests rojos.
- [x] 9.2 Implementar parser en `src/cli.py` (sección de args, separada del entry point). Tests verdes.

## 10. Comando `init`

- [x] 10.1 Escribir tests de integración en `tests/commands/test_init.py` con `tmp_path` simulando `~/.claude/`: init en directorio vacío instala todos los archivos, init con `--force` sobreescribe con backup, init con archivos pre-existentes sin state file los detecta como conflictos y se planta, cancelación en confirmación no toca disco. Tests rojos.
- [x] 10.2 Implementar `src/commands/init.py` orquestando manifest + diff + copy + state. Tests verdes.
- [x] 10.3 Escribir tests en `tests/commands/test_init_idempotent.py` que verifican: `init` invocado cuando el state file refleja una instalación completa sale con código 0, no toca disco, e imprime el hint "ya está inicializado, usá `from-scratch update` para sincronizar"; `init` invocado cuando el state file refleja sync incompleto detecta `hasIncompleteSync` e informa qué archivos quedaron pendientes y ofrece reanudar; `init --force` sobre instalación previa sí avanza pero muestra preview enfatizando los archivos que serán pisados. Tests rojos.
- [x] 10.4 Implementar las ramas de idempotencia en `src/commands/init.py`. Tests verdes.
- [x] 10.5 Escribir tests en `tests/commands/test_init_preview.py` que verifican que antes del prompt de confirmación, `init` siempre imprime el preview (lista categorizada de archivos + conteos), incluso cuando el directorio está limpio. Tests rojos.
- [x] 10.6 Conectar `init` con `src/ui/preview.py`. Tests verdes.

## 11. Comando `update`

- [x] 11.1 Escribir tests de integración en `tests/commands/test_update.py` con un repo git local como remoto: update sin cambios remotos no toca nada y reporta "todo está al día"; update con catálogo nuevo aplica cambios tras confirmación; update con clone local sucio falla con mensaje claro y NO toca `~/.claude/`; update con cambios en `src/` además del catálogo imprime el aviso "código actualizado". Tests rojos.
- [x] 11.2 Implementar `src/commands/update.py` con la secuencia: `git pull --ff-only` → diff → confirm → copy → state. Tests verdes.
- [x] 11.3 Escribir tests en `tests/commands/test_update_preview.py` que verifican que `update` muestra el preview categorizado (incluido el bloque `! N en conflicto` cuando aplica) antes del prompt y nunca aplica cambios sin la confirmación. Tests rojos.
- [x] 11.4 Conectar `update` con `src/ui/preview.py`. Tests verdes.
- [x] 11.5 Escribir tests en `tests/commands/test_update_no_changes_hint.py` que verifican que cuando no hay cambios, el mensaje final incluye la fecha de la última sincronización leída del state file (formato legible, no epoch crudo). Tests rojos.
- [x] 11.6 Implementar la lectura de `lastSyncAt` del state file en el path "no changes" de `update`. Tests verdes.
- [x] 11.7 Escribir tests en `tests/commands/test_update_user_modified.py` que verifican el comportamiento ante drift (design.md decisión 6.1): cuando un archivo rastreado fue modificado a mano por el usuario y el catálogo trae update remoto para el mismo archivo, (a) sin `--force`, el preview lo muestra con prefijo `! path (modificado localmente)`, el comando se planta y NO pisa el archivo aunque el usuario confirme `s` para los demás cambios; (b) con `--force`, hace backup `.bak.<timestamp>` con el contenido modificado y aplica el update; (c) si el archivo modificado por el usuario NO tiene update remoto, simplemente no aparece en el diff (queda como está). Tests rojos.
- [x] 11.8 Implementar la rama de drift en `src/commands/update.py`. Tests verdes.
- [x] 11.9 Escribir tests en `tests/commands/test_update_preserves_unowned.py` que verifican que `update` no borra ni toca archivos en `~/.claude/from-scratch/` o `~/.claude/commands/` que no estén ni en el catálogo ni en el state file (ej. archivos creados por el usuario después del init). Tests rojos.
- [x] 11.10 Ajustar `src/commands/update.py` para que el algoritmo de aplicación itere solo sobre paths del diff y nunca llame a delete sobre paths fuera del state file. Tests verdes.
- [x] 11.11 Escribir tests en `tests/commands/test_update_cancel_safety.py` que verifican el contrato de cancelación segura (design.md decisión 6 "Cancelación segura"): simular SIGINT durante la fase de copy (después del confirm, antes de escribir todos los archivos) deja `~/.claude/` en un estado donde (a) los archivos ya copiados completamente quedan completos, (b) ningún archivo queda truncado o a medias, (c) los `.bak.<timestamp>` de los que sí se llegaron a procesar permanecen para recovery manual, (d) los `<destino>.tmp.<pid>` huérfanos los limpia la siguiente corrida (cubierto por 7.13 pero re-verificado a nivel comando), (e) el state file refleja `hasIncompleteSync == true` con la lista de archivos pendientes. Tests rojos.
- [x] 11.12 Implementar la marca `hasIncompleteSync` y el flush parcial del state file en el flujo de update. Tests verdes.

## 12. Entry point y wrapper

- [x] 12.1 Escribir tests en `tests/test_cli_entrypoint.py` que verifican el dispatch del entry point: invocar `cli.main(["init"])` llama al handler de `commands.init` con los args parseados; idem para `update`; `cli.main([])` muestra `--help` y retorna exit code 0; un subcomando inválido retorna exit code 1 (validación) y emite la sugerencia más cercana; una excepción `NetworkError` propagada por un comando se mapea a exit code 1; un `KeyboardInterrupt` se mapea a exit code 2; una excepción inesperada (no-prevista) se mapea a exit code 1 y stack trace breve. Tests rojos.
- [x] 12.2 Implementar `src/cli.py` como entry point completo (orquesta `args` parser, dispatch a `commands.init` / `commands.update`, manejo central de excepciones → exit codes). Tests verdes.
- [x] 12.3 Escribir tests en `tests/test_wrapper_bash.py` que invocan `src/bin/from-scratch` vía `subprocess.run` y verifican: el wrapper pasa los args al script Python sin transformación (probar con args con espacios, args con `--`, sin args), el exit code del Python se preserva, stdout/stderr se preservan separados. Tests rojos.
- [x] 12.4 Crear el wrapper bash en `src/bin/from-scratch`:
  ```bash
  #!/usr/bin/env bash
  exec python3 "$HOME/.from-scratch/src/cli.py" "$@"
  ```
  con permisos de ejecución (`chmod +x` registrado en git via `update-index --chmod=+x`). Tests verdes (los tests pueden setear `HOME` apuntando a `tmp_path` y armar el layout esperado).

## 13. Bootstrap `install.sh`

- [x] 13.1 Escribir tests en `tests/test_install_sh.py` que invocan `install.sh` con `subprocess.run` en un `tmp_path` con `$HOME` mockeado vía env vars. Cubren: install limpio crea `~/.from-scratch/`, escribe wrapper en `~/.local/bin/`, lo hace ejecutable; install con `~/.from-scratch/` ya existente hace `git pull`; falta `git` → exit code distinto de cero, sin escrituras; falta `python3` → idem; `python3 --version` reporta 3.7 → idem; `~/.local/bin` ausente del PATH → mensaje impreso pero el wrapper queda escrito; instalación previa npm detectada vía `npm root -g` → exit no-cero, mensaje, sin escrituras. Tests rojos.
- [x] 13.2 Escribir `install.sh` en la raíz del repo. Implementar todas las ramas hasta que los tests pasen.
- [x] 13.3 Escribir tests en `tests/test_install_sh_messaging.py` que verifican el contrato de UX del install: (a) cada error de precondición (git ausente, python3 ausente, python3 < 3.8, npm previo detectado) imprime el comando concreto a ejecutar para resolverlo (mapeo en design.md decisión 6), (b) los errores van a stderr, (c) el éxito imprime al final un hint con el siguiente paso (`from-scratch init`), (d) el feedback durante `git clone`/`git pull` no queda en silencio (al menos una línea por fase, "Clonando…" / "Actualizando…"). Tests rojos.
- [x] 13.4 Ajustar `install.sh` con los mensajes y el routing stdout/stderr correspondientes. Tests verdes.

## 14. Migración del catalog.json

- [x] 14.1 Eliminar el campo `requires_binary` de [catalog/catalog.json](catalog/catalog.json). El parser de manifest ya lo ignora desde 5.1, pero limpiarlo del JSON evita confusión.

## 15. Smoke test end-to-end

- [x] 15.1 Crear `tests/test_e2e.py` que: clona el propio repo a un `tmp_path`, ejecuta `install.sh` con `$HOME` apuntando ahí, luego invoca el wrapper instalado para correr `from-scratch init`, después modifica un archivo del catálogo en el "remote" y corre `from-scratch update`, verificando que el cambio llegó a `~/.claude/`. Test rojo si falla.
- [x] 15.2 Ajustar lo necesario hasta que e2e pase.

## 16. Actualización del README

- [x] 16.1 Reemplazar la sección **Instalación** ([README.md:13-19](README.md#L13-L19)): cambiar el bloque `npm i -g github:dimartinez/from-scratch` por:
  ```bash
  curl -fsSL https://raw.githubusercontent.com/dimartinez/from-scratch/main/install.sh | bash
  ```
  Cambiar "Requiere Node.js >= 18" por "Requiere `git`, `python3` (>= 3.8) y `bash`".
- [x] 16.2 Eliminar la sección **¿Por qué `dist/` está en el repo?** ([README.md:168-174](README.md#L168-L174)) — ya no aplica.
- [x] 16.3 Reescribir la sección **Desarrollo de la CLI** ([README.md:138-167](README.md#L138-L167)): eliminar referencias a `npm install`, `npm run build`, pre-commit hook de build, `tsx`, vitest. Reemplazar con flujo Python: `python3 -m venv .venv && .venv/bin/pip install pytest`, correr tests con `python3 -m pytest`, archivos editables directamente sin compilar.
- [x] 16.4 Eliminar la sección **Política de versionado y handshake** ([README.md:111-122](README.md#L111-L122)) o reemplazarla con una nota corta: "El código y el catálogo viajan juntos en cada `git pull`. No hay versionado independiente del binario; eliminamos el handshake `requires_binary` que existía en versiones previas".
- [x] 16.5 En la sección **Cómo funciona `~/.claude/`** ([README.md:124-136](README.md#L124-L136)): verificar que sigue exacta — el state file y el layout de `~/.claude/` no cambian. Solo agregar una mención breve de que `~/.from-scratch/` es donde vive el clone que ejecuta la CLI.
- [x] 16.6 Actualizar el mensaje de error citado en la sección de versionado (si quedó alguna referencia) para que refleje el nuevo flujo.

## 17. Cleanup del scaffolding TypeScript

- [x] 17.1 Eliminar archivos: `package.json`, `package-lock.json`, `tsconfig.json`, `vitest.config.ts`.
- [x] 17.2 Eliminar directorios: `dist/`, `node_modules/`, `scripts/` (contiene solo `add-shebang.js`).
- [x] 17.3 Eliminar todo el contenido TS bajo `src/` que estaba antes (preservar solo lo creado en este change). Nota: esto se hace al final, después de que toda la suite Python esté verde, para minimizar ventanas en las que el repo quede roto.
- [x] 17.4 Eliminar el git hook de pre-commit en `.githooks/` que compilaba TypeScript. Si ese era el único hook, eliminar el directorio. Actualizar `npm run setup` (si todavía existe alguna referencia) a un comando equivalente Python o eliminar.
- [x] 17.5 Verificar que `git grep -i "npm\|tsc\|vitest\|tsx"` en la raíz del repo (excluyendo el directorio `openspec/`) no devuelve resultados — si quedan, son referencias a corregir.

## 18. Validación OpenSpec

- [x] 18.1 Correr `openspec validate python-curl-install --strict` y resolver cualquier issue que reporte.
- [x] 18.2 Correr la suite completa: `python3 -m pytest`. Toda verde.
- [x] 18.3 Smoke test manual en máquina del autor: hacer `npm uninstall -g from-scratch` (si aplica), correr `curl ... | bash` apuntando a una rama de prueba, ejecutar `from-scratch init` y `from-scratch update`, validar que `~/.claude/commands/new-project.md` y `~/.claude/from-scratch/stacks/java.md` quedan instalados con el contenido correcto.
