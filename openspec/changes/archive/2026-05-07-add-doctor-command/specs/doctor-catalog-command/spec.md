## ADDED Requirements

### Requirement: Entrada de catálogo para /from-scratch:doctor
El catálogo SHALL incluir una entrada de tipo `command` para `commands/from-scratch/doctor.md` que `from-scratch init` y `from-scratch update` instalan en `~/.claude/commands/from-scratch/doctor.md`, exponiendo el slash command `/from-scratch:doctor` en Claude Code.

#### Scenario: Instalación del slash command
- **WHEN** el usuario corre `from-scratch init` o `from-scratch update`
- **THEN** el archivo `~/.claude/commands/from-scratch/doctor.md` queda instalado y `/from-scratch:doctor` aparece disponible en Claude Code

#### Scenario: El comando aparece en catalog.json
- **WHEN** se lee `catalog/catalog.json`
- **THEN** existe una entrada `{ "kind": "command", "source": "commands/from-scratch/doctor.md" }` en el array `entries`

---

### Requirement: Contenido del slash command
El archivo `catalog/commands/from-scratch/doctor.md` SHALL contener un prompt de sistema que instruye al agente a ejecutar el diagnóstico CLI e interpretar el resultado.

#### Scenario: Ejecución del diagnóstico desde Claude Code
- **WHEN** el usuario invoca `/from-scratch:doctor` en una sesión de Claude Code
- **THEN** el agente ejecuta `from-scratch doctor --markdown` en la terminal, lee el output, y presenta al usuario un diagnóstico en lenguaje natural explicando los problemas encontrados y los pasos para remediarlos

#### Scenario: Instalación sana
- **WHEN** el output del doctor es `status: OK`
- **THEN** el agente confirma que la instalación está en buen estado y no sugiere acciones

#### Scenario: Problemas detectados
- **WHEN** el output del doctor contiene checks con WARN o ERROR
- **THEN** el agente lista los problemas, explica qué significa cada uno, y proporciona los comandos de remediación a correr

#### Scenario: Frontmatter válido
- **WHEN** se lee el archivo `catalog/commands/from-scratch/doctor.md`
- **THEN** contiene frontmatter YAML con al menos el campo `description` en español, parseable por el parser plano del proyecto (`src/catalog/yaml_frontmatter.py`)
