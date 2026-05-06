## 1. Preparación y registro en el catálogo

- [x] 1.1 Leer los 3 prompts de inicialización del repositorio `despegar/agent-rules-and-skills` para entender el contrato exacto de cada uno (bootstrap, sin test)
- [x] 1.2 Escribir test que verifica que `catalog/catalog.json` registra una entrada para `commands/from-scratch/sync-skills.md` con el slug `from-scratch:sync-skills`. Harness: `json.loads(Path("catalog/catalog.json").read_text())` y assert sobre la estructura (la entrada existe, el path apunta al subdirectorio correcto, el slug tiene el prefijo de namespace)
- [x] 1.3 Registrar `commands/from-scratch/sync-skills.md` en `catalog/catalog.json` para que pase el test de 1.2 (el archivo de prompt todavía no existe; ese caso lo cubre 2.1)
- [x] 1.4 Escribir test que verifica que el archivo `catalog/commands/from-scratch/sync-skills.md` existe y tiene frontmatter YAML válido con campos `description` no vacío. Harness: `Path(...).exists()` + parseo de frontmatter usando el parser ya presente en `tests/catalog/test_yaml_parser.py`
- [x] 1.5 Escribir test que verifica que el cuerpo del prompt de `sync-skills.md` referencia los 3 prompts de `agent-rules-and-skills` en orden (análisis del proyecto, sync de skills, generación de skills customizados). Harness: `read_text()` + búsqueda de los tres marcadores y comparación de índices ascendentes

## 2. Nuevo comando sync-skills: ejecución de los 3 prompts

- [x] 2.1 Crear `catalog/commands/from-scratch/sync-skills.md` con frontmatter válido y un cuerpo mínimo que referencia los 3 prompts en orden, suficiente para que pasen los tests de 1.4 y 1.5
- [x] 2.2 Escribir test que verifica que el prompt de `sync-skills.md` declara explícitamente cómo se comporta el Prompt 3 cuando el proyecto no tiene historia suficiente: el prompt instruye a Claude a ejecutarlo igualmente y reportar advertencia si el output es pobre, en vez de saltearlo silenciosamente. Harness: assert sobre substrings que indican el manejo del caso (ej. "advertencia", "historia insuficiente" o equivalente declarado en design)
- [x] 2.3 Actualizar `sync-skills.md` para incluir el manejo del caso "proyecto sin historia suficiente"
- [x] 2.4 Escribir test que verifica que el prompt de `sync-skills.md` instruye a Claude a regenerar automáticamente la sección auto-managed de `CLAUDE.md` cuando `AGENTS.md` cambió, sin pedir confirmación, y reportar la regeneración en el resumen de cierre (D9). Harness: assert que el prompt declara la regeneración condicional al cambio en AGENTS.md y que NO menciona pedir confirmación al usuario para esa regeneración
- [x] 2.5 Actualizar `sync-skills.md` para incluir la regeneración automática de la sección auto-managed de `CLAUDE.md` cuando `AGENTS.md` cambia
- [x] 2.6 Escribir test que verifica que el prompt de `sync-skills.md` instruye a Claude a abrir un TodoWrite al inicio del flujo enumerando los pasos (análisis del proyecto, sync de skills compartidos, generación de skills customizados, actualización de AGENTS.md, regeneración de CLAUDE.md cuando aplique) y actualizarlo a medida que avanza (D12). Harness: assert sobre substring que mencione TodoWrite y los ítems de la lista
- [x] 2.7 Actualizar `sync-skills.md` para incluir la instrucción de TodoWrite con los pasos del flujo

## 3. Extensión de new-project

