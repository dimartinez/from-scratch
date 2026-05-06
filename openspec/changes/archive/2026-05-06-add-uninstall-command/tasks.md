## 1. Bootstrap de tests

- [x] 1.1 Crear `tests/commands/test_uninstall.py` con helper `make_installed_env(tmp_path)` que escribe un `.state.json` con al menos dos entradas en `installed_files` y crea los archivos correspondientes en disco bajo `tmp_path`; el helper retorna un dict con `dest_dir`, `state_path`, `tool_dir` y `wrapper_path` todos dentro de `tmp_path`

## 2. Mensajes UI

- [x] 2.1 Test: `render_uninstall_preview` retorna texto que incluye el recuento de archivos, las rutas del state dir, tool dir y wrapper — harness: llamada directa a la función con datos fijos, assertir contenido concreto en el string retornado; no requiere filesystem
- [x] 2.2 Agregar función `render_uninstall_preview(files, dirs, state_dir, tool_dir, wrapper)` en `src/ui/preview.py` que devuelve el texto formateado del preview
- [x] 2.3 Test: `already_uninstalled` y `uninstall_success` y `uninstall_cancelled` contienen el texto esperado en español — harness: importar las constantes/funciones de `src/ui/hints.py` y assertir que los strings incluyen "from-scratch init"; no requiere filesystem
- [x] 2.4 Agregar hint `already_uninstalled` en `src/ui/hints.py` con texto y hint de `from-scratch init` (español)
- [x] 2.5 Agregar hint `uninstall_success` en `src/ui/hints.py` con hint "Para volver a instalarlo: from-scratch init" (español)
- [x] 2.6 Agregar hint `uninstall_cancelled` en `src/ui/hints.py` (español)
- [x] 2.7 Test: `UninstallPermissionError` tiene `code == "UNINSTALL_PERMISSION_ERROR"` y `remediation` contiene `sudo rm` — harness: instanciar la clase con una ruta de ejemplo y assertir los atributos directamente
- [x] 2.8 Agregar subclase `UninstallPermissionError` en `src/errors.py` (hereda `FromScratchError`) con `code = "UNINSTALL_PERMISSION_ERROR"` y `remediation` que incluye `sudo rm <ruta>`; los errores de permisos individuales no se lanzan como excepción sino que se acumulan en lista y se reportan al final, por lo que esta clase se usa solo si se quiere renderizar el resumen vía el contrato de errores del proyecto

## 3. Comando uninstall — estado ausente y state corrupto

- [x] 3.1 Test: cuando no existe el state file, `run_uninstall` retorna exit code 0 y el output capturado incluye el hint "from-scratch init" — harness: `make_installed_env` sin crear el archivo `.state.json`; `out = io.StringIO()`; `stdin = io.StringIO()`; llamar `run_uninstall` con esos argumentos y assertir código de retorno y contenido de `out.getvalue()`
- [x] 3.2 Test: cuando `read_state` lanza `StateCorruptError`, `run_uninstall` retorna exit code 1 sin borrar ningún archivo — harness: `make_installed_env` con `.state.json` de contenido JSON inválido (ej. `"{"` ); assertir que los archivos del catálogo siguen presentes en `tmp_path` tras la llamada
- [x] 3.3 Crear `src/commands/uninstall.py` con `run_uninstall(dest_dir, state_path, tool_dir, wrapper_path, out, stdin) -> int`; implementar lectura de state con `read_state`: retornar 0 con mensaje `already_uninstalled` si no hay state, retornar 1 con el mensaje del error si hay `StateCorruptError`

## 4. Comando uninstall — confirmación interactiva

- [x] 4.1 Test: preview mostrada antes de pedir confirmación incluye recuento de archivos y rutas del tool dir y wrapper — harness: `make_installed_env`; `out = io.StringIO()`; `stdin = io.StringIO("n\n")`; llamar `run_uninstall` y assertir que `out.getvalue()` contiene el recuento y las rutas antes de cancelar
- [x] 4.2 Test: si el usuario no confirma, `run_uninstall` retorna exit code 2 sin borrar ningún archivo — harness: igual que 4.1; assertir código de retorno 2 y que los archivos del catálogo siguen en disco
- [x] 4.3 Implementar lógica de preview y confirmación en `run_uninstall`: mostrar `render_uninstall_preview`, leer una línea de `stdin`, retornar 2 con mensaje `uninstall_cancelled` si la respuesta no es `s` ni `S`

## 5. Comando uninstall — borrado de archivos del catálogo

- [x] 5.1 Test: tras confirmación, `run_uninstall` borra todos los archivos listados en `installed_files` — harness: `make_installed_env`; `stdin = io.StringIO("s\n")`; assertir que cada ruta de `installed_files` ya no existe en disco tras la llamada
- [x] 5.2 Test: `run_uninstall` omite sin error archivos ya ausentes del disco — harness: `make_installed_env`; borrar manualmente uno de los archivos antes de llamar a `run_uninstall`; assertir que la llamada retorna exit code 0
- [x] 5.3 Implementar borrado de archivos del catálogo en `run_uninstall`: iterar `installed_files`, llamar `unlink(missing_ok=True)` en cada ruta; capturar `PermissionError` por archivo y acumular en lista de fallidos

