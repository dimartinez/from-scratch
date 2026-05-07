## Context

El comando `new-project` (`catalog/commands/new-project.md`) orquesta 5 fases para dejar un proyecto listo. La Fase 2 clona el template y lo configura. Actualmente no incluye `openspec init`, lo que significa que los proyectos nuevos no tienen la estructura `openspec/` ni el agente recibe feedback visual sobre ese paso.

`openspec init` es un comando CLI externo (`npm install -g @fission-ai/openspec`) que crea la carpeta `openspec/` con el scaffolding necesario para el flujo spec-driven. Es una herramienta del entorno del usuario, no del proyecto — análoga a `git` o `node`.

## Goals / Non-Goals

**Goals:**
- Agregar `openspec init` como paso explícito y visible en el `TodoWrite` del skill `new-project`.
- Verificar disponibilidad de `openspec` antes de ejecutar; reportar error accionable si no está.
- No interrumpir el flujo completo ante este fallo — el resto de las fases continúa.

**Non-Goals:**
- Instalar `openspec` automáticamente (`npm install -g`) — es responsabilidad del entorno del usuario.
- Modificar el comportamiento de `openspec init` ni sus artefactos generados.
- Cambiar otras fases del flujo de `new-project`.

## Decisions

### Ubicación: al final de la Fase 2, antes del skills sync

**Decisión:** El paso de `openspec init` se agrega como último sub-paso de la Fase 2, después de clonar y configurar el template.

**Rationale:** La Fase 3 (skills sync) ejecuta Prompt 1 que analiza el proyecto. Si `openspec/` existe en ese momento, el análisis lo detecta y puede referenciarlo en `AGENTS.md`. Si lo dejamos para después, se pierde esa oportunidad. La Fase 2 ya tiene como objetivo "el proyecto existe en disco, configurado correctamente" — `openspec/` es parte de esa configuración.

**Alternativa descartada:** Agregarlo en la Fase 3 como parte del skills sync. Se descartó porque mezclaría scaffolding de proyecto con instalación de skills.

### Error handling: reportar y continuar

**Decisión:** Si `openspec` no está disponible, el agente reporta un error accionable (`npm install -g @fission-ai/openspec`) y continúa con las fases restantes. No aborta.

**Rationale:** Consistente con la política de error de la Fase 3 del skill (`Si algún prompt falla... Continuá con los pasos restantes — no abortes todo el flujo`). Un proyecto sin `openspec/` es subóptimo pero funcional; no justifica bloquear el setup completo.

### TodoWrite: ítem separado

**Decisión:** El paso aparece como su propio ítem en el `TodoWrite`, no como sub-bullet de la Fase 2.

**Rationale:** El usuario pidió explícitamente feedback visual de que esto ocurrió. Un ítem dedicado en el `TodoWrite` comunica inicio, progreso y resultado de forma inequívoca.

## Risks / Trade-offs

- **`openspec` no instalado globalmente** → Mitigation: error accionable con el comando exacto para instalarlo; el flujo continúa.
- **`openspec init` falla por permisos o conflicto de directorio** → Mitigation: el agente reporta el error y continúa; el usuario puede correr `openspec init` manualmente después.
- **Versión de `openspec` incompatible** → Mitigation: fuera de scope; el error de `openspec init` se propaga como error accionable.
- **Directorio del proyecto sin repositorio git inicializado** → El Paso 2 clona via git, así que normalmente existe un `.git/`. Pero si el clone falló parcialmente y el usuario reintentó el flujo, podría no haber `.git/`. Algunos runners de `openspec init` lo requieren. Mitigation: si `openspec init` falla y el directorio no contiene `.git/`, el mensaje de error incluye como remediación `git init && openspec init`; si `.git/` existe, se reporta el stderr del proceso hijo.

## UX — Comportamiento observable

### Texto del ítem en el TodoWrite

El ítem dedicado al paso de OpenSpec debe aparecer con el texto: `"Inicializar OpenSpec (openspec init)"`. Su estado pasa por tres transiciones: pendiente → en progreso → completado (o error).

### Idempotencia

Antes de ejecutar `openspec init`, el agente verifica si la carpeta `openspec/` ya existe en el directorio del proyecto. Si existe, el agente marca el ítem como completado con el mensaje `"openspec/ ya existe — paso omitido"` y continúa sin ejecutar `openspec init`. Esto garantiza que re-ejecutar `/new-project` sobre un proyecto ya configurado no produce errores ni sobreescrituras.

### Mensajes de error: tres piezas obligatorias

Cada caso de fallo en este paso debe comunicar las tres piezas:

| Caso | Qué falló | Por qué | Cómo resolver |
|---|---|---|---|
| `openspec` no instalado | "No se encontró `openspec` en el sistema" | "El binario no está disponible en el PATH" | `npm install -g @fission-ai/openspec` |
| `openspec init` falla (permisos, directorio) | "Falló `openspec init` en `<ruta>`" | El mensaje de error del proceso hijo | `cd <ruta> && openspec init` |

### Hint post-ejecución

Al finalizar el flujo completo (resumen final), si `openspec init` completó exitosamente, el resumen incluye la línea: `"OpenSpec inicializado — usá /opsx:propose para proponer tu primer cambio."` Si el paso falló o fue omitido, el resumen lo menciona con el comando para corregirlo manualmente.

### Interrupción durante el paso

Si el agente es interrumpido mientras ejecuta `openspec init`, el estado del TodoWrite queda incompleto. Al retomar, el agente verifica la existencia de `openspec/` (criterio de idempotencia) para determinar si el paso completó antes de la interrupción.
