## 1. Setup del repositorio y toolchain

- [x] 1.1 Inicializar `package.json` con metadata del paquete (nombre `from-scratch`, bin entry, type `module`).
- [x] 1.2 Configurar TypeScript (`tsconfig.json`) con target/module modernos y strict habilitado.
- [x] 1.3 Agregar dependencias mínimas: `@clack/prompts`, runtime utils que sean indispensables.
- [x] 1.4 Configurar build script que compile a un único entrypoint ejecutable (con shebang `#!/usr/bin/env node`).
- [x] 1.5 Configurar `package.json` para que `npm i -g github:dimartinez/from-scratch` instale el binario y deje el ejecutable accesible globalmente.
- [x] 1.6 Configurar framework de testing (Vitest o Node test runner) y un primer test que pase, para validar el setup TDD.
- [x] 1.7 Crear estructura de carpetas: `src/`, `tests/`, `catalog/` (raíz del catálogo dentro del repo).

## 2. Estructura del catálogo en el repo

- [x] 2.1 Definir el layout del catálogo dentro del repo: subcarpeta `catalog/` con `commands/`, `stacks/`, y un manifest.
- [x] 2.2 Crear el archivo manifest del catálogo (`catalog/catalog.json` o equivalente) con la lista de archivos a sincronizar y el campo `requires_binary >= ...`.
- [x] 2.3 Documentar en el repo (README) cómo agregar un stack nuevo (poner archivo en `catalog/stacks/`, actualizar manifest si corresponde).
- [x] 2.4 Escribir test que verifique que cada entrada del manifest tiene un campo `kind` (string) y que los `kind` reconocidos en v1 son exactamente `command` y `stack`.
- [x] 2.5 Implementar el schema del manifest con `kind` y `source` por entrada.
- [x] 2.6 Escribir test que verifique que un manifest con un `kind` desconocido por el binario produce el mensaje de error "kind de artefacto desconocido" (texto exacto según `design.md`) y termina con código distinto de 0 sin tocar disco.
- [x] 2.7 Implementar la detección de `kind` desconocido y su mensaje accionable.

## 3. Núcleo de la CLI

- [x] 3.1 Escribir test que verifique que `from-scratch init` se reconoce como invocación al subcomando `init` (sin ejecutar todavía la lógica de init, solo el dispatch).
- [x] 3.2 Implementar el dispatch del subcomando `init`.
- [x] 3.3 Escribir test que verifique que `from-scratch update` se reconoce como invocación al subcomando `update`.
- [x] 3.4 Implementar el dispatch del subcomando `update`.
- [x] 3.5 Escribir test que verifique que `from-scratch` sin argumentos muestra el `--help` y termina con código 0 (no es error).
- [x] 3.6 Implementar el comportamiento "sin argumentos = help".
- [x] 3.7 Escribir test que verifique que un subcomando inválido (ej. `from-scratch lalala`) produce un mensaje que nombra el subcomando recibido, lista los subcomandos válidos, y sugiere `from-scratch --help`, terminando con código distinto de 0.
- [x] 3.8 Implementar el mensaje de subcomando inválido.
- [x] 3.9 Escribir test que verifique que `from-scratch --help` imprime al menos un ejemplo concreto de uso y los subcomandos disponibles.
- [x] 3.10 Escribir test que verifique que `from-scratch <subcomando> --help` imprime al menos un ejemplo concreto de uso del subcomando.
- [x] 3.11 Implementar los textos de `--help` general y por subcomando.
- [x] 3.12 Escribir test que verifique que la versión del binario se obtiene de `package.json` y se expone como dato consultable por el resto de la CLI.
- [x] 3.13 Implementar la lectura de versión.
- [x] 3.14 Escribir test que verifique el caso "binario suficiente": cuando la versión del binario es igual o mayor a la requerida por el catálogo, el handshake pasa silenciosamente.
- [x] 3.15 Escribir test que verifique el caso "binario insuficiente": cuando la versión del binario es menor a la requerida, el handshake se planta con el mensaje exacto definido en `design.md` (incluye versión actual, versión requerida y comando de upgrade) y termina con código distinto de 0 sin tocar disco.
- [x] 3.16 Escribir test del caso límite "versión exactamente igual a la requerida": el handshake pasa.
- [x] 3.17 Implementar el chequeo de versión y el mensaje de error con el comando exacto de upgrade.

## 4. Sincronización del catálogo (download y copia)

