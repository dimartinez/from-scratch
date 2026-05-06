## Context

`/new-project` es un slash command de Claude Code (un archivo `.md` con un prompt en lenguaje natural) distribuido por `from-scratch init` a `~/.claude/commands/`. Actualmente el comando crea y configura el proyecto desde un template, pero no realiza ninguna configuración de Claude Code sobre el proyecto resultante.

El repositorio `despegar/agent-rules-and-skills` define tres prompts de inicialización de skills: análisis del proyecto, sync de skills compartidos (generando `AGENTS.md`), y generación de skills customizados desde el codebase. La integración debe invocar estos prompts en orden durante la creación del proyecto.

La restricción principal es que todo ocurre dentro de una conversación de Claude Code: no hay un binario externo que orqueste los pasos — el prompt del slash command le instruye a Claude qué hacer y en qué orden.

## Goals / Non-Goals

**Goals:**
- El flujo de `/new-project` deja el proyecto con skills instalados, `AGENTS.md` y `CLAUDE.md` generados, y `.claude/settings.json` configurado.
- El usuario ve el progreso completo vía TodoWrite sin necesidad de saber qué es `agent-rules-and-skills`.
- El nuevo slash command `/from-scratch:sync-skills` permite re-sincronizar skills en proyectos existentes.
- El comando sync-skills es distribuido por `from-scratch` junto con el resto del catálogo.

**Non-Goals:**
- No se modifica el CLI Python (`from-scratch init/update`).
- No se instala `agent-rules-and-skills` globalmente en la máquina del usuario.
- No se genera el Prompt 3 (skills customizados desde el codebase) durante `new-project`: el proyecto recién clonado no tiene historia suficiente.

## Decisions

**D1: Los prompts de `agent-rules-and-skills` se referencian por URL+ref pinneada, y Claude los lee en tiempo de ejecución.**

El slash command es un archivo markdown con instrucciones para Claude. Claude Code no tiene un mecanismo nativo para que un slash command invoque a otro. Hay dos alternativas:

- **Embeber** los 3 prompts dentro de `new-project.md` y `sync-skills.md`. Ventaja: el prompt es self-contained y no depende de red durante la corrida. Desventaja: acopla versiones, duplica el contenido en dos archivos del catálogo, y obliga a re-publicar el binario cada vez que `agent-rules-and-skills` cambie.
- **Referenciar** los prompts por URL del repo `despegar/agent-rules-and-skills` apuntando a un commit/tag pinneado. Claude los lee con la herramienta de fetch al ejecutarse. Ventaja: una sola fuente de verdad; el catálogo no se desactualiza. Desventaja: depende de red en runtime.

Elegimos referenciar con pin: el prompt declara la URL del repo y un ref específico (tag o commit SHA), y le instruye a Claude a leer los 3 prompts de allí. Si la red falla, el flujo cae al manejo de error de U3 ("repo de skills inaccesible"). El ref pinneado se actualiza editando el catálogo y publicando una nueva versión del binario, lo cual da control sobre cuándo adoptar cambios upstream.

**D2: El orden de los pasos es: setup del template → skills sync (Prompts 1+2) → Claude Code setup (settings.json + `/init`).**

El skills sync genera `AGENTS.md`. El paso `/init` debe correr después para poder leer `AGENTS.md` y referenciarlo en `CLAUDE.md`. Invertir el orden produciría un `CLAUDE.md` incompleto.

**D3: `/init` es guiado, no libre, y se ejecuta en línea — no se invoca como sub-comando.**

Claude Code no soporta que un slash command tipee `/init` para que el harness lo despache. En su lugar, el prompt de `new-project.md` describe en línea el comportamiento equivalente al `/init` built-in (analizar el codebase, generar `CLAUDE.md`) y agrega la instrucción explícita de buscar `AGENTS.md` y referenciarlo. El prompt deja claro que `/init` se nombra como referencia conceptual del comportamiento esperado, no como invocación literal. Sin esta guía, Claude generaría un `CLAUDE.md` que ignora los skills instalados.

**D4: El nuevo comando se llama `from-scratch:sync-skills` (con prefijo de namespace).**

Los comandos con prefijo `from-scratch:` son descubribles juntos en la lista de slash commands. El usuario que no conoce el comando lo encuentra junto a `/from-scratch:new-project` (si en algún momento se renombra) o lo recuerda por el prefijo del ecosistema.

