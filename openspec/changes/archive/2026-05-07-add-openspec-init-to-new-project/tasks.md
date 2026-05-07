## 1. Modificar el skill new-project — happy path

- [x] 1.1 Leer `catalog/commands/new-project.md` completo para entender el estado actual del Paso 2 y la lista del TodoWrite
- [x] 1.2 Agregar en `new-project-openspec-init/spec.md` los escenarios BDD que cubren el comportamiento esperado del happy path: (a) `openspec` disponible y proyecto clonado → `openspec init` ejecutado, `openspec/` creada, ítem del TodoWrite marcado completado; (b) `openspec` no disponible → ítem marcado con error, mensaje con las tres piezas, flujo continúa. [Verificación humana — spec BDD de comportamiento de agente; no existe runner automático para este tipo de artefacto]
- [x] 1.3 Agregar en la sección del Paso 2 las instrucciones para verificar disponibilidad de `openspec` (con error accionable si no está) y ejecutar `openspec init`. Las instrucciones deben seguir el estilo del resto del archivo: declarativas, orientadas a objetivo, sin scripting paso a paso. No listes cada sub-paso como orden imperativa; describí el comportamiento esperado y dejá que el modelo decida la mecánica.
- [x] 1.4 Agregar en `new-project-command/spec.md` el escenario que cubre el ítem dedicado en el TodoWrite: cuando el usuario invoca `/new-project` y confirma, el TodoWrite incluye un ítem independiente para la inicialización de OpenSpec (distinto del clone/configuración), con su propio estado observable. [Verificación humana — spec BDD de comportamiento de agente]
- [x] 1.5 Actualizar las instrucciones del `TodoWrite` para incluir el ítem de "Inicializar OpenSpec" como paso separado entre la configuración del template y el skills sync

## 2. Idempotencia — verificación de estado previo

- [x] 2.1 Agregar en `new-project-openspec-init/spec.md` el escenario BDD: cuando `openspec/` ya existe en el directorio del proyecto al llegar al paso, el agente NO ejecuta `openspec init` y marca el ítem como completado con el mensaje `"openspec/ ya existe — paso omitido"`. [Verificación humana — spec BDD de comportamiento de agente]
- [x] 2.2 Agregar en las instrucciones del Paso 2 del skill: antes de llamar `openspec init`, verificar si `openspec/` existe; si existe, omitir la ejecución y registrar el motivo

## 3. Mensajes de error — caso fallo de ejecución (no solo ausencia del binario)

- [x] 3.1 Agregar en `new-project-openspec-init/spec.md` el escenario BDD: cuando `openspec init` falla por permisos o error interno, el mensaje de error incluye qué falló, el output del proceso hijo, y el comando exacto para reintentar manualmente (`cd <ruta> && openspec init`). [Verificación humana — spec BDD de comportamiento de agente]
- [x] 3.2 Agregar en las instrucciones del Paso 2 del skill: capturar el stderr/código de salida de `openspec init` y reportarlo con las tres piezas (qué falló / por qué / cómo resolver)
- [x] 3.3 Agregar en `new-project-openspec-init/spec.md` el escenario BDD: cuando `openspec init` falla y el directorio del proyecto no contiene `.git/`, el mensaje de error incluye como remediación `git init && openspec init`; cuando `.git/` sí existe, el mensaje reporta el stderr del proceso hijo y sugiere `cd <ruta> && openspec init`. [Verificación humana — spec BDD de comportamiento de agente]
- [x] 3.4 Agregar en las instrucciones del Paso 2 del skill: al capturar un fallo de `openspec init`, verificar si el directorio contiene `.git/` para elegir el mensaje de remediación correcto

## 4. Hint post-ejecución

- [x] 4.1 Agregar en `new-project-command/spec.md` el escenario BDD: cuando el flujo completo termina con `openspec init` exitoso, el resumen final incluye la línea `"OpenSpec inicializado — usá /opsx:propose para proponer tu primer cambio."`. [Verificación humana — spec BDD de comportamiento de agente]
- [x] 4.2 Agregar en las instrucciones del resumen final del skill (Fase 5 o cierre) la condición: si el ítem de OpenSpec completó con éxito, incluir el hint de uso; si falló u omitió, incluir el comando para corregirlo manualmente

## 5. Verificar consistencia

- [x] 5.1 Confirmar que el mensaje de error accionable especifica exactamente `npm install -g @fission-ai/openspec`
- [x] 5.2 Confirmar que la instrucción de continuar ante fallo es consistente con la política de error ya existente en el Paso 3 del skill
