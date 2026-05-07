## 1. Tests (TDD — escribir antes de implementar)

- [x] 1.1 Escribir tests para el check del binario: encontrado en PATH (OK) y no encontrado (WARN). Mecánica: `monkeypatch.setattr(shutil, "which", lambda name: "/usr/local/bin/from-scratch")` para el caso OK; `lambda name: None` para el caso WARN. Llamar `check_binary()` directamente y assertar el objeto resultado (`status`, `remediation`).
- [x] 1.2 Escribir tests para el check del state file: válido (OK), inexistente (ERROR), corrupto (ERROR con remediación `from-scratch init --force`), sync incompleta (WARN). Mecánica: crear el archivo `.state.json` en `tmp_path` con el contenido correspondiente en cada caso; pasar el path como argumento a `check_state_file(state_path)`. Para el caso corrupto, escribir JSON inválido. Assertar `result.status` y `result.remediation`.
- [x] 1.3 Escribir tests para el check de integridad de archivos: todos OK, archivo faltante (ERROR con remediación `from-scratch update`), hash diferente (WARN). Mecánica: construir un estado registrado en memoria con entradas en `installed_files`; crear los archivos reales en `tmp_path`; pasar ambos como argumento a `check_files_integrity(installed_files, base_path)`. Para el caso faltante, no crear el archivo. Para hash diferente, escribir contenido distinto al registrado. Assertar lista de resultados.
- [x] 1.4 Escribir tests para el check de archivos `.tmp.*` huérfanos: sin huérfanos (OK), con huérfanos (ERROR con remediación `rm ~/.claude/**/*.tmp.*`). Mecánica: pasar `tmp_path` como `base_path` a `check_orphan_tmp(base_path)`; en el caso con huérfanos crear al menos un archivo `foo.tmp.1234` dentro de `tmp_path`. Assertar `result.status` y que `result.remediation` contiene `*.tmp.*`.
- [x] 1.5 Escribir tests para el check de archivos `.bak.*`: sin backups (OK), con 6 o más backups de un mismo archivo (WARN con remediación `rm ~/.claude/**/*.bak.*`). Mecánica: pasar `tmp_path` como `base_path` a `check_bak_files(base_path)`; en el caso con backups crear 6 archivos `commands/foo.bak.1` … `foo.bak.6` dentro de `tmp_path`. Assertar `result.status`.
- [x] 1.6 Escribir tests para el formato de output texto: que el string retornado por `format_text_report(results)` contiene la sección `[ESTADO]`, la sección `[ARCHIVOS]`, la sección `[RESIDUOS]`, y el bloque `=== RESUMEN ===`; que cada línea de check tiene el formato `<clave>: <valor> → STATUS`; que el bloque RESUMEN incluye el hint correcto según estado global (solo-warnings vs. errores presentes). Mecánica: construir listas de objetos resultado con statuses distintos y llamar `format_text_report(results)` directamente; assertar sobre el string retornado con `in` o con comparación de líneas.
- [x] 1.7 Escribir tests para el output JSON: que el dict retornado por `format_json_report(results)` contiene `schema_version == "1"`, `timestamp` (string no vacío), `status` (uno de `ok`, `warn`, `error`), `checks` (lista), `summary` con `error_count` y `warn_count`. Mecánica: construir lista de objetos resultado y llamar `format_json_report(results)` directamente; assertar sobre el dict retornado. No capturar stdout — la función retorna el dict, no imprime.
- [x] 1.8 Escribir tests para el formato Markdown: que el string retornado por `format_markdown_report(results)` contiene un header H1 con timestamp, secciones H2, tablas con separadores correctos (`| --- |`), y `## Resumen` con el status en negrita. Mecánica: construir listas de resultados con distintos statuses; llamar `format_markdown_report(results)` directamente; assertar sobre el string retornado. Para checks con WARN/ERROR, verificar que la remediación aparece en la columna `Detalle`.
- [x] 1.9 Escribir tests para exit codes: que `run_doctor` retorna `0` cuando todos los checks son OK, `1` cuando hay solo warnings, `2` cuando hay al menos un error. Mecánica: reemplazar los checks individuales con stubs que retornan resultados fijos usando `monkeypatch` sobre las funciones `check_binary`, `check_state_file`, etc. Capturar el valor de retorno de `run_doctor(args)` sin `sys.exit` — la función debe retornar el código, no llamar exit directamente.