- [x] 4.1 Escribir tests (con mocks de red) para la descarga del manifest del catálogo desde GitHub.
- [x] 4.2 Implementar la descarga del manifest vía HTTP, sin requerir git.
- [x] 4.3 Escribir tests para la descarga de cada archivo listado en el manifest (happy path con varios archivos).
- [x] 4.4 Implementar la descarga de archivos.
- [x] 4.4.a Escribir test que verifique que, si un archivo del manifest devuelve 404 al descargarse, la CLI corta el flujo, NO escribe nada en disco y reporta qué archivo falló.
- [x] 4.4.b Implementar el manejo de 404 / error de descarga sobre archivos del catálogo.
- [x] 4.5 Escribir tests para la lógica de "destino correcto": entradas con `kind: command` van a `~/.claude/commands/` (zona Claude Code), entradas con `kind: stack` van a `~/.claude/from-scratch/stacks/` (zona interna).
- [x] 4.6 Implementar el mapeo `kind → destino` y la copia a disco.
- [x] 4.7 Escribir test que verifique que, antes de copiar un archivo a zona Claude Code (`~/.claude/commands/`), la CLI valida su frontmatter YAML; si el frontmatter es inválido, NO copia y reporta el error "frontmatter inválido en un comando del catálogo" (texto exacto según `design.md`).
- [x] 4.8 Implementar la validación de frontmatter previa a la copia, usando un parser YAML maduro.
- [x] 4.9 Escribir test que verifique que, al instalar un archivo en zona Claude Code, su path relativo a `~/.claude/` queda registrado en `installed_files` del state file.
- [x] 4.10 Implementar la actualización de `installed_files` durante la fase de copia.

## 5. Subcomando `init`

- [x] 5.1 Escribir test que verifique el esqueleto del flujo de `init`: ante invocación, la CLI dispara las fases en orden (descarga manifest → handshake → descarga archivos → copia → resumen) y produce un código de salida 0 cuando todas las fases (mockeadas) responden OK.
- [x] 5.2 Implementar el orquestador de `init` que encadena las fases, delegando cada una a su módulo correspondiente.
- [x] 5.3 Escribir test que verifique que, antes de la confirmación de `init`, la salida incluye la versión del catálogo, la lista de archivos a crear agrupada por destino, y un resumen contable (cantidad de archivos por destino).
- [x] 5.4 Implementar el preview pre-confirmación de `init`.
- [x] 5.5 Escribir test que verifique que la confirmación de `init` se le pregunta al usuario con la pregunta exacta `¿Instalar el catálogo en ~/.claude/?` y default sí.
- [x] 5.6 Implementar la confirmación de `init`.
- [x] 5.7 Escribir test que verifique que, si el usuario rechaza la confirmación, `init` no toca disco y termina con un mensaje de cancelación.
- [x] 5.8 Implementar la rama "usuario rechaza confirmación" en `init`.
- [x] 5.9 Escribir test que verifique que `init` ejecutado con instalación previa NO escribe archivos: solo imprime un mensaje sugiriendo `from-scratch update` y termina con código 0.
- [x] 5.10 Implementar la detección de instalación previa y el redireccionamiento a `update`.
- [x] 5.11 Escribir test que verifique que `init --force` con instalación previa muestra preview de qué se va a sobrescribir antes de pedir confirmación.
- [x] 5.12 Implementar el flag `--force` para `init`.
- [x] 5.13 Escribir test que verifique que, si en `~/.claude/commands/` ya existe un archivo con el mismo nombre que un command del catálogo y ese archivo NO figura en `installed_files`, `init` se planta con el mensaje "conflicto de nombre con archivo preexistente" y NO escribe en disco.
- [x] 5.14 Implementar la detección de conflicto y la negativa a sobreescribir archivos del usuario sin `--force`.
- [x] 5.15 Escribir test que verifique que `init --force` ante un conflicto crea un backup en `<archivo>.bak.<timestamp>` antes de pisar el archivo del usuario, y que el backup contiene exactamente el contenido previo.
- [x] 5.16 Implementar el respaldo `.bak.<timestamp>` previo a la sobreescritura forzada.
- [ ] 5.17 Escribir test que verifique que la CLI usa Clack para presentar el saludo inicial de `init` con un texto definido (no un `console.log` plano).
- [ ] 5.18 Escribir test que verifique que las confirmaciones y spinners de `init` se renderizan vía Clack (no vía prints sueltos).
- [ ] 5.19 Integrar `@clack/prompts` para saludo, confirmaciones y spinners de `init`.
- [x] 5.20 Escribir test que verifique que el resumen final de `init` incluye un "Próximo paso" con la indicación de reiniciar Claude Code y la mención del subcomando `update` para futuras sincronizaciones.
- [x] 5.21 Implementar el bloque de resumen final de `init`.
- [x] 5.22 Escribir test de aceptación end-to-end que ejercite el flujo completo de `init` con catálogo y filesystem mockeados, partiendo de un `~/.claude/` vacío y validando: preview mostrado, confirmación pedida, archivos escritos en sus zonas correctas, state file actualizado, resumen final con "Próximo paso".
- [x] 5.23 Escribir test de aceptación end-to-end de `init --force` sobre instalación previa con un conflicto: valida que se hace backup, se sobreescribe, y se reporta correctamente en el resumen.

