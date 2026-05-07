## MODIFIED Requirements

### Requirement: El flujo de /new-project incluye setup de Claude Code

El comando `/new-project` SHALL incluir los pasos de skills sync y configuración de Claude Code como parte del flujo estándar de creación del proyecto. Estos pasos se ejecutan automáticamente después de la configuración del template sin requerir acción del usuario.

#### Scenario: Flujo completo exitoso

- **WHEN** el usuario invoca `/new-project`, elige stack y nombre, y el template se configura correctamente
- **THEN** Claude ejecuta en orden: (1) clone y configuración del template según README, (2) inicialización de OpenSpec con `openspec init`, (3) validación de coherencia, (4) skills sync desde `despegar/agent-rules-and-skills`, (5) creación de `.claude/settings.json`, (6) generación de `CLAUDE.md` con referencia a `AGENTS.md`, y al finalizar reporta el proyecto listo junto con un resumen de skills instalados.

### Requirement: El progreso de /new-project es visible mediante TodoWrite

Claude SHALL usar la herramienta TodoWrite al inicio de la ejecución de `/new-project` para mostrar todos los pasos del flujo, y SHALL actualizar el estado de cada paso conforme avanza.

#### Scenario: Checklist visible durante ejecución

- **WHEN** el usuario invoca `/new-project` y confirma stack y nombre
- **THEN** aparece un TodoWrite con todos los pasos del flujo (clone, configuración, openspec init, validación, skills sync, settings.json, CLAUDE.md) y cada ítem se marca completado a medida que termina.

#### Scenario: Fallo en un paso intermedio

- **WHEN** uno de los pasos falla (ej. el skills sync no puede acceder al repositorio, o `openspec` no está instalado)
- **THEN** el ítem correspondiente en el TodoWrite queda sin completar, Claude reporta el error al usuario con un mensaje accionable, y continúa con los pasos restantes que no dependan del fallido.

### Requirement: El resumen final refleja el resultado de openspec init

El cierre del flujo SHALL incluir información sobre el resultado del paso de OpenSpec, con un hint de uso si completó exitosamente o un comando de remediación si falló u fue omitido.

#### Scenario: Resumen final con openspec init exitoso

- **WHEN** el flujo completo termina y el paso de `openspec init` completó exitosamente
- **THEN** el resumen final incluye la línea: `"OpenSpec inicializado — usá /opsx:propose para proponer tu primer cambio."`.

#### Scenario: Resumen final con openspec init fallido u omitido

- **WHEN** el flujo completo termina y el paso de `openspec init` falló o fue omitido
- **THEN** el resumen final menciona el estado del paso e incluye el comando para corregirlo manualmente (`cd <ruta-del-proyecto> && openspec init`).