**D5: `sync-skills` ejecuta los 3 Prompts de `agent-rules-and-skills`, incluyendo el Prompt 3.**

A diferencia de `new-project` (donde el proyecto recién clonado no tiene historia), `sync-skills` se usa sobre proyectos en evolución. El Prompt 3 genera skills customizados desde el codebase real, que es exactamente el caso de uso.

**D6: Postura del prompt: razonador, no script.**

El prompt existente de `new-project.md` declara "No seguís pasos mecánicos — leés el README del template y tomás las decisiones correctas para ese contexto específico". Esa misma postura SHALL preservarse cuando se agregan los nuevos pasos. Concretamente:

- El prompt enuncia el **objetivo** de cada paso (qué tiene que ser cierto al terminar) y las **restricciones** (qué no debe hacer), pero no describe la secuencia interna de tool calls.
- Las invariantes de comportamiento (atomic writes, preview antes de tocar disco, formato de errores accionables) se declaran una vez como restricciones globales del flujo, no se repiten en cada paso.
- El prompt referencia las herramientas que Claude ya conoce (`TodoWrite`, lectura/escritura de archivos, ejecución de `git`) sin re-explicar cómo usarlas.
- El prompt es legible de corrido por un humano: si la lista de "instrucciones a incluir" excede ~150 líneas, es señal de que se está scripteando en vez de declarar contrato. En ese caso se factoriza en restricciones globales o se mueve a `agent-rules-and-skills`.

Esta decisión es la barandilla contra el riesgo de que el prompt degenere en un checklist rígido a medida que se agregan capacidades.

**D7: Versionado pinneado de `agent-rules-and-skills`.**

El prompt referencia el repo `despegar/agent-rules-and-skills` con un ref específico (tag o commit SHA), no `main`. El ref vive como string visible en el cuerpo del prompt para que sea diff-able en PRs y auditable en review. Actualizar el ref es un cambio explícito al catálogo, no un side-effect de cualquier merge upstream.

**D8: User-installed skills se preservan.**

Si en `.claude/skills/` existen skills que **no** vienen del catálogo de `agent-rules-and-skills` (skills que el usuario o el equipo instalaron a mano), `sync-skills` los detecta por ausencia en el manifest del repo upstream y los preserva tal cual. El preview de U2 los lista en una categoría separada ("preservados sin cambios") para que el usuario sepa que la herramienta los ve.

**D9: `sync-skills` regenera `CLAUDE.md` automáticamente cuando `AGENTS.md` cambia.**

Cuando el sync produce cambios en `AGENTS.md` (skills agregados/removidos), `sync-skills` SHALL regenerar la sección auto-managed de `CLAUDE.md` sin pedir confirmación, y reportar la regeneración en el resumen de cierre. Alternativa descartada: pedir confirmación al final ("¿querés actualizar CLAUDE.md también?"). Riesgo de la alternativa: el usuario dice "no" por inercia y queda con `CLAUDE.md` desincronizado del estado real del proyecto, perdiendo el valor del sync. Como el merge de U2 nunca toca las secciones escritas a mano por el usuario, el riesgo de regenerar automáticamente está acotado a contenido que de todas formas era auto-generado.

**D10: Preview del skills sync — counts + nombres por categoría, drill-down conversacional.**

El preview muestra por categoría (added / updated / removed / preserved) la cantidad y los nombres de skills afectados. No incluye diff por archivo en la salida default — sería ruidoso para el caso típico. Si el usuario necesita más detalle sobre un skill puntual, lo pide en la conversación ("mostrame qué cambió en `desp-eva-ui`") y Claude muestra el diff de ese skill. Esta decisión asume que el contexto conversacional reemplaza la necesidad de un flag `--verbose`: en una CLI tradicional la única opción es elegir el nivel de detalle por anticipado, en Claude Code el usuario puede pedir más sobre la marcha.

**D11: Educar al usuario sobre `.claude/settings.json` en dos momentos.**

`.claude/settings.json` es un archivo nuevo para muchos usuarios y su efecto sobre la velocidad de desarrollo es directo (la diferencia entre que Claude pida confirmación cada 30 segundos o trabaje fluido). El proyecto SHALL educar al usuario sobre este archivo en dos momentos complementarios:

1. **En el mensaje de cierre de `/new-project`** (atención alta, justo después de crear el proyecto): un bloque corto que explica qué es, por qué importa, cómo agregar comandos nuevos, y qué NO pre-aprobar. Una sola vez, en el flow de la conversación.
2. **Como sección permanente en `CLAUDE.md` del proyecto** (referencia futura + contexto para Claude): porque el mensaje de cierre se lee una vez. La sección en `CLAUDE.md` sobrevive a la sesión inicial y queda como contexto cargado en cada sesión de Claude Code, lo cual le da a Claude visibilidad sobre cómo razonar cuando el usuario diga "agregá esto al settings" más adelante.

El contenido SHALL incluir: para qué sirve, ejemplo concreto de cómo agregar un comando, lista explícita de qué NO pre-aprobar (estado compartido, producción, destructivos), y la idea de que el archivo se afina con el uso.

**D12: TodoWrite es el estándar de visibilidad para todo comando `from-scratch:` multi-paso.**

Cualquier slash command distribuido por `from-scratch` que tenga más de un paso del lado del usuario SHALL abrir un TodoWrite al inicio enumerando todos los pasos del flujo, y actualizar el estado de cada ítem (in_progress / completed) a medida que avanza. Esto se aplica a `/new-project`, a `/from-scratch:sync-skills`, y a cualquier comando futuro del catálogo que cumpla esa condición.

Razonamiento:

- TodoWrite reduce el riesgo de "Claude se olvidó un paso", que es alto cuando un prompt enumera 6+ acciones en lenguaje natural sin estructura visible.
- Para el usuario es la representación visual del progreso: ve qué falta, qué se hizo, en qué está parado el flujo en cada momento.
- Para Claude es un check anti-drift: cada vez que cierra un ítem y abre el siguiente, re-ancla en el plan original en vez de improvisar a partir del último mensaje.

Comandos one-shot (un solo paso, sin orden interno) SHALL NOT usar TodoWrite — sería ruido. La regla es "más de un paso visible para el usuario", no "el código hace varias cosas internas".

## UX / Comportamiento del usuario

Esta sección define cómo se vive el flujo desde el lado del usuario. El prompt del slash command tiene que ser explícito en estos comportamientos para que la experiencia sea consistente entre invocaciones y entre usuarios.

**U1: Feedback visible para operaciones largas.**

Las operaciones que pueden tardar más de unos segundos son: (a) clone del template, (b) clone/fetch de `despegar/agent-rules-and-skills`, (c) análisis del proyecto (Prompt 1), (d) copia de skills al proyecto (Prompt 2), (e) ejecución del Prompt 3 en `sync-skills`, y (f) generación de `CLAUDE.md` vía `/init`. El TodoWrite global cubre el "qué paso estoy haciendo", pero el prompt SHALL instruir a Claude a anunciar en chat el inicio de cada operación larga (ej. "Clonando agent-rules-and-skills…", "Analizando el proyecto…") y el resultado al terminar (ej. "Copiados 7 skills a .claude/skills/").

**U2: Preview y merge — nunca overwrite ciego.**

`AGENTS.md`, `CLAUDE.md` y `.claude/settings.json` no son archivos donde tenga sentido sobreescribir: contienen tanto contenido auto-generado por el flujo como contenido escrito a mano por el usuario. El comportamiento estándar es **merge**, no overwrite:

- **`AGENTS.md`**: las secciones auto-managed (tabla de skills, descripción de cada skill compartido) se regeneran. Las secciones escritas a mano por el usuario (notas del proyecto, reglas custom) se preservan tal cual. Se delimitan las secciones auto-managed con marcadores HTML (ej. `<!-- AUTO-GENERATED: skills-start -->` … `<!-- AUTO-GENERATED: skills-end -->`) para que el merge sea inequívoco.
- **`CLAUDE.md`**: igual patrón — la sección que `/init` regenera se actualiza, las secciones que el usuario agregó se preservan.
- **`.claude/settings.json`**: merge JSON. Los permisos nuevos del catálogo se agregan; los permisos preexistentes que el usuario haya configurado se mantienen. Si una key colisiona con valor distinto, se pide confirmación al usuario.