- [x] 3.1 Escribir test que verifica que el prompt de `new-project.md` instruye a Claude a abrir un TodoWrite al inicio del flujo que enumera los pasos: clone del template, skills sync, `.claude/settings.json`, generación de `CLAUDE.md`. Harness: `read_text()` + assert sobre substrings que mencionen TodoWrite y los 4 pasos
- [x] 3.2 Actualizar `catalog/commands/new-project.md` para incluir la instrucción de TodoWrite con los 4 pasos al inicio del flujo
- [x] 3.3 Escribir test que verifica que `new-project.md` declara el paso de skills sync post-configuración del template, referenciando los Prompts 1 y 2 de `agent-rules-and-skills` (Prompt 3 explícitamente excluido por D2). Harness: assert sobre substrings y verificación de orden (skills sync aparece después del paso de configuración del template)
- [x] 3.4 Actualizar `new-project.md` para incluir el paso de skills sync con Prompts 1+2 en el lugar correcto del flujo
- [x] 3.5 Escribir test que verifica que `new-project.md` declara el paso de creación o merge de `.claude/settings.json` con permisos base: si el template ya trae uno, hace merge JSON (agrega keys nuevas, preserva las existentes), y solo pide confirmación cuando hay conflicto real (misma key, valor distinto). Harness: assert sobre substrings (`.claude/settings.json`, "merge", "permisos", "conflicto" o equivalente)
- [x] 3.6 Actualizar `new-project.md` para incluir el paso de `.claude/settings.json` con la lógica de merge
- [x] 3.7 Escribir test que verifica que `new-project.md` declara el paso de generación de `CLAUDE.md` con instrucción explícita de referenciar `AGENTS.md`, que ese paso aparece **después** del skills sync (D2), y que la sección auto-managed se genera envuelta en marcadores HTML (`<!-- AUTO-GENERATED: claude-init-start -->` … `<!-- AUTO-GENERATED: claude-init-end -->`) para soportar merge en re-syncs futuros. Harness: assert sobre substrings + verificación de orden de índices + assert sobre los marcadores
- [x] 3.8 Actualizar `new-project.md` para incluir el paso de generación de `CLAUDE.md` en el orden correcto y con los marcadores
- [x] 3.9 Escribir test que verifica el manejo de fallo del skills sync: el prompt instruye a continuar con los pasos restantes (settings.json + CLAUDE.md) y a reportar el error al usuario en vez de abortar. Harness: assert sobre substrings que describan el comportamiento ("continuar", "reportar el error", "no abortar" o equivalente)
- [x] 3.10 Actualizar `new-project.md` para incluir el manejo de fallo del skills sync

## 4. UX: feedback, errores y resumen final

- [x] 4.1 Escribir tests que verifican que el prompt de `new-project.md` instruye a Claude a anunciar el inicio y resultado de cada operación larga (clone de template, clone de agent-rules-and-skills, análisis del proyecto, copia de skills, generación de CLAUDE.md)
- [x] 4.2 Actualizar el prompt de `new-project.md` para incluir esas instrucciones de feedback en chat (además del TodoWrite)
- [x] 4.3 Escribir tests que verifican que el prompt define el formato de errores accionables: cada error reporta qué falló, por qué, y qué comando ejecutar para recuperar
- [x] 4.4 Actualizar el prompt para incluir el formato de errores y cubrir los casos enumerados en design U3 (repo inaccesible, AGENTS.md con edits locales, settings.json colisión, Prompt 3 sin codebase)
- [x] 4.5 Escribir tests que verifican que el prompt instruye a Claude a mostrar un resumen final al cierre de `new-project` con: ruta del proyecto, cantidad de skills instalados, archivos generados, advertencias por pasos incompletos, y hint sobre `/from-scratch:sync-skills`
- [x] 4.6 Actualizar el prompt de `new-project.md` para incluir el bloque de cierre con el resumen y el hint
- [x] 4.7 Escribir el test equivalente para `sync-skills.md`: el prompt instruye a Claude a mostrar al cierre el delta de skills (counts + nombres por categoría: agregados/removidos/actualizados/preservados según D10) y, si AGENTS.md cambió y por lo tanto CLAUDE.md también fue regenerado (D9), reportarlo en el resumen
- [x] 4.8 Actualizar el prompt de `sync-skills.md` para incluir el bloque de delta con el formato counts+nombres y el reporte de regeneración de CLAUDE.md cuando aplique

## 5. UX: confirmaciones, idempotencia y cancelación segura