## 2. Lógica de checks

- [x] 2.1 Escribir tests para el manejo de `PermissionError` en checks que leen disco: que `check_state_file`, `check_files_integrity`, `check_orphan_tmp` y `check_bak_files` retornan un resultado con `status == "error"` y `remediation` no vacío en vez de propagar la excepción. Mecánica: usar `monkeypatch.setattr` sobre `Path.read_bytes` (o el método concreto que cada check usa para leer) para que lance `PermissionError`; llamar cada función directamente y assertar el objeto resultado.
- [x] 2.2 Implementar `check_binary()` en `src/commands/doctor.py` usando `shutil.which`
- [x] 2.3 Implementar `check_state_file()` llamando a `read_state` de `src/state/state.py` y capturando `StateCorruptError` (no `json.JSONDecodeError` directamente); mapear `StateCorruptError` a ERROR con remediación `from-scratch init --force` sin propagar la excepción
- [x] 2.4 Implementar `check_files_integrity()` iterando `installed_files` del state, computando SHA256 por archivo
- [x] 2.5 Implementar `check_orphan_tmp()` con `glob("**/*.tmp.*")` bajo `~/.claude/`
- [x] 2.6 Implementar `check_bak_files()` con `glob("**/*.bak.*")` bajo `~/.claude/`
- [x] 2.7 Implementar `PermissionError` handling en todos los checks que leen disco; capturar como ERROR con remediación explícita y sin traza a stdout

## 3. Orquestador y formato de output

- [x] 3.1 Escribir tests para el bloque `=== RESUMEN ===` en modo texto: que aparece siempre (incluso cuando todo es OK), que muestra el status global, y que incluye el hint de próximo paso correcto según estado (solo-warnings vs. errores presentes). Mecánica: construir listas de resultados con distintos statuses y llamar `format_text_report(results)` directamente; assertar sobre el string retornado.
- [x] 3.2 Implementar `format_text_report(results)` en `src/ui/doctor.py` con secciones `[ESTADO]`, `[ARCHIVOS]`, `[RESIDUOS]`, `=== RESUMEN ===`, output progresivo por sección, y hint de próximo paso al final
- [x] 3.3 Agregar strings en español para todos los labels, remediaciones y mensajes de estado en `src/ui/doctor.py`, siguiendo la tabla de remediaciones definida en `design.md` (una remediación ejecutable por tipo de check)
- [x] 3.4 Escribir tests para que el campo `remediation` en JSON sea `null` cuando el status del check es `ok` y sea un string no vacío cuando es `warn` o `error`. Mecánica: construir objetos resultado con `status="ok"` y con `status="warn"/"error"` y llamar `format_json_report(results)`; assertar sobre los valores del dict retornado por la función (no capturar stdout).
- [x] 3.5 Escribir tests para que `run_doctor` imprime todo output a stdout (incluso cuando hay checks con ERROR) y que no hay contenido en stderr durante una ejecución normal. Mecánica: usar `capsys` de pytest; stubbear los checks con `monkeypatch` para retornar resultados con ERROR; llamar `run_doctor(args)` y assertar `capsys.readouterr().out` contiene la estructura esperada y `capsys.readouterr().err` está vacío.
- [x] 3.6 Implementar `format_json_report(results)` en `src/ui/doctor.py` con estructura `{schema_version, timestamp, status, checks, summary}` y `remediation: null` en checks OK
- [x] 3.7 Implementar `format_markdown_report(results)` en `src/ui/doctor.py` con header H1, secciones H2, tablas markdown por categoría, y sección `## Resumen` con status en negrita y hint de próximo paso
- [x] 3.8 Implementar `run_doctor(args)` en `src/commands/doctor.py` orquestando todos los checks, delegando el formato a `src/ui/doctor.py` según el flag (`--json`, `--markdown`, o texto por defecto), y retornando el exit code como int

## 4. Log rotante