## 6. Comando uninstall — limpieza de directorios vacíos

- [x] 6.1 Test: tras el borrado, `run_uninstall` elimina directorios vacíos que eran padre de archivos en `installed_files` — harness: `make_installed_env` con archivos bajo un subdirectorio propio (ej. `dest_dir/commands/from-scratch/sync-skills.md`); tras confirmar, assertir que `dest_dir/commands/from-scratch/` ya no existe
- [x] 6.2 Test: `run_uninstall` no borra directorios que contienen archivos que from-scratch no instaló — harness: `make_installed_env`; crear un archivo extra bajo el mismo subdirectorio que no figure en `installed_files`; tras confirmar, assertir que el directorio sigue existiendo
- [x] 6.3 Test: `run_uninstall` no borra directorios que no son padre de ninguna ruta en `installed_files` — harness: `make_installed_env`; crear un subdirectorio separado bajo `dest_dir` que from-scratch no usó; tras confirmar, assertir que ese subdirectorio sigue existiendo
- [x] 6.4 Implementar limpieza de directorios vacíos en `run_uninstall`: recolectar los directorios padre de rutas en `installed_files`; iterar de hoja a raíz; borrar solo los que quedaron vacíos y que no sean `dest_dir`

## 7. Comando uninstall — borrado del state dir, tool dir y wrapper

- [x] 7.1 Test: `run_uninstall` borra el state dir tras el borrado de archivos — harness: `make_installed_env`; `stdin = io.StringIO("s\n")`; assertir que `state_path.parent` ya no existe tras la llamada
- [x] 7.2 Test: `run_uninstall` borra el tool dir y el wrapper — harness: `make_installed_env`; crear `tool_dir` y `wrapper_path` como rutas reales bajo `tmp_path`; tras confirmar, assertir que ambas rutas ya no existen
- [x] 7.3 Test: un `PermissionError` al borrar un archivo no aborta el proceso y el archivo fallido se reporta en el output final — harness: `make_installed_env`; `monkeypatch.setattr` en `pathlib.Path.unlink` para lanzar `PermissionError` solo en la primera ruta de `installed_files`; assertir que el resto de archivos se borró y que `out.getvalue()` menciona la ruta fallida y contiene `sudo rm`
- [x] 7.4 Test: `run_uninstall` retorna exit code 1 cuando hubo al menos un elemento que no se pudo borrar — harness: mismo setup de 7.3; assertir código de retorno 1
- [x] 7.5 Test: `run_uninstall` retorna exit code 0 y el output incluye "from-scratch init" tras borrado completo exitoso — harness: `make_installed_env` completo; `stdin = io.StringIO("s\n")`; assertir código 0 y que `out.getvalue()` contiene la frase del hint
- [x] 7.6 Implementar borrado del state dir (`shutil.rmtree`), tool dir y wrapper en `run_uninstall`; capturar `PermissionError` para cada uno y acumularlo en la lista de fallidos; al final: si hay fallidos retornar 1 con lista de remediaciones, si no retornar 0 con mensaje `uninstall_success`

## 8. Integración en el CLI

- [x] 8.1 Test: `main(["uninstall"])` despacha a `run_uninstall` — harness: `monkeypatch.setattr` en `src.commands.uninstall.run_uninstall` para capturar la llamada; assertir que fue invocado exactamente una vez con los argumentos esperados
- [x] 8.2 Agregar `"uninstall"` a `SUBCOMMANDS` en `src/cli.py`
- [x] 8.3 Registrar subparser `uninstall` en `_build_parser()` (sin flags adicionales)
- [x] 8.4 Agregar rama `if parsed.subcommand == "uninstall"` en `main()`

## 9. Test de aceptación end-to-end

- [x] 9.1 Test de aceptación: flujo completo — init simulado seguido de uninstall confirma y deja el entorno limpio — harness: `make_installed_env` con state + archivos reales bajo `tmp_path`; crear también `tool_dir` y `wrapper_path` como rutas reales; llamar `run_uninstall` con `stdin = io.StringIO("s\n")` y `out = io.StringIO()`; assertir: código de retorno 0, todos los archivos del catálogo ausentes, state dir ausente, tool dir ausente, wrapper ausente, y `out.getvalue()` contiene el hint de re-instalación

## 10. Verificación final

- [x] 10.1 Correr suite completa `python -m pytest` — todos los tests pasan

## Verificación humana (no cuenta como cobertura automatizada)

- [x] H.1 Smoke test manual: `from-scratch init` seguido de `from-scratch uninstall` en un equipo real; verificar que el entorno queda limpio y que el wrapper ya no es accesible en `$PATH`
