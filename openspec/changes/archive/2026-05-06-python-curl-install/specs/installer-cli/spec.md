## MODIFIED Requirements

### Requirement: Instalación global desde el repo de GitHub

La CLI `from-scratch` SHALL ser instalable mediante un instalador `curl | bash` que clona el repositorio y deja un wrapper ejecutable en el PATH del usuario, sin necesidad de Node.js, npm, ni publicación en ninguna registry de paquetes.

#### Scenario: Instalación inicial en una máquina limpia

- **WHEN** un usuario con `git`, `python3` (>= 3.8) y `bash` ejecuta `curl -fsSL https://raw.githubusercontent.com/dimartinez/from-scratch/main/install.sh | bash`
- **THEN** el script clona el repo en `~/.from-scratch/`, escribe un wrapper ejecutable en `~/.local/bin/from-scratch` que delega a `python3 ~/.from-scratch/src/cli.py`, y reporta el path donde dejó el binario.

#### Scenario: Re-instalación sobre clone existente

- **WHEN** el usuario re-ejecuta el comando `curl | bash` y `~/.from-scratch/` ya existe como clone limpio
- **THEN** el script ejecuta `git pull --ff-only` en ese directorio, re-escribe el wrapper si hace falta, y reporta el SHA actualizado.

#### Scenario: Falta una dependencia básica

- **WHEN** el usuario ejecuta el comando `curl | bash` y no tiene `git` o `python3` instalados, o `python3` reporta una versión menor a 3.8
- **THEN** el script falla con código distinto de cero, imprime el binario faltante o la versión encontrada, y NO modifica ningún archivo del sistema.

#### Scenario: `~/.local/bin` no está en PATH

- **WHEN** el usuario completa el install y `~/.local/bin` no está en la variable `PATH` de su shell actual
- **THEN** el script imprime una instrucción explícita para agregarlo (e.g., `export PATH="$HOME/.local/bin:$PATH"` y dónde ponerlo), pero igualmente deja el wrapper escrito.

### Requirement: Subcomando `update`

`from-scratch update` SHALL re-sincronizar tanto el código de la CLI como el catálogo local con el del repo, ejecutando `git pull --ff-only` en `~/.from-scratch/` antes de aplicar cambios al directorio `~/.claude/`.

#### Scenario: Actualización con cambios disponibles

- **WHEN** el usuario ejecuta `from-scratch update` y el repo remoto tiene commits nuevos respecto al clone local
- **THEN** la CLI ejecuta `git pull --ff-only`, después lista los archivos del catálogo agregados (`+`), modificados (`~`) y sin cambios (`=`), pide confirmación, y aplica los cambios al directorio `~/.claude/` solo si el usuario confirma.

#### Scenario: Update sin cambios

- **WHEN** el usuario ejecuta `from-scratch update` y ni el código ni el catálogo tienen cambios remotos
- **THEN** la CLI ejecuta `git pull --ff-only` (que no trae nada), informa "todo está al día" y sale sin tocar archivos en `~/.claude/`.

#### Scenario: Cancelación durante update

- **WHEN** la CLI muestra los cambios del catálogo y el usuario responde "no" a la confirmación
- **THEN** ningún archivo en `~/.claude/` es modificado. El `git pull` previo permanece (el clone queda actualizado), pero esto no afecta la instalación visible.

#### Scenario: El clone local tiene cambios sin commitear

- **WHEN** el usuario ejecuta `from-scratch update` y `~/.from-scratch/` tiene modificaciones locales que harían fallar `git pull --ff-only`
- **THEN** la CLI captura el error de git, imprime un mensaje específico ("tu clone local en `~/.from-scratch` tiene cambios; revisalo con `git status` o re-cloná"), y sale sin tocar `~/.claude/`.

#### Scenario: El pull trajo cambios en el código de la CLI

- **WHEN** el `git pull --ff-only` actualiza archivos en `src/` además del catálogo
- **THEN** la CLI completa la sincronización con el código viejo (el que está en memoria) e imprime al final un aviso explícito: "Se actualizó el código de la CLI; la próxima ejecución usará la versión nueva".

### Requirement: Feedback visual moderno y consistente

La CLI SHALL proveer feedback visual coherente entre subcomandos: spinners en operaciones que toman tiempo, prompts interactivos para confirmaciones, y resumen de cierre tras cada operación. La implementación usa primitivas de la stdlib de Python (sin dependencias externas).

#### Scenario: Indicador durante operaciones lentas

- **WHEN** la CLI está ejecutando `git pull` o copiando muchos archivos
- **THEN** muestra un indicador (spinner o equivalente textual) con un mensaje descriptivo de la operación en curso.

#### Scenario: Resumen final tras operación exitosa

- **WHEN** un subcomando termina su trabajo correctamente
- **THEN** la CLI imprime un mensaje de cierre que indica qué se hizo (archivos tocados, commits aplicados) y, cuando aplica, qué tiene que hacer el usuario a continuación (por ejemplo, "Reiniciá Claude Code").

## ADDED Requirements

### Requirement: Detección de instalación previa vía npm

`install.sh` SHALL detectar la presencia de una instalación previa de `from-scratch` realizada vía `npm i -g` antes de proceder, y SHALL pedir al usuario que la desinstale manualmente — sin ejecutar `npm uninstall` automáticamente.

#### Scenario: Instalación previa detectada

- **WHEN** `install.sh` ejecuta `npm root -g 2>/dev/null` y el directorio `from-scratch` existe dentro de esa ruta
- **THEN** el script imprime un mensaje explícito ("Detecté una instalación previa vía npm. Antes de continuar ejecutá `npm uninstall -g from-scratch` y volvé a correr este install"), sale con código distinto de cero, y NO escribe ni modifica ningún archivo.

#### Scenario: Sin instalación previa npm

- **WHEN** `install.sh` ejecuta `npm root -g 2>/dev/null` y el directorio `from-scratch` no existe ahí (o `npm` no está disponible)
- **THEN** el script continúa con la instalación normal sin mencionar npm.

## REMOVED Requirements

### Requirement: Handshake de versión con el catálogo

**Reason**: En el modelo clone-and-run, el código de la CLI y el catálogo viajan juntos en el mismo repo y se actualizan atómicamente con `git pull`. El escenario "binario viejo + catálogo nuevo" no puede ocurrir, lo que vuelve al handshake innecesario.

**Migration**: El campo `requires_binary` se elimina de `catalog/catalog.json`. Si por alguna razón está presente en el JSON, la CLI lo ignora silenciosamente (sin warning) — no hay versionado independiente del binario que comparar. La sección "Política de versionado y handshake" del README se elimina o reemplaza con una nota que explica el modelo nuevo.