## 6. Subcomando `update`

- [x] 6.1 Escribir test que verifique que el diff clasifica correctamente cada archivo del catálogo en una de las categorías `+` (nuevo), `~` (modificado), `=` (sin cambios) según el contenido remoto vs. local.
- [x] 6.2 Escribir test que verifique que el diff clasifica como `-` (eliminado) un archivo presente en `installed_files` que ya no aparece en el catálogo remoto.
- [x] 6.3 Implementar el cálculo del diff.
- [x] 6.4 Escribir test que verifique que el flujo de `update` pasa por las fases en orden: descarga manifest → handshake → cálculo de diff → mostrar diff → confirmación → aplicar.
- [x] 6.5 Implementar el orquestador de `update` integrando Clack para el rendering del diff y la confirmación.
- [x] 6.6 Escribir test que verifique que `update`, cuando el diff no tiene cambios, NO pide confirmación, NO toca disco e imprime el mensaje exacto `Tu catálogo está al día (vX.Y.Z).`.
- [x] 6.7 Implementar el caso "no hay cambios" en `update`.
- [x] 6.8 Escribir test de idempotencia que ejecute `update` dos veces seguidas sobre el mismo catálogo remoto sin cambios y verifique que la segunda ejecución no modifica ningún archivo, no actualiza `last_sync_completed_at` con valores distintos por escritura innecesaria, y no produce output de cambios.
- [x] 6.9 Implementar (si hace falta) los ajustes para garantizar idempotencia exacta.
- [x] 6.10 Escribir test que verifique que el render del diff usa los prefijos `+`, `~`, `-`, y que los archivos sin cambios se reportan solo como un total agregado, no listados uno por uno.
- [x] 6.11 Implementar el formato del diff según el contrato.
- [x] 6.12 Escribir test que verifique que el resumen final de `update` incluye conteo por categoría (instalados / actualizados / sin cambios) y un "Próximo paso" que pide reiniciar Claude Code cuando hubo cambios efectivos.
- [x] 6.13 Implementar el resumen final de `update`.
- [x] 6.14 Escribir test que verifique que, si `update` debe instalar un archivo nuevo en zona Claude Code y ya existe un archivo con ese nombre que NO figura en `installed_files`, la CLI muestra el conflicto en el diff con un símbolo distinto (`!`) y NO lo aplica sin `--force`.
- [x] 6.15 Escribir test que verifique que `update --force` ante un conflicto crea backup `.bak.<timestamp>` antes de pisar y luego aplica el cambio.
- [x] 6.16 Implementar el manejo de conflicto en `update` (símbolo `!`, exclusión del apply automático, respaldo `.bak.<timestamp>` cuando se fuerza).
- [x] 6.17 Escribir test que verifique que, si un archivo desapareció del catálogo y figura en `installed_files`, `update` lo elimina (símbolo `-`).
- [ ] 6.18 Escribir test que verifique que, si un path que estaba en `installed_files` desaparece del catálogo pero el archivo en disco fue reemplazado por contenido que NO instaló la CLI, `update` lo deja intacto y avisa con `Aviso:`.
- [x] 6.19 Implementar la lógica de borrado seguro: solo se borran paths que figuran en `installed_files`.
- [ ] 6.20 Escribir test de aceptación end-to-end de `update` que combine en una sola corrida: un archivo nuevo (`+`), uno modificado (`~`), uno eliminado (`-`), uno sin cambios (`=`) y un conflicto (`!`); validar el render del diff, la confirmación, la aplicación selectiva y el resumen final.

## 7. Primer contenido del catálogo