- [x] 5.1 Escribir tests que verifican que el prompt de `sync-skills.md` instruye a mostrar preview con el formato counts + nombres por categoría (added/updated/removed/preserved) y pedir confirmación antes de aplicar cambios cuando ya existe `.claude/skills/` o `AGENTS.md`. Harness: assert sobre substrings que indiquen el formato del preview y la lógica condicional de confirmación
- [x] 5.2 Actualizar el prompt de `sync-skills.md` para incluir el preview con formato D10 y la confirmación condicional según U2
- [x] 5.3 Escribir test que verifica que ambos prompts instruyen a hacer **merge** (no overwrite) sobre `AGENTS.md` y `CLAUDE.md` usando los marcadores HTML (`<!-- AUTO-GENERATED: ...-start -->` / `<!-- AUTO-GENERATED: ...-end -->`) para regenerar solo la sección auto-managed y preservar el contenido escrito a mano por el usuario. Caso edge: si el archivo existe pero no tiene los marcadores (proyecto antiguo), el prompt instruye a pedir confirmación e insertar los marcadores envolviendo el contenido auto-generado
- [x] 5.4 Actualizar `new-project.md` y `sync-skills.md` para incluir el patrón de merge con marcadores HTML y el manejo del caso "archivo sin marcadores"
- [x] 5.5 Escribir tests que verifican que ambos prompts (`new-project.md`, `sync-skills.md`) declaran escrituras atómicas para `AGENTS.md`, `CLAUDE.md` y `.claude/settings.json` (escribir a temp file en el mismo directorio, renombrar al destino al final) y copia de skills a directorio temporal con promoción al final
- [x] 5.6 Actualizar los prompts para incluir las instrucciones de escritura atómica
- [x] 5.7 Escribir tests que verifican que `sync-skills.md` instruye a detectar estado parcial de una corrida previa (ej. skills copiados sin AGENTS.md, AGENTS.md sin CLAUDE.md actualizado) y completar el flujo sin pedir intervención manual cuando es seguro
- [x] 5.8 Actualizar `sync-skills.md` para incluir la detección de estado parcial
- [x] 5.9 Escribir test que verifica que `new-project.md` instruye a fallar temprano si el directorio destino ya existe, sin destruir el proyecto previo
- [x] 5.10 Actualizar `new-project.md` para incluir el chequeo previo del directorio

- [x] 5.11 Escribir test que verifica que el prompt de `new-project.md` instruye a Claude a (a) incluir un bloque educativo sobre `.claude/settings.json` en el mensaje de cierre del flujo (qué es, por qué afecta la velocidad, ejemplo concreto de cómo agregar un comando, lista de qué NO pre-aprobar), y (b) escribir el mismo contenido como subsección dentro de la sección auto-managed de `CLAUDE.md`. Harness: `read_text()` + asserts sobre marcadores que identifiquen el bloque educativo y los 4 puntos requeridos por D11
- [x] 5.12 Actualizar `new-project.md` para incluir la doble emisión del bloque educativo (cierre + CLAUDE.md) según D11

## 6. Postura del prompt y referencias externas

- [x] 6.1 Escribir test que verifica que ambos prompts (`new-project.md`, `sync-skills.md`) declaran un bloque de restricciones globales (atomic writes, preview antes de mutar, formato de errores, no avanzar ante ambigüedad) **una sola vez**, no repetido por paso, y que cada paso describe estado final esperado en vez de secuencia de tool calls
- [x] 6.2 Refactorizar los prompts de `new-project.md` y `sync-skills.md` para cumplir D6: factorizar las restricciones globales a un bloque único y reescribir cada paso como objetivo (estado final), no como procedimiento
- [x] 6.3 Escribir test que verifica que ningún prompt contiene pseudo-código de control de flujo (if/else, for, while) ni re-explica cómo usar TodoWrite o tools nativas
- [x] 6.4 Ajustar los prompts para eliminar pseudo-código y re-explicaciones de tools nativas
- [x] 6.5 Escribir test que verifica que el cuerpo de cada prompt (sin frontmatter) no excede ~150 líneas de contenido sustantivo
- [x] 6.6 Si algún prompt excede el límite, factorizar las partes redundantes o moverlas a referencias externas

