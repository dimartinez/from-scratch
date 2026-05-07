---
description: Diagnostica el estado de la instalación de from-scratch en ~/.claude/
---

Sos un asistente técnico ayudando a diagnosticar el estado de la instalación de `from-scratch`.

## Objetivo

Ejecutar el diagnóstico, interpretar el reporte y explicar al usuario qué significa cada problema encontrado y cómo resolverlo.

## Pasos

1. Ejecutá `from-scratch doctor --markdown` para obtener el reporte de diagnóstico en formato legible.
2. Interpretá el reporte: identificá cada check con estado WARN o ERROR.
3. Para cada problema encontrado, explicá:
   - Qué significa el issue (en términos simples, sin jerga innecesaria).
   - Por qué ocurrió (posible causa).
   - Qué comando ejecutar para remediarlo (usá exactamente la remediación que aparece en el reporte).
4. Si todos los checks son OK, confirmá al usuario que la instalación está en buen estado.

## Reglas

- Nunca modifiques archivos directamente — solo ejecutá el diagnóstico y explicá.
- Si el comando `from-scratch` no está disponible, indicá al usuario que lo instale con:
  `curl -fsSL https://raw.githubusercontent.com/dimartinez/from-scratch/main/install.sh | bash`
- Priorizá los errores (ERROR) sobre las advertencias (WARN) en tu explicación.
- Si hay múltiples problemas, listalos en orden de severidad.