- [x] 7.1 Escribir test que verifique que `catalog/commands/new-project.md` tiene un frontmatter YAML parseable con al menos el campo `description`, y que la `description` no es vacía y entra en una sola línea.
- [x] 7.2 Escribir test (revisión textual sobre el cuerpo del prompt) que verifique que el prompt: (a) declara explícitamente el rol que Claude debe adoptar, (b) declara el objetivo final (proyecto listo para usar), (c) declara las restricciones explícitas (no avanzar ante ambigüedad sin preguntar, no inventar pasos no declarados en el README del template, validar coherencia entre README y código del template), (d) NO scriptea pasos imperativos numerados que el modelo deba seguir al pie de la letra.
- [x] 7.3 Escribir test que verifique que el prompt instruye explícitamente a Claude a leer los stacks desde `~/.claude/from-scratch/stacks/` y a presentar `name` + `description` al usuario.
- [x] 7.4 Crear `catalog/commands/new-project.md` con frontmatter YAML idiomático (al menos `description` con la línea visible en el menú de `/`) y, en el cuerpo markdown, el rol de "desarrollador senior" y el flujo descrito en el spec de `new-project-command`, hasta que los tests 7.1, 7.2 y 7.3 pasen.
- [x] 7.5 Escribir test que verifique que un archivo de stack con frontmatter YAML válido y los tres campos `name`, `description`, `template_url` se parsea correctamente y devuelve esos tres campos.
- [x] 7.6 Escribir test que verifique que un stack sin alguno de los tres campos requeridos es rechazado con el mensaje de error documentado en `design.md` ("UX de la CLI" → "Archivo de stack inválido").
- [x] 7.7 Escribir test del caso límite "frontmatter YAML mal formado" (sintaxis inválida): el parser falla con el mismo mensaje de error documentado.
- [x] 7.8 Implementar el parser de stack basado en frontmatter YAML.
- [x] 7.9 Escribir test que verifique que `catalog/stacks/java.md` se parsea correctamente y devuelve `name: "Java (Despegar)"`, `description: "Microservicio Java estándar Despegar"`, `template_url: "github.com/despegar/java-template"`.
- [x] 7.10 Crear `catalog/stacks/java.md` con frontmatter YAML que declare `name: "Java (Despegar)"`, `description: "Microservicio Java estándar Despegar"`, `template_url: "github.com/despegar/java-template"`, hasta que el test 7.9 pase. El cuerpo markdown queda libre (puede estar vacío o contener notas humanas opcionales).
- [x] 7.11 Documentar el contrato del archivo de stack en el README del repo, mostrando el frontmatter mínimo y los campos disponibles. (Decisión 10 del design — formato es frontmatter YAML.)
- [ ] 7.12 Validar manualmente el flujo end-to-end: `npm i -g github:...` → `from-scratch init` → reiniciar Claude Code → `/new-project` → elegir Java → proyecto creado.

## 8. Mensajería de errores y rutas no felices

- [x] 8.1 Escribir test para el mensaje de error "red caída / GitHub inaccesible": se simula fallo de fetch del manifest y se verifica que la salida contiene las tres piezas (qué falló, causa probable, comando concreto de remediación) según la plantilla de `design.md`.
- [x] 8.2 Implementar el manejo y mensaje de error de red caída.
- [x] 8.3 Escribir test para el mensaje de error "manifest inválido": se sirve un manifest no parseable y se verifica que la salida contiene las tres piezas según la plantilla.
- [x] 8.4 Implementar el manejo y mensaje de error de manifest inválido.
- [x] 8.5 Escribir test para el mensaje de error "permisos sobre `~/.claude/`": se simula un EACCES al escribir y se verifica que la salida contiene las tres piezas según la plantilla.
- [x] 8.6 Implementar el manejo y mensaje de error de permisos.
- [x] 8.7 Escribir test para el mensaje de error "archivo de stack inválido" (al sincronizar): se sirve un stack sin un campo requerido y se verifica que la salida contiene las tres piezas según la plantilla y que el resto del catálogo se sincroniza igual.
- [x] 8.8 Implementar el manejo y mensaje de error de stack inválido.
- [x] 8.9 Escribir test para el mensaje de error "frontmatter inválido en un comando del catálogo": se sirve un command con YAML inválido y se verifica que la salida contiene las tres piezas según la plantilla y que NO se copia ese archivo a disco.
- [x] 8.10 Implementar el manejo y mensaje de error de frontmatter inválido.
- [x] 8.11 Escribir test que verifique el mensaje de error del handshake de versión (referencia cruzada con sección 3): contiene las tres piezas según la plantilla.
- [x] 8.12 Escribir test que verifique el mensaje de error de "conflicto de nombre con archivo preexistente del usuario" (referencia cruzada con sección 5): contiene las tres piezas según la plantilla.
- [x] 8.13 Escribir test que verifique el mensaje de error de "`kind` de artefacto desconocido" (referencia cruzada con sección 2): contiene las tres piezas según la plantilla.
- [ ] 8.14 Escribir test que verifique que, ante una falla a mitad de la fase de copia, la CLI deja un mensaje al usuario explicando el estado parcial y NO termina silenciosamente.
- [x] 8.15 Implementar la garantía de "ningún error deja `~/.claude/` en estado parcial sin avisar".
- [x] 8.16 Escribir test que verifique que los errores se imprimen con el prefijo `Error:` en color rojo.
- [x] 8.17 Escribir test que verifique que los warnings no bloqueantes se imprimen con el prefijo `Aviso:` en color amarillo.
- [x] 8.18 Implementar el formato visual de errores y avisos.