- [x] 6.7 Escribir test que verifica que los prompts referencian `despegar/agent-rules-and-skills` con un ref pinneado (tag o commit SHA) visible en el cuerpo del prompt, no `main`
- [x] 6.8 Actualizar los prompts para incluir el ref pinneado del repo de skills y documentar dónde editar el ref cuando se quiera adoptar una versión nueva
- [x] 6.9 Escribir test que verifica que los prompts instruyen a Claude a leer los 3 prompts del repo en runtime (no embeberlos), siguiendo D1
- [x] 6.10 Asegurarse de que el prompt declara la URL+ref como única fuente de verdad y que los pasos del flujo se describen en términos del objetivo de cada prompt remoto, no de su contenido

- [x] 6.11 Escribir test que verifica que `sync-skills.md` instruye a Claude a detectar skills user-installed (presentes en `.claude/skills/` pero ausentes del manifest upstream) y a listarlos en el preview en categoría "preservados sin cambios"
- [x] 6.12 Actualizar `sync-skills.md` para incluir la lógica de detección y preservación de skills user-installed (D8)

## 7. Modos de falla ecosistema-específicos

- [x] 7.1 Escribir test que verifica que `sync-skills.md` instruye a abortar temprano con error accionable cuando se invoca fuera de un proyecto (no `.git`, no marcadores de stack, no `AGENTS.md`)
- [x] 7.2 Actualizar `sync-skills.md` para incluir la detección de "no estoy en un proyecto" y el error correspondiente
- [x] 7.3 Escribir test que verifica que `sync-skills.md` reporta skills con frontmatter inválido en una categoría separada del preview ("ignorados por frontmatter inválido") y continúa el sync con el resto
- [x] 7.4 Actualizar `sync-skills.md` para incluir el manejo de frontmatter inválido en skills preexistentes
- [x] 7.5 Escribir test que verifica que `sync-skills.md` documenta la versión mínima de `from-scratch` requerida (la primera que conoce el subdir `commands/from-scratch/`) y describe cómo recuperarse si el binario es viejo
- [x] 7.6 Agregar la nota de versión mínima al prompt de `sync-skills.md`

## 8. Integración y aceptación automatizada

- [x] 8.1 Escribir test de aceptación end-to-end del catálogo: ejecutar `from-scratch init` apuntando a un `HOME` temporal (`tmp_path` como fixture pytest, env var `HOME`/`CLAUDE_HOME` redirigido) y verificar que el archivo `~/.claude/commands/from-scratch/sync-skills.md` queda instalado con frontmatter válido. Harness: `subprocess.run([sys.executable, "-m", "cli", "init"], env={..., "HOME": str(tmp_path)})` + checks sobre el filesystem
- [x] 8.2 Escribir test de aceptación end-to-end de contenido: leer el `sync-skills.md` instalado en 8.1 y validar que cumple simultáneamente el contrato del prompt declarado en design (rol al inicio, bloque de restricciones globales una sola vez, ref pinneado visible, bloque de cierre con resumen). Harness: `read_text()` + asserts sobre las marcas estructurales del prompt
- [x] 8.3 Escribir test de aceptación end-to-end para `new-project.md`: verificar que el prompt instalado tras `from-scratch init` declara los 4 pasos del flujo extendido en orden (template → skills sync → settings.json → CLAUDE.md) y referencia el ref pinneado del repo de skills. Harness: igual que 8.1+8.2 pero contra `~/.claude/commands/new-project.md`
- [x] 8.4 Correr el test suite completo (`python -m pytest`) y verificar que no hay regresiones

## 9. Verificación humana (no automatizable, fuera del recuento de cobertura)

Estos pasos requieren ejecutar Claude Code interactivamente. No son tests automatizables y se documentan acá para que un humano los corra antes del release. No cuentan como cobertura de las features.

- [ ] 9.1 Ejecutar `/new-project` con el stack Java y verificar visualmente que aparece el TodoWrite con todos los pasos, incluyendo los nuevos
- [ ] 9.2 Validar el flujo de cancelación: invocar `/new-project`, interrumpir durante la copia de skills, y verificar que `AGENTS.md` y `CLAUDE.md` no quedan a medio escribir
- [ ] 9.3 Validar idempotencia: correr `/from-scratch:sync-skills` dos veces seguidas en el mismo proyecto y verificar que la segunda corrida reporta "no hay cambios" sin reescribir archivos
- [ ] 9.4 Validar que invocar `/from-scratch:sync-skills` desde un directorio que no es proyecto aborta con el error accionable definido en 7.1
