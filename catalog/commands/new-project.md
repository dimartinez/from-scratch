---
description: Crea un nuevo proyecto desde un template de Despegar
---

Sos un desarrollador senior preparando el ambiente para un proyecto nuevo.
Tu objetivo es dejar el proyecto listo para que el usuario pueda empezar a trabajar:
template configurado, skills instalados, `AGENTS.md` y `CLAUDE.md` generados, permisos base en su lugar.

## Restricciones globales

- Verificá que el directorio destino no exista antes de comenzar. Si ya existe, abortá con un mensaje
  claro — nunca destruyas el proyecto previo.
- Escrituras atómicas: escribí a un archivo temporal en el mismo directorio y renombralo al destino.
- Merge en vez de overwrite para `AGENTS.md`, `CLAUDE.md` y `.claude/settings.json` usando marcadores
  `<!-- AUTO-GENERATED: ...-start -->` / `<!-- AUTO-GENERATED: ...-end -->`. Si el archivo existe
  sin los marcadores (proyecto antiguo), pedí confirmación e insertálos.
- Cada error incluye: qué falló, por qué, y qué hacer para recuperarse.
- No avancés ante ambigüedad sin preguntar.

## Ref pinneado

**Repositorio de skills:** `despegar/agent-rules-and-skills` @ `v1.0.0`

- Prompt 1 (análisis del proyecto): `https://raw.githubusercontent.com/despegar/agent-rules-and-skills/v1.0.0/prompts/01-project-analysis.md`
- Prompt 2 (sync de skills compartidos): `https://raw.githubusercontent.com/despegar/agent-rules-and-skills/v1.0.0/prompts/02-skills-sync.md`

El Prompt 3 no se ejecuta en `/new-project` — el proyecto recién clonado no tiene historia suficiente.
Para generar skills customizados, corré `/from-scratch:sync-skills` cuando el proyecto tenga código real.

## Flujo

No seguís pasos mecánicos — leés el README del template y tomás las decisiones correctas.
Usá un TodoWrite al inicio enumerando los pasos: clone del template, skills sync,
`.claude/settings.json`, generación de `CLAUDE.md`. Actualizalo a medida que avancés.
Anunciá en el chat el inicio y resultado de cada operación larga.

### Paso 1: Selección del template

El objetivo es que el usuario elija un stack y un nombre de proyecto.
Leé los stacks en `~/.claude/stacks/`: mostrá `name` y `description` de cada uno.
Si `~/.claude/stacks/` está vacía, informale al usuario y sugerí correr `from-scratch init`.

### Paso 2: Clone y configuración del template

El objetivo es que el proyecto exista en disco, configurado con el nombre y los parámetros correctos.
Cloná el template con la `template_url` del stack elegido. Leé el README del template y seguí
sus instrucciones. Si hay ambigüedad, pausá y preguntá antes de continuar.
Validá coherencia entre el README, el código y la configuración.

Si el directorio destino ya existe, abortá con error accionable — nunca sobreescribas un proyecto previo.

### Paso 3: Skills sync (Prompts 1+2)

El objetivo es que el proyecto tenga `.claude/skills/`, `AGENTS.md` con los skills relevantes.
Leé y ejecutá el Prompt 1 (análisis) y el Prompt 2 (skills compartidos) desde el ref pinneado.
En un proyecto recién clonado no hay estado previo, así que mostrá el resumen sin pedir confirmación.

Si el skills sync falla (repo inaccesible, permisos denegados): reportá el error con qué falló,
por qué, y qué hacer (ej. "verificá que tu SSH key esté en GitHub y corré `/from-scratch:sync-skills`").
Continuá con los pasos restantes — no abortes todo el flujo.

### Paso 4: Configuración de .claude/settings.json

El objetivo es que el proyecto tenga permisos base para trabajar sin confirmaciones constantes.
Si el template ya incluye un `settings.json`, hacé merge JSON: agregá las keys nuevas, preservá
las existentes. Si detectás un conflicto (misma key, valor distinto), pedí confirmación.

### Paso 5: Generación de CLAUDE.md

El objetivo es que el proyecto tenga un `CLAUDE.md` que referencia `AGENTS.md` y documenta los
skills instalados. Seguí el comportamiento del `/init` built-in de Claude Code: analizá el codebase,
generá `CLAUDE.md` con referencia explícita a `AGENTS.md`. Este paso corre después del skills sync
para que `AGENTS.md` ya exista y pueda ser referenciado.

Envolvé la sección auto-generada con los marcadores
`<!-- AUTO-GENERATED: claude-init-start -->` / `<!-- AUTO-GENERATED: claude-init-end -->`.

Incluí en la sección auto-managed una subsección sobre `.claude/settings.json`:
qué es, por qué afecta la velocidad de trabajo, cómo agregar un comando nuevo,
y qué NO pre-aprobar (comandos destructivos, producción, estado compartido).

## Cierre

Mostrá un resumen escaneable: nombre del proyecto, ruta absoluta, cantidad de skills instalados,
archivos generados (`AGENTS.md`, `CLAUDE.md`, `.claude/settings.json`),
advertencias por pasos incompletos.

Incluí en el mensaje de cierre un bloque educativo sobre `.claude/settings.json`:
qué es, por qué importa para la velocidad, cómo agregar comandos nuevos, y qué no pre-aprobar.

Finalizá con el hint: "Para resincronizar skills cuando el proyecto evolucione, usá `/from-scratch:sync-skills`."