## 11. Atomicidad, cancelación segura y recuperación

- [x] 11.1 Escribir test que verifique que las escrituras a disco se hacen primero a `<destino>.tmp` y solo se renombran al destino final cuando la escritura termina sin errores.
- [x] 11.2 Implementar la escritura atómica (`.tmp` + `rename`).
- [ ] 11.3 Escribir test que simule un Ctrl+C antes del primer `rename` y verifique que (a) no quedan archivos `.tmp` huérfanos en `~/.claude/`, (b) ningún archivo de destino fue modificado, (c) la CLI imprime el mensaje "Cancelado. No se modificó ningún archivo de tu catálogo.".
- [x] 11.4 Implementar el handler de SIGINT que limpia `.tmp` y reporta cancelación.
- [x] 11.5 Escribir test que verifique que la CLI escribe `~/.claude/from-scratch/.state.json` con `last_sync_started_at` antes de tocar archivos y `last_sync_completed_at` solo cuando todo terminó OK, y que el state incluye los campos `installed_files` (array de paths relativos a `~/.claude/`), `catalog_version` y `binary_version`.
- [x] 11.6 Implementar la lectura/escritura del state file alrededor del flujo de sync, incluyendo la actualización de `installed_files`, `catalog_version` y `binary_version`.
- [x] 11.7 Escribir test que verifique que, si al arrancar `from-scratch` el state file tiene `started > completed`, la CLI avisa "Detecté una sincronización anterior interrumpida. Voy a reanudarla." y sigue con un flujo equivalente a `update`.
- [x] 11.8 Implementar la detección de estado parcial y la reanudación.

## 12. Feedback visual y output consistente

- [ ] 12.1 Escribir test que verifique que cada operación que excede ~1s (descarga de manifest, descarga de archivos, copia a disco, cálculo de diff) muestra un spinner con el texto definido en `design.md` y lo reemplaza por una línea de éxito al terminar.
- [ ] 12.2 Implementar los spinners y sus mensajes según el contrato.
- [x] 12.3 Escribir test que verifique que el output de los subcomandos NO contiene emojis.
- [x] 12.4 Asegurar (vía linter de strings o assertions) que el output respeta la regla de "sin emojis".
- [x] 12.5 Escribir test que verifique que cada subcomando exitoso termina con un bloque "Resumen" con la forma definida en `design.md` y un "Próximo paso" no vacío.
- [x] 12.6 Implementar el helper que renderiza Resumen + Próximo paso, y usarlo desde `init` y `update`.

## 13. Documentación

- [x] 13.1 Escribir README del repo con: qué es `from-scratch`, cómo se instala, cómo se usa, cómo se actualiza, cómo se agregan stacks.
- [x] 13.2 Documentar el contrato del archivo de stack y el contrato de los slash commands instalados.
- [x] 13.3 Documentar la política de versionado y el handshake.

## 14. Validación final con revisores

- [ ] 14.1 Compartir los artefactos OpenSpec (proposal, design, specs, tasks) con el revisor de UX y aplicar feedback antes de implementar.
- [ ] 14.2 Compartir los artefactos con el revisor de IA (especialmente `new-project-command/spec.md` y la sección de delegación con rol) y aplicar feedback.
- [ ] 14.3 Revisar y resolver las "Open Questions" listadas en `design.md` antes de cerrar el change.