- [x] 4.1 Escribir tests para la escritura del log: que después de llamar `write_doctor_log(entry, log_path)` el archivo contiene la entrada como JSON válido en la última línea. Mecánica: pasar `tmp_path / "doctor.log"` como argumento; assertar que la última línea es JSON parseable con los campos `timestamp`, `status`, `error_count`, `warn_count`.
- [x] 4.2 Escribir tests para la rotación: que cuando el log ya tiene 20 entradas, `write_doctor_log` conserva solo las últimas 19 más la nueva (total 20 líneas). Mecánica: crear el archivo en `tmp_path` con 20 líneas de contenido controlado; llamar `write_doctor_log`; assertar que el archivo tiene exactamente 20 líneas y que la última es la nueva entrada.
- [x] 4.3 Escribir tests para el comportamiento best-effort: que `write_doctor_log` no lanza excepción cuando el directorio no existe o cuando `Path.write_text` lanza `PermissionError`. Mecánica: pasar una ruta en un directorio inexistente; assertar que no se lanza ninguna excepción. Alternativamente, usar `monkeypatch` sobre `os.rename` para lanzar `PermissionError`; verificar que la función retorna sin error.
- [x] 4.4 Implementar `write_doctor_log(entry, log_path)` en `src/commands/doctor.py`: leer líneas existentes, retener las últimas 19, appender la nueva, escribir atómicamente (tmp + rename). Silenciar cualquier excepción.
- [x] 4.5 Integrar `write_doctor_log` en `run_doctor`: llamar al finalizar los checks, antes de imprimir el output. Usar el path por defecto `~/.claude/from-scratch/doctor.log`.

## 5. Integración con CLI

- [x] 5.1 Escribir test de aceptación para el subcomando `doctor` en CLI: que invocar el entry-point con `["doctor"]` llama a `run_doctor` con los args correctos; con `["doctor", "--json"]` pasa `json=True`; con `["doctor", "--markdown"]` pasa `markdown=True`. Mecánica: `monkeypatch` sobre `run_doctor` para capturar los argumentos recibidos; invocar `main(["doctor"])`, `main(["doctor", "--json"])`, y `main(["doctor", "--markdown"])` directamente; assertar los args capturados.
- [x] 5.2 Escribir test para que el help del subcomando `doctor` contiene texto en español. Mecánica: capturar `argparse` usando `capsys` o inspeccionar el objeto parser directamente (`parser.description` / `parser.format_help()`); assertar presencia de al menos una palabra clave española (ej. `"instalación"`).
- [x] 5.3 Registrar el subcomando `doctor` en `src/cli.py`: agregar el parser con flags `--json` y `--markdown` (mutuamente excluyentes con `add_mutually_exclusive_group`), agregar `"doctor"` a la lista `SUBCOMMANDS`, y agregar la rama que llama a `run_doctor`

## 6. Slash command de catálogo

- [x] 6.1 Escribir test que verifica que `catalog.json` incluye la entrada `{ "kind": "command", "source": "commands/from-scratch/doctor.md" }`. Mecánica: leer `catalog/catalog.json` en el test y assertar que el entry existe en `entries`. Este test falla hasta que se agregue la entrada.
- [x] 6.2 Escribir test que verifica que `catalog/commands/from-scratch/doctor.md` tiene frontmatter parseable con campo `description` no vacío. Mecánica: usar `parse_frontmatter` de `src/catalog/yaml_frontmatter.py`; assertar `metadata["description"]` es string no vacío.
- [x] 6.3 Crear `catalog/commands/from-scratch/doctor.md` con frontmatter `description` en español y prompt de sistema que instruye al agente a ejecutar `from-scratch doctor --markdown`, interpretar el reporte, y explicar problemas y remediaciones.
- [x] 6.4 Agregar la entrada al array `entries` de `catalog/catalog.json`.

## 7. Verificación final

- [x] 7.1 Correr suite completa de tests: `python -m pytest` sin regresiones

## Verificación humana (fuera del recuento de cobertura automatizada)


Las siguientes verificaciones requieren interacción humana o un entorno instalado real. No cuentan como cobertura del feature y deben realizarse manualmente antes del merge:

- Verificar que `PYTHONPATH=src python -m cli doctor` funciona end-to-end en un entorno con instalación real bajo `~/.claude/`.
- Verificar exit code `2` manualmente: eliminar un archivo instalado y confirmar que `from-scratch doctor; echo $?` imprime `2`.
- Verificar output JSON legible con `from-scratch doctor --json | python3 -m json.tool` sin errores de parseo.