Antes de aplicar cualquier merge, el skills sync SHALL mostrar un **preview** con: skills a agregar, skills a actualizar, skills a remover (con la categoría "preservados sin cambios" para los user-installed según D8). El preview es **counts + nombres por categoría**; si el usuario quiere ver el diff de un skill específico, lo pide en la conversación y Claude lo muestra. En `new-project` (proyecto recién clonado, sin estado previo del usuario) se muestra el resumen sin pedir confirmación. En `sync-skills` se pide confirmación antes de aplicar cuando hay cambios. Si el merge JSON de `settings.json` detecta un conflicto real (misma key, valor distinto), se pide confirmación explícita aunque sea `new-project`.

**U3: Errores accionables.**

Cada error reportado al usuario SHALL incluir tres piezas: (1) qué falló (ej. "skills sync no completó"), (2) por qué (ej. "no se pudo clonar despegar/agent-rules-and-skills: permisos denegados"), y (3) qué hacer (ej. "verificá que tu SSH key esté agregada a GitHub y volvé a correr `/from-scratch:sync-skills`"). Casos a cubrir explícitamente en el prompt: repo de skills inaccesible (red, auth, repo movido), `AGENTS.md` con edits locales que se perderían, `settings.json` previo que colisiona, fallo del Prompt 3 por codebase insuficiente.

**U4: Idempotencia.**

Re-ejecutar `/new-project` sobre un directorio que ya existe SHALL fallar temprano con mensaje claro (no destruir el proyecto previo). Re-ejecutar `/from-scratch:sync-skills` sobre un proyecto ya sincronizado SHALL ser seguro: detecta el estado actual (skills ya presentes, `AGENTS.md` ya generado), reporta "no hay cambios" cuando corresponde, y solo escribe lo que cambió. Si una ejecución previa quedó a mitad (ej. `.claude/skills/` parcial sin `AGENTS.md`), la siguiente SHALL detectar el estado parcial y completar el flujo.

**U5: Cancelación segura.**

Las escrituras a `AGENTS.md`, `CLAUDE.md` y `.claude/settings.json` SHALL hacerse de forma atómica: escribir a un archivo temporal en el mismo directorio y renombrar al destino al final. Si el usuario cancela (Ctrl+C) durante una operación, el archivo destino queda en su estado anterior — nunca a medio escribir. La copia masiva de skills SHALL hacerse a un directorio temporal y promoverse al directorio final solo cuando la copia completó. El prompt del slash command SHALL instruir explícitamente este patrón.

**U6: Output consistente.**

Cada paso del flujo termina con una línea de resumen del paso (ej. "OK: 7 skills instalados", "OK: AGENTS.md generado"). Al final del flujo completo, Claude SHALL mostrar un resumen escaneable que incluye: nombre del proyecto, ruta absoluta, cantidad de skills instalados, archivos generados (`AGENTS.md`, `CLAUDE.md`, `.claude/settings.json`), y advertencias si algún paso quedó incompleto. Sin emojis decorativos en el output del prompt — el TodoWrite ya provee la representación visual del progreso.

**U7: Hints y próximos pasos al finalizar.**

Al finalizar `/new-project` exitosamente, Claude SHALL mostrar un mensaje de cierre que incluye: (a) cómo entrar al proyecto (ej. `cd <ruta>`), (b) que existe `/from-scratch:sync-skills` para resincronizar skills cuando el proyecto evolucione, y (c) que `AGENTS.md` documenta los skills instalados. Al finalizar `/from-scratch:sync-skills`, Claude SHALL mostrar el delta de skills (agregados/removidos/actualizados) y, si corresponde, el comando para regenerar `CLAUDE.md`. Estos hints aparecen solo al final, no durante el flujo, para no agregar ruido.

## Risks / Trade-offs

**El repositorio `despegar/agent-rules-and-skills` es una dependencia externa en tiempo de ejecución.**
→ Si el repo está inaccesible o cambia su estructura de prompts, el paso de skills sync falla. Mitigación: el prompt de `new-project` debe manejar el fallo gracefully y continuar con los pasos de Claude Code setup, reportando al usuario que el sync de skills no pudo completarse.

