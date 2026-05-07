## ADDED Requirements

### Requirement: openspec se inicializa como paso explícito en /new-project

Durante la ejecución de `/new-project`, el agente SHALL ejecutar `openspec init` en el directorio del proyecto recién clonado como un paso dedicado dentro de la Fase 2, después de la configuración del template y antes del skills sync.

#### Scenario: openspec disponible y proyecto clonado

- **WHEN** el template fue clonado y configurado exitosamente, y `openspec` está disponible en el sistema
- **THEN** el agente ejecuta `openspec init` en el directorio del proyecto, la carpeta `openspec/` queda creada con su estructura, y el ítem correspondiente en el TodoWrite se marca completado.

#### Scenario: openspec no disponible en el sistema

- **WHEN** el agente intenta verificar la disponibilidad de `openspec` y el comando no existe
- **THEN** el agente marca el ítem del TodoWrite con error, reporta un error accionable (`npm install -g @fission-ai/openspec`) indicando qué falló y cómo resolverlo, y continúa con los pasos restantes del flujo sin abortar.

### Requirement: La inicialización de openspec es idempotente

Si `openspec/` ya existe en el directorio del proyecto al llegar al paso, el agente SHALL omitir `openspec init` y reportar el motivo.

#### Scenario: openspec/ ya existe en el directorio

- **WHEN** el agente llega al paso de `openspec init` y la carpeta `openspec/` ya existe en el directorio del proyecto
- **THEN** el agente NO ejecuta `openspec init`, marca el ítem del TodoWrite como completado con el mensaje `"openspec/ ya existe — paso omitido"`, y continúa con los pasos restantes sin producir errores.

### Requirement: Los errores de openspec init se reportan con tres piezas y permiten recuperación manual

Cuando `openspec init` falla, el agente SHALL reportar qué falló, por qué, y el comando exacto para reintentar manualmente, y SHALL continuar con los pasos restantes.

#### Scenario: openspec init falla por permisos o error interno

- **WHEN** `openspec` está disponible en el sistema pero `openspec init` termina con código de salida distinto de cero
- **THEN** el mensaje de error incluye: qué falló (`"Falló openspec init en <ruta>"`), el output del proceso hijo (stderr), y el comando exacto para reintentar manualmente; el flujo continúa con los pasos restantes sin abortar.

#### Scenario: openspec init falla y el directorio no tiene .git/

- **WHEN** `openspec init` falla y el directorio del proyecto no contiene `.git/`
- **THEN** el mensaje de remediación es `git init && openspec init`.

#### Scenario: openspec init falla y el directorio tiene .git/

- **WHEN** `openspec init` falla y el directorio del proyecto contiene `.git/`
- **THEN** el mensaje de remediación es `cd <ruta> && openspec init` e incluye el stderr del proceso hijo.

### Requirement: La inicialización de openspec tiene ítem dedicado en el TodoWrite

El paso de `openspec init` SHALL aparecer como un ítem independiente en el TodoWrite de `/new-project`, no como sub-bullet de otro paso.

#### Scenario: Ítem visible desde el inicio

- **WHEN** el usuario invoca `/new-project` y confirma stack y nombre
- **THEN** el TodoWrite incluye un ítem explícito para la inicialización de OpenSpec (distinto del ítem de clone/configuración del template), y su estado se actualiza de forma independiente.
