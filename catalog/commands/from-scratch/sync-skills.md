---
description: Re-sincroniza skills de Claude Code desde el catálogo compartido de Despegar
---

Sos un desarrollador senior actualizando la configuración de Claude Code en este proyecto.
Tu objetivo es mantener los skills sincronizados con el catálogo de Despegar, preservando cambios locales.

## Versión mínima de from-scratch

Requiere `from-scratch` >= 0.2.0 (primera versión que conoce el subdirectorio `commands/from-scratch/`).
Si `/from-scratch:sync-skills` no aparece en tu lista de comandos después de `from-scratch init`,
actualizá el binario con `from-scratch update`.

## Restricciones globales

- Escrituras atómicas: escribí a un archivo temporal en el mismo directorio y renombralo al destino.
  La copia masiva de skills se hace a un directorio temporal y se promueve al final.
- Preview antes de mutar: mostrá counts y nombres por categoría (agregados/actualizados/removidos/preservados)
  antes de aplicar cambios. Pedí confirmación cuando `.claude/skills/` o `AGENTS.md` ya existen.
- Cada error incluye: qué falló, por qué, y qué hacer para recuperarse.
- No avancés ante ambigüedad sin preguntar.

## Ref pinneado

**Repositorio:** `despegar/agent-rules-and-skills` @ `v1.0.0`

- Prompt 1 (análisis del proyecto): `https://raw.githubusercontent.com/despegar/agent-rules-and-skills/v1.0.0/prompts/01-project-analysis.md`
- Prompt 2 (sync de skills compartidos): `https://raw.githubusercontent.com/despegar/agent-rules-and-skills/v1.0.0/prompts/02-skills-sync.md`
- Prompt 3 (generación de skills customizados): `https://raw.githubusercontent.com/despegar/agent-rules-and-skills/v1.0.0/prompts/03-custom-skills.md`

Para actualizar a una nueva versión, editá el ref `v1.0.0` en las tres URLs y publicá una nueva versión del catálogo.

## Flujo

Usá un TodoWrite al inicio enumerando: análisis del proyecto, sync de skills compartidos,
generación de skills customizados, actualización de AGENTS.md, regeneración de CLAUDE.md cuando aplique.
Actualizalo a medida que avancés.

### Paso 0: Pre-validación

El objetivo es confirmar que estás en la raíz de un proyecto: debe existir `.git`, o un marcador
de stack (`pom.xml`, `package.json`, `build.gradle`, etc.), o `AGENTS.md`.
Si ninguno existe, abortá con un error accionable que sugiera `cd` al directorio correcto
o ejecutar `/new-project` para crear uno nuevo.

### Paso 1: Análisis del proyecto

Leé y ejecutá el Prompt 1 desde el ref pinneado. El objetivo es identificar cuáles skills
del catálogo son relevantes para este proyecto.

Skills en `.claude/skills/` con frontmatter inválido: listálos en el preview como
"ignorados por frontmatter inválido" y continuá con el resto — no bloqueés el sync completo.

Skills user-installed (presentes en `.claude/skills/` pero ausentes del catálogo upstream):
detectálos y listálos en el preview como "preservados sin cambios". Nunca los toques.

### Paso 2: Preview y confirmación

Antes de aplicar, mostrá el preview: counts y nombres por categoría
(agregados / actualizados / removidos / preservados sin cambios).
Si el usuario quiere ver el diff de un skill específico, mostráselo en la conversación.

Cuando `.claude/skills/` o `AGENTS.md` ya existen, pedí confirmación antes de proceder.
En un proyecto sin estado previo, el resumen no requiere confirmación.

### Paso 3: Sync de skills compartidos

Leé y ejecutá el Prompt 2 desde el ref pinneado. El objetivo es que `.claude/skills/` y
`AGENTS.md` reflejen el catálogo relevante.

Para `AGENTS.md`: merge usando los marcadores
`<!-- AUTO-GENERATED: skills-start -->` / `<!-- AUTO-GENERATED: skills-end -->`.
Solo regenerá la sección delimitada; el contenido escrito a mano se preserva.
Si el archivo existe pero no tiene los marcadores (proyecto antiguo), pedí confirmación
e insertá los marcadores envolviendo el contenido auto-generado.

### Paso 4: Generación de skills customizados

Leé y ejecutá el Prompt 3 desde el ref pinneado. El objetivo es generar skills
específicos de este proyecto desde el codebase real.

Si el proyecto no tiene historia de código suficiente para que el Prompt 3 produzca
skills útiles, ejecutalo igualmente pero advertí al usuario que el output puede ser
de baja calidad por falta de codebase. Sugerí volver a correr `/from-scratch:sync-skills`
cuando el proyecto tenga más código.

### Paso 5: Detección de estado parcial

Si detectás que una ejecución previa quedó a mitad (ej. skills copiados sin `AGENTS.md`,
o `AGENTS.md` sin `CLAUDE.md` actualizado), completá el flujo desde el punto de quiebre
sin pedir intervención manual cuando es seguro hacerlo.

### Paso 6: Regeneración de CLAUDE.md

Si el sync modificó `AGENTS.md`, regenerá automáticamente la sección auto-managed de `CLAUDE.md`
sin pedir confirmación. Usá los marcadores
`<!-- AUTO-GENERATED: claude-init-start -->` / `<!-- AUTO-GENERATED: claude-init-end -->`.
Si el archivo no tiene los marcadores, pedí confirmación e insertálos.

## Cierre

Mostrá el delta de skills: counts y nombres por categoría (agregados/actualizados/removidos/preservados).
Si `AGENTS.md` cambió y `CLAUDE.md` fue regenerado automáticamente, reportalo en el resumen.
Si algún paso quedó incompleto, listá las advertencias con el comando para completar.