**El Prompt 3 de generación de skills customizados puede ser lento o producir output de calidad variable.**
→ En `sync-skills` es aceptable (el usuario lo invocó explícitamente). En `new-project` no se ejecuta por esta razón.

**El `.claude/settings.json` base puede colisionar con configuración existente en el template.**
→ Mitigación: antes de escribir `settings.json`, verificar si el template ya incluye uno. Si existe, hacer merge o avisar al usuario.

**`AGENTS.md` o `CLAUDE.md` con ediciones locales del usuario pueden ser sobreescritos en `sync-skills`.**
→ Mitigación: nunca overwrite — merge usando marcadores HTML que delimitan las secciones auto-managed (ver U2). Las secciones del usuario se preservan tal cual. Si el archivo no tiene los marcadores (proyecto antiguo migrado), el prompt detecta esa situación, pide confirmación, e inserta los marcadores envolviendo el contenido auto-generado.

**Una ejecución interrumpida puede dejar el proyecto en estado parcial (skills copiados, `AGENTS.md` no generado).**
→ Mitigación: escrituras atómicas (temp file + rename) para archivos individuales; copia de skills a directorio temporal con promoción al final. La siguiente ejecución de `sync-skills` debe poder detectar el estado parcial y completarlo sin pedir intervención manual.

**`/from-scratch:sync-skills` invocado fuera de un proyecto.**
→ El usuario puede invocar el comando desde un directorio que no es la raíz de un proyecto (no hay `.git`, no hay `package.json`/`pom.xml`/etc., no hay `AGENTS.md`). Mitigación: el prompt detecta la ausencia de marcadores de proyecto y aborta temprano con un error accionable que sugiere `cd` al directorio correcto o ejecutar `/new-project` para crear uno nuevo.

**Skills preexistentes con frontmatter inválido en `.claude/skills/`.**
→ Si el directorio destino tiene archivos `.md` con YAML mal formado, el análisis del Prompt 1 puede fallar. Mitigación: el prompt los reporta como skills inválidos en el preview (categoría "ignorados por frontmatter inválido") y continúa con el resto, sin bloquear el sync completo.

**Binario `from-scratch` desactualizado respecto del catálogo.**
→ Una versión vieja del binario puede no conocer la convención de subcarpetas en `commands/` (`commands/from-scratch/`). Mitigación: el prompt de `sync-skills` documenta la versión mínima de `from-scratch` requerida; si el archivo no aparece en `~/.claude/commands/from-scratch/` después de `init`, el usuario sabe que necesita actualizar el binario primero.

## Contrato del prompt (qué tiene que tener `new-project.md` y `sync-skills.md`)

El prompt resultante SHALL cumplir simultáneamente:

1. **Rol declarado al inicio** (1-2 líneas) — quién es Claude en este flujo y cuál es el objetivo.
2. **Bloque de restricciones globales** que aplican a todo el flujo (atomic writes, preview antes de mutar, formato de errores accionables, no avanzar ante ambigüedad). Se declara una sola vez, no se repite en cada paso.
3. **Lista de pasos como objetivos**, no como secuencias de tool calls. Cada paso describe el estado final esperado, no el procedimiento. Ejemplo bueno: "Al final de este paso, el proyecto tiene `AGENTS.md` con los skills instalados". Ejemplo malo: "Ejecutá `git clone <url>`, después corré `cat README.md`, después...".
4. **Referencias externas explícitas con pin de versión** (D7) cuando el flujo depende de prompts/recursos remotos.
5. **Bloque de cierre con resumen y hints** (U6, U7).
6. **Tono consistente** con `new-project.md` actual: voseo, registro de desarrollador senior, sin emojis, sin pasos mecánicos.

El prompt SHALL NOT:

- Re-explicar cómo se usa `TodoWrite` o cualquier tool nativa de Claude Code.
- Repetir las restricciones globales dentro de cada paso.
- Incluir pseudo-código de control de flujo (if/else, loops) — eso es trabajo de Claude, no del prompt.
- Crecer indefinidamente: si supera ~150 líneas de prompt útil (sin contar frontmatter), es señal de que falta factorizar.

## Open Questions

- ¿Cuál es el `settings.json` base correcto para proyectos Despegar? ¿Hay permisos estándar que todos los proyectos deberían tener pre-aprobados (ej. `Bash(mvn test)`, `Bash(git status)`)?
