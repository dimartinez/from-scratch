## ADDED Requirements

### Requirement: Instalación global desde el repo de GitHub

La CLI `from-scratch` SHALL ser instalable globalmente con `npm i -g github:dimartinez/from-scratch`, sin necesidad de publicar en la registry pública de npm.

#### Scenario: Instalación inicial desde el repo

- **WHEN** un usuario con Node.js instalado ejecuta `npm i -g github:dimartinez/from-scratch`
- **THEN** el binario `from-scratch` queda disponible globalmente en su PATH y puede invocarse desde cualquier directorio.

#### Scenario: Actualización del binario

- **WHEN** el usuario re-ejecuta `npm i -g github:dimartinez/from-scratch` con una nueva versión publicada en `main`
- **THEN** la versión local del binario se reemplaza por la nueva sin pasos adicionales.

#### Scenario: Pin a versión específica

- **WHEN** el usuario ejecuta `npm i -g github:dimartinez/from-scratch#v1.0.0`
- **THEN** se instala la versión correspondiente al tag `v1.0.0` y permanece pineada hasta el próximo install.

### Requirement: Subcomando `init`

`from-scratch init` SHALL realizar la primera instalación del catálogo en la carpeta `~/.claude/` del usuario.

#### Scenario: Primer init en una máquina sin instalación previa

- **WHEN** el usuario ejecuta `from-scratch init` por primera vez
- **THEN** la CLI muestra un saludo, pide confirmación, descarga el catálogo, copia los archivos a `~/.claude/`, y reporta cada archivo instalado con feedback visual.

#### Scenario: Cancelación antes de aplicar cambios

- **WHEN** el usuario ejecuta `from-scratch init` y responde "no" a la confirmación inicial
- **THEN** la CLI sale sin haber tocado ningún archivo del disco.

#### Scenario: Re-ejecución de init sobre instalación existente

- **WHEN** el usuario ejecuta `from-scratch init` y ya hay archivos instalados previamente
- **THEN** la CLI sugiere usar `from-scratch update` en lugar de `init`, o se comporta como `update` con confirmación explícita.

### Requirement: Subcomando `update`

`from-scratch update` SHALL re-sincronizar el catálogo local con el del repo, mostrando los cambios al usuario antes de aplicarlos.

#### Scenario: Actualización con cambios disponibles

- **WHEN** el usuario ejecuta `from-scratch update` y el repo tiene archivos nuevos o modificados respecto a la copia local
- **THEN** la CLI lista los archivos agregados (`+`), modificados (`~`) y sin cambios (`=`), pide confirmación, y aplica los cambios solo si el usuario confirma.

#### Scenario: Update sin cambios

- **WHEN** el usuario ejecuta `from-scratch update` y el repo no tiene cambios respecto a la copia local
- **THEN** la CLI informa "todo está al día" y sale sin tocar archivos.

#### Scenario: Cancelación durante update

- **WHEN** la CLI muestra los cambios y el usuario responde "no" a la confirmación
- **THEN** ningún archivo es modificado en disco.

### Requirement: Feedback visual moderno y consistente

La CLI SHALL proveer feedback visual usando una librería estándar de la industria (`@clack/prompts` o equivalente), con una estética consistente entre subcomandos.

#### Scenario: Spinners durante operaciones de red

- **WHEN** la CLI está descargando archivos del repo
- **THEN** muestra un spinner con un texto descriptivo de la operación en curso.

#### Scenario: Resumen final tras operación exitosa

- **WHEN** un subcomando termina su trabajo correctamente
- **THEN** la CLI muestra un mensaje de cierre que indica qué se hizo y, cuando aplica, qué tiene que hacer el usuario a continuación (por ejemplo, "Reiniciá Claude Code").

### Requirement: Handshake de versión con el catálogo

La CLI SHALL leer la versión mínima de binario declarada por el catálogo y SHALL detenerse si su propia versión es menor a esa, mostrando instrucciones explícitas para actualizar.

#### Scenario: Catálogo exige versión mayor a la instalada

- **WHEN** el binario v1.2 se ejecuta y el catálogo declara `requires_binary >= v2.0`
- **THEN** la CLI imprime un mensaje que incluye la versión actual, la versión requerida, y el comando exacto para actualizar (`npm i -g github:dimartinez/from-scratch`), y sale sin aplicar cambios.

#### Scenario: Versiones compatibles

- **WHEN** la versión del binario es mayor o igual a la versión mínima declarada por el catálogo
- **THEN** la CLI procede normalmente.

### Requirement: Confirmación explícita antes de modificar archivos

La CLI SHALL pedir confirmación al usuario antes de escribir, modificar o eliminar cualquier archivo en `~/.claude/`.

#### Scenario: El usuario nunca pierde datos en silencio

- **WHEN** una operación va a tocar archivos en disco
- **THEN** la CLI describe los cambios planeados y espera una respuesta afirmativa antes de proceder.
