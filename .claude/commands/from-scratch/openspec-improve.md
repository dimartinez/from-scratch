---
description: Run a full review cycle on an OpenSpec change — UX, agentic-coding, and TDD specialists in sequence — to bring the spec to a better state.
argument-hint: <change-name>
---

Vas a ejecutar un ciclo de revisión completa sobre un cambio de OpenSpec.

## Resolver cuál cambio se va a revisar

**Si `$ARGUMENTS` viene con un valor**, usalo como nombre del cambio. Verificá que la carpeta `openspec/changes/<nombre-resuelto>/` existe. Si no existe, avisale al usuario y detenete.

**Si `$ARGUMENTS` está vacío**, descubrí los cambios abiertos automáticamente:

1. Listá los directorios dentro de `openspec/changes/` excluyendo el directorio `archive` (los cambios archivados no son candidatos). Para esto podés ejecutar: `ls -d openspec/changes/*/ 2>/dev/null | grep -v '/archive/$' | xargs -n1 basename`.

2. Según cuántos cambios abiertos haya:
   - **Cero cambios abiertos**: avisale al usuario que no hay specs abiertos para revisar y detenete.
   - **Un único cambio**: anunciá al usuario que vas a revisar ese cambio (mostrá el nombre) y procedé directamente, sin preguntar.
   - **Más de un cambio**: presentale la lista al usuario y pedile que elija cuál revisar. Esperá su respuesta antes de seguir.

A partir de acá, el resto del flujo trabaja sobre la carpeta `openspec/changes/<nombre-resuelto>/`.

## El ciclo

Vas a invocar tres sub-agentes en este orden, uno después del otro (no en paralelo — cada uno depende del estado que dejó el anterior):

### 1. `openspec-ux-reviewer`

Pasale como contexto: la ruta `openspec/changes/<nombre-resuelto>/`. Que audite proposal.md, design.md y tasks.md contra sus 8 criterios de UX y aplique las modificaciones que correspondan.

Esperá su reporte completo antes de seguir.

### 2. `openspec-agentic-reviewer`

Pasale como contexto: la misma ruta `openspec/changes/<nombre-resuelto>/`. Que audite los archivos contra sus 7 criterios de agentic-coding y aplique las modificaciones — manteniéndose dentro del scope ya declarado del cambio (no debe expandir features). Sus sugerencias fuera de scope vienen como notas en el reporte, no como ediciones.

Esperá su reporte completo antes de seguir.

### 3. `openspec-tdd-reviewer`

Pasale como contexto: la misma ruta. Que audite tasks.md contra sus 6 criterios de TDD y corrija cualquier tarea (incluyendo las que agregaron los dos agentes anteriores) que no esté en formato test → implementación.

## Reporte final al usuario

Cuando los tres terminen, presentale al usuario un resumen unificado en este orden:

1. **Resumen ejecutivo** (2-3 líneas): cuántos criterios violados encontró cada agente, cuántas ediciones se aplicaron en total, y si la spec quedó validando.

2. **Por agente** (una sección breve para cada uno):
   - Violaciones encontradas (lista corta).
   - Cambios aplicados (lista corta con archivo + sección).

3. **Estado de validación final**: si `openspec validate <nombre-resuelto>` pasa o no.

4. **Notas fuera de scope** (si las hay): sugerencias del agente agentic que requieren un cambio futuro de OpenSpec, no aplicadas al spec actual. Esto es información para que el usuario decida si quiere abrir un cambio nuevo más adelante.

5. **Recomendaciones que requieren decisión humana** (si las hay): preguntas que algún agente dejó abiertas porque no podía decidir solo.

Mantené el reporte conciso. El usuario quiere ver el delta, no leer un ensayo. Si un agente no aplicó ningún cambio, decilo en una línea ("UX reviewer: spec ya cumple, sin cambios").
