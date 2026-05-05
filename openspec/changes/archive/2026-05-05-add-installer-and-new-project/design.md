## Context

Hoy, los desarrolladores que quieren empezar un proyecto nuevo o sumar capacidades a uno existente repiten manualmente pasos que un asistente como Claude Code podría hacer por ellos. Para que Claude Code pueda hacer ese trabajo, necesita tener instalados ciertos comandos (slash commands) y skills, y esos comandos deben mantenerse actualizados a través del tiempo.

`from-scratch` cumple ese rol de "instalador y gestor". No construye proyectos por sí mismo; equipa a Claude Code con las herramientas que después construyen los proyectos. Esta separación es deliberada: queremos que toda la inteligencia de scaffolding viva en prompts que Claude lee y obedece, no en código de la CLI.

Stakeholders: el autor (Diego Martínez), revisores especialistas (UX, IA), y los usuarios finales (desarrolladores de Despegar y otros que usen Claude Code).

Constraints relevantes:

- Distribución interna, sin registry pública de npm.
- Toolchain estándar de la industria: Node + TypeScript + Clack.
- El usuario debe poder reiniciar Claude Code después de `init`/`update` y encontrar los comandos disponibles inmediatamente, sin pasos adicionales.

## Goals / Non-Goals

**Goals:**

- Que `from-scratch` se instale con un único comando (`npm i -g github:dimartinez/from-scratch`).
- Que `from-scratch init` deje todo listo para que el usuario pueda usar `/new-project` en Claude Code tras un reinicio.
- Que sumar un stack nuevo al catálogo sea, para el autor, agregar un archivo en el repo y nada más.
- Que la experiencia visual de la CLI se sienta moderna y amigable, con feedback claro en cada paso.
- Que la herramienta nunca toque código del usuario sin avisar, y nunca aplique cambios sin confirmación explícita.
- Que el modelo conceptual sea recursivo: el mismo molde de "delegación con rol" sirve para `/new-project` y para cualquier comando futuro.

**Non-Goals:**

- No es un scaffolder propio: no genera código, solo replica archivos de catálogo y delega el scaffolding real a Claude.
- No es un package manager genérico: solo gestiona archivos para `~/.claude/`.
- No mantiene retrocompatibilidad de formato a perpetuidad: cuando el formato cambia, la versión vieja deja de servir y se exige upgrade.
- No soporta múltiples catálogos en v1 (solo el repo oficial `dimartinez/from-scratch`).
- No tiene mecanismo de auto-update silencioso del binario: siempre lo decide el usuario.
- No publica a la registry pública de npm.

## Decisions

### 1. La CLI es un "copiador inteligente", no un generador

**Decisión:** `from-scratch` solo descarga archivos del repo y los coloca en `~/.claude/`. Toda la lógica de scaffolding vive en los prompts (los archivos del catálogo) que Claude Code después interpreta.

**Por qué:** Mantener la inteligencia en prompts permite que iterar sobre el comportamiento sea editar markdown, no recompilar la CLI. Es además consistente con el espíritu de Claude Code: del otro lado hay un modelo que lee y razona, así que no hace falta codificar pasos rígidos.

**Alternativa descartada:** una CLI que ejecute pasos imperativos por sí misma (clonar, copiar archivos, correr comandos shell). Se descartó porque acopla la inteligencia con la herramienta de distribución, y mata la flexibilidad que da delegar en Claude.

### 2. Distribución vía `npm i -g github:...`, sin registry pública

**Decisión:** El binario se instala apuntando directo al repo de GitHub.

**Por qué:** Es uso interno, no queremos publicar en la registry pública. npm soporta nativamente instalar desde un repo Git, así que evitamos cualquier paso adicional de publishing y el repo cumple doble rol (fuente del binario y fuente del catálogo).

**Alternativa descartada:** registry privada (npm Enterprise, Artifactory). Se descartó por overhead operativo desproporcionado para una herramienta interna.

### 3. Lenguaje y stack: Node + TypeScript + @clack/prompts

**Decisión:** TypeScript sobre Node, con `@clack/prompts` como librería de UI.

**Por qué:** Es el estándar de facto para CLIs modernas distribuidas vía npm. El usuario ya tiene Node instalado (es prerrequisito de Claude Code). `@clack/prompts` es la librería usada por la mayoría de los `create-*` modernos (`create-astro`, `create-svelte`, etc.) y entrega el aspecto visual moderno que buscamos.

**Alternativas descartadas:**
- Go o Rust: dan binarios standalone sin dependencias, pero salimos del ecosistema npm y obligamos a un canal de distribución distinto.
- JavaScript plano: pierde la red de seguridad de tipos en una herramienta que va a evolucionar.

### 4. Encapsulación en `~/.claude/from-scratch/` para datos internos

**Decisión:** Los archivos que Claude Code consume (slash commands, skills) van en sus carpetas estándar (`~/.claude/commands/`, `~/.claude/skills/`). Los archivos internos de `from-scratch` (catálogo de stacks, metadata) van en un subdirectorio propio: `~/.claude/from-scratch/`.

**Por qué:** Evita colisiones futuras con convenciones que Claude Code pueda introducir. Deja claro qué archivos son responsabilidad de Claude Code y cuáles son nuestros. Si mañana hay que limpiar todo lo que `from-scratch` instaló, basta borrar `~/.claude/from-scratch/` más los archivos puntuales en `commands/`.

**Alternativa descartada:** poner todo "plano" en `~/.claude/`. Se descartó por riesgo de colisión y por mezclar responsabilidades.

### 5. Modelo de actualización: "diff y aplicar" para el catálogo, "reinstall manual" para el binario

**Decisión:** El catálogo se actualiza con `from-scratch update`, que muestra qué cambia y pide confirmación antes de tocar archivos. El binario se actualiza re-ejecutando el `npm i -g ...`.

**Por qué:** Separa dos cosas que tienen frecuencias y consecuencias distintas. Cambiar el catálogo es barato y frecuente; cambiar el binario es raro y deliberado. Mezclarlos en un único `update` mágico esconde lo que está pasando.

**Alternativa descartada:** auto-update transparente del binario. Se descartó porque mete sorpresas en la herramienta y choca con el principio de "el usuario siempre tiene veto".

### 6. Handshake de versión catálogo ↔ binario

**Decisión:** Cada versión del catálogo declara la versión mínima de binario requerida. El binario, al arrancar, lee esa declaración y se planta si no la cumple, mostrando el comando exacto para actualizar.

**Por qué:** Permite romper formato cuando hace falta sin acumular código de retrocompatibilidad. El usuario nunca queda en estado "raro": o todo funciona o el mensaje le dice exactamente qué hacer.

**Alternativa descartada:** compatibilidad hacia atrás indefinida. Se descartó por costo de mantenimiento y por la preferencia explícita del autor.

### 7. Sobreescritura ciega de catálogo en v1

**Decisión:** En v1, `update` sobreescribe los archivos locales con los del repo, sin detectar ediciones manuales del usuario.

**Por qué:** Asumimos que en v1 los usuarios no editan los archivos del catálogo a mano. La detección de conflictos local-vs-repo agrega complejidad real (3-way merge, prompt de resolución) que no se justifica todavía.

**Alternativa para versiones futuras:** detección de archivos modificados localmente y prompt de resolución (sobreescribir / mantener / mostrar diff).

### 8. Comandos como prompts ("delegación con rol")

**Decisión:** Cada slash command instalado por `from-scratch` es un archivo markdown que define un **rol** (cómo debe encarar la tarea Claude) y un **objetivo** (a dónde debe llegar), sin dictar pasos rígidos. Claude lo lee al ejecutarse y decide cómo cumplirlo.

**Por qué:** Aprovecha la capacidad de razonamiento de Claude. Permite que el comando se adapte a diferencias entre templates (un README distinto, un paso extra, un error inesperado). Mantiene el tamaño del catálogo chico (un comando es texto, no un script).

**Alternativa descartada:** comandos como recetas paso-a-paso. Se descartó porque cada cambio en un template obligaría a actualizar el comando, y porque pierde lo que hace especial a Claude Code.

### 9. Stack como archivo declarativo mínimo

**Decisión:** Cada stack es un archivo con tres campos visibles: nombre, descripción corta, URL del template. El resto de la información (estructura, pasos de setup, dependencias) vive dentro del template, en su README, y la lee Claude en tiempo de ejecución.

**Por qué:** "Cada cosa en un solo lugar". Si el archivo de stack también describiera estructura o pasos, duplicaría información del README y se desincronizarían.

### 10. Formato idiomático: frontmatter YAML en archivos markdown

**Decisión:** Tanto los slash commands del catálogo (`commands/new-project.md`) como los archivos de stack (`stacks/java.md`) usan **frontmatter YAML** delimitado por `---` para sus metadatos, y markdown libre debajo para el contenido de prompt o documentación.

Para `commands/new-project.md`, el frontmatter sigue el contrato estándar de slash commands de Claude Code: `description` (línea visible en el menú de `/`) y, si en el futuro hace falta, `argument-hint` y `allowed-tools`. El cuerpo markdown debajo es el prompt — el rol y objetivo descritos en el spec de `new-project-command`.

Para `stacks/<id>.md`, el frontmatter declara los tres campos: `name` (nombre visible), `description` (descripción corta), `template_url` (URL del template). El cuerpo markdown queda disponible para notas humanas opcionales que la CLI ignora; Claude solo consume el frontmatter.

**Por qué:** Es el formato idiomático del ecosistema Claude Code (lo usan los slash commands, los sub-agentes, las skills). Reutilizarlo nos da: (a) familiaridad inmediata para cualquier autor de catálogo, (b) parsers maduros disponibles en npm, (c) consistencia visual al inspeccionar archivos a mano. Inventar un formato propio (JSON puro, keys en el cuerpo del markdown, etc.) sería reinventar sin valor agregado.

**Alternativa descartada:** archivo `stacks/<id>.json` o keys planos en el cuerpo del markdown. Se descartó por inconsistencia con el resto del ecosistema y por degradar la legibilidad humana.

### 11. Distinción entre archivos propios y archivos del usuario en `~/.claude/commands/`

**Decisión:** La CLI mantiene en `~/.claude/from-scratch/.state.json` un campo `installed_files` con la lista exacta de paths (relativos a `~/.claude/`) que `from-scratch` instaló en zona Claude Code (`commands/`, y a futuro `skills/`, `agents/`). Antes de escribir un archivo en zona Claude Code, la CLI verifica:

1. Si el destino no existe en disco: lo crea normalmente.
2. Si el destino existe y figura en `installed_files`: lo trata como propio y procede (sobreescritura controlada en `update`).
3. Si el destino existe pero NO figura en `installed_files`: lo trata como archivo del usuario y se planta. En `init` y `update`, muestra el mensaje de error "conflicto de nombre con archivo preexistente" (ver UX) y deja al usuario resolver (renombrar el suyo, o pasar `--force` que lo respalda a `<archivo>.bak.<timestamp>` antes de pisar).

Para archivos en zona interna (`~/.claude/from-scratch/`) la regla no aplica: esa zona es de propiedad exclusiva de la CLI y se sobreescribe siempre.

Cuando un archivo se desinstala (porque desapareció del catálogo), la CLI solo lo borra si figura en `installed_files`; si el path está ocupado por algo que la CLI no puso, lo deja intacto y avisa.

**Por qué:** `~/.claude/commands/` es territorio compartido: el usuario puede tener comandos personales ahí desde antes (o creados con otra herramienta), y `from-scratch` no es dueño exclusivo del directorio. Pisar a ciegas un comando del usuario sería el peor modo de falla posible. El registro `installed_files` da una respuesta directa a "¿este archivo es mío o del usuario?" sin recurrir a heurísticas frágiles (timestamps, hashes).

**Alternativa descartada:** namespace por subcarpeta (instalar en `~/.claude/commands/from-scratch/<nombre>.md`). Se descartó porque rompe la convención idiomática de Claude Code, donde los slash commands viven planos en `commands/` y se referencian por nombre simple (`/new-project`, no `/from-scratch/new-project`).

### 12. Manifest extensible por tipo de artefacto

**Decisión:** El manifest del catálogo (`catalog.json` o equivalente) NO mapea archivos a destinos individualmente. En cambio, declara una lista de **artefactos** donde cada artefacto tiene `kind`, `source` (path dentro del catálogo) y `destination_zone` (`claude_code` o `internal`). La CLI conoce un mapeo `kind → ruta concreta` para cada tipo soportado por la versión del binario:

- `kind: command` → `~/.claude/commands/<nombre>` (zona `claude_code`)
- `kind: stack` → `~/.claude/from-scratch/stacks/<nombre>` (zona `internal`)

Cuando una versión futura del catálogo introduzca `kind: skill`, `kind: agent` o `kind: hook`, el manifest los listará con el mismo formato; los binarios viejos verán un `kind` desconocido y se plantarán con mensaje claro ("este artefacto requiere una versión más nueva del binario") gracias al handshake de versión.

**Por qué:** Mantiene el formato del manifest estable a través del tiempo. Agregar un nuevo tipo de artefacto en el futuro es: (a) declarar el `kind` nuevo en el catálogo, (b) bumpear `requires_binary`, (c) implementar el mapeo en el binario nuevo. Las instalaciones viejas reciben un mensaje accionable (upgrade), no un crash silencioso. Esto cumple el goal de "agregar tipos de artefactos sin romper instalaciones viejas".

**Alternativa descartada:** mapear cada archivo individualmente con `source` + `destination_path` literal. Se descartó porque acopla el catálogo a paths específicos de Claude Code que pueden cambiar, y duplica información (el `kind` ya determina el destino).

## UX de la CLI (cómo se vive desde la terminal)

Esta sección define cómo se siente usar `from-scratch` paso a paso. Es el contrato visible al usuario; la implementación debe respetarlo.

### Operaciones con feedback visible

Toda operación que pueda durar más de ~1 segundo lleva feedback explícito. Lista exhaustiva:

- **Descarga del manifest** (red): spinner con texto `Buscando catálogo en GitHub...`. Al terminar, el spinner se reemplaza por una línea estática `Catálogo encontrado (vX.Y.Z, N archivos).`.
- **Handshake de versión** (instantáneo en general, pero puede dar mensaje de error largo): no lleva spinner; si falla, va directo al mensaje de error accionable (ver más abajo).
- **Descarga de archivos del catálogo** (red, varios archivos): spinner con contador `Descargando archivos (i/N): <nombre>`. Si la lista es chica (≤3), basta `Descargando archivos...`.
- **Copia a disco** (filesystem): spinner `Aplicando cambios en ~/.claude/...`. Al terminar, una línea por categoría: `Instalados: N`, `Actualizados: N`, `Sin cambios: N`.
- **Cálculo de diff en `update`**: spinner `Comparando con tu copia local...`.

Cada spinner DEBE tener un mensaje de éxito y uno de error. El mensaje de éxito reemplaza al spinner (no se acumulan líneas de "...spinning..." en el output final).

### Confirmaciones y previews

La regla es: **nunca sorprender al usuario con cambios en disco**. Antes de cada confirmación se muestra el preview correspondiente.

- **`init` (primera vez)**: antes de la confirmación, la CLI muestra (a) la versión del catálogo que va a instalar, (b) la lista de archivos que va a crear, agrupados por destino (`~/.claude/commands/`, `~/.claude/from-scratch/stacks/`, etc.), (c) el espacio total estimado. La confirmación es una sola pregunta: `¿Instalar el catálogo en ~/.claude/?` (default: sí).
- **`init` sobre instalación previa**: la CLI detecta el estado y, en lugar de preguntar de nuevo, **sugiere `update`** con un mensaje del estilo `Detecté una instalación previa. Para sincronizar cambios usá: from-scratch update`. Solo procede como `init` destructivo si el usuario lo invoca con un flag explícito (`--force`), y en ese caso muestra preview claro de qué se va a sobrescribir antes de pedir la confirmación.
- **`update` con cambios**: muestra un diff en formato escaneable — una línea por archivo con prefijo `+` (nuevo), `~` (modificado) o `-` (eliminado). Los `=` (sin cambios) NO se listan archivo por archivo: se resumen al final como `(N archivos sin cambios)`. La confirmación es: `¿Aplicar estos cambios?` (default: sí).
- **`update` sin cambios**: no hay confirmación. Sale con un mensaje único `Tu catálogo está al día (vX.Y.Z).` y un hint sobre cuándo correr `update` de vuelta.

### Mensajes de error: qué falló, por qué, qué hacer

Todo error documentado en este spec se reporta con tres piezas obligatorias: **qué falló**, **por qué** (cuando se sabe) y **qué comando ejecutar** para resolverlo. Plantillas:

- **Red caída / GitHub inaccesible**:
  ```
  No pude alcanzar GitHub para descargar el catálogo.
  Causa probable: sin conexión, o GitHub bloqueado en tu red.
  Probá: revisar tu conexión y volver a correr `from-scratch <subcomando>`. Si es persistente, verificá tu acceso a github.com/dimartinez/from-scratch.
  ```
- **Manifest inválido / parseo fallido**:
  ```
  El catálogo descargado tiene un formato que no entiendo.
  Causa probable: el binario está desactualizado respecto al catálogo.
  Probá: `npm i -g github:dimartinez/from-scratch` para actualizar el binario.
  ```
- **Handshake de versión** (caso ya cubierto en el spec; la plantilla la respeta):
  ```
  Tu binario from-scratch v<actual> es más viejo que lo que el catálogo necesita (>= v<requerido>).
  Probá: `npm i -g github:dimartinez/from-scratch`.
  ```
- **Permisos sobre `~/.claude/`**:
  ```
  No tengo permisos para escribir en ~/.claude/<ruta>.
  Causa probable: el directorio fue creado con otro usuario o tiene permisos restrictivos.
  Probá: `ls -ld ~/.claude` para revisar permisos. Si el dueño no sos vos: `sudo chown -R $(whoami) ~/.claude`.
  ```
- **Archivo de stack inválido** (en el repo, detectado al sincronizar):
  ```
  El stack `<nombre>` tiene un formato inválido (falta el campo <X>).
  Causa probable: el repo tiene un stack mal formado.
  Probá: reportar el problema en github.com/dimartinez/from-scratch/issues. El resto del catálogo se sincronizó igual.
  ```
- **Frontmatter inválido en un comando del catálogo** (al validar antes de copiar):
  ```
  El comando `<nombre>` del catálogo tiene un frontmatter YAML que no se puede parsear.
  Causa probable: el repo tiene un commit con un comando mal formado, o tu binario no entiende un campo nuevo.
  Probá: `npm i -g github:dimartinez/from-scratch` para descartar binario viejo. Si persiste, reportar en github.com/dimartinez/from-scratch/issues.
  ```
- **Conflicto de nombre con archivo preexistente del usuario** (zona Claude Code):
  ```
  Ya existe un archivo en ~/.claude/commands/<nombre> que from-scratch no instaló.
  Causa probable: tenés un comando propio con el mismo nombre, o lo creó otra herramienta.
  Probá: renombrarlo si querés conservarlo, o re-correr con `--force` (la CLI hará un backup en <archivo>.bak.<timestamp> antes de pisar).
  ```
- **`kind` de artefacto desconocido en el manifest** (catálogo más nuevo que el binario, no detectado por el handshake principal):
  ```
  El catálogo declara un artefacto de tipo `<kind>` que este binario no entiende.
  Causa probable: el catálogo introdujo un tipo de artefacto nuevo y tu binario está desactualizado.
  Probá: `npm i -g github:dimartinez/from-scratch` para actualizar.
  ```

### Idempotencia y recuperación de estado parcial

`init` y `update` son idempotentes: re-ejecutarlos sin cambios remotos no toca archivos ni produce output ruidoso (más allá del mensaje "todo al día").

Para detectar interrupciones a mitad de camino, la CLI mantiene un archivo `~/.claude/from-scratch/.state.json` con los campos: `last_sync_started_at`, `last_sync_completed_at`, `installed_files` (paths relativos a `~/.claude/` que la CLI instaló y considera propios — ver Decisión 11), `catalog_version` (versión del catálogo aplicada en el último sync exitoso), y `binary_version` (versión del binario que escribió el state). Si al arrancar `from-scratch` encuentra `started > completed`, sabe que hubo una interrupción previa y avisa al usuario:

```
Detecté una sincronización anterior interrumpida. Voy a reanudarla.
```

Luego procede como un `update` normal (recalcula el diff contra el repo, lo cual sobreescribe cualquier estado a medio escribir).

### Cancelación segura (Ctrl+C)

Las escrituras a disco se hacen de manera atómica: cada archivo se escribe primero en `<destino>.tmp` y solo se hace `rename` al destino final cuando termina la escritura. Si el usuario manda Ctrl+C en cualquier momento:

- Antes de cualquier `rename`: no quedó ningún cambio aplicado. La CLI captura la señal, limpia archivos `.tmp` que haya creado, marca `last_sync_completed_at = null` en el state file, e imprime `Cancelado. No se modificó ningún archivo de tu catálogo.`.
- Durante la fase de `rename`s (que es rápida): puede quedar a mitad. La próxima ejecución detectará el state file inconsistente y reanudará.

Las descargas de red también se interrumpen limpio: la cancelación durante un fetch aborta el request, no deja archivos parciales en disco (porque la escritura es post-descarga, no streaming a destino final).

### Output consistente y escaneable

- **Sin emojis**: el output es texto plano. La estética viene de Clack (cajas, separadores, color sutil), no de iconografía.
- **Cada subcomando termina con un bloque de resumen** con la misma forma:
  ```
  Resumen
    Instalados: 3
    Actualizados: 1
    Sin cambios: 12
  Próximo paso: reiniciá Claude Code para que reconozca los nuevos comandos.
  ```
- **Errores siempre rojos, con prefijo `Error:`**. Warnings (no bloqueantes) en amarillo con prefijo `Aviso:`. Éxitos sin color especial: el contexto del bloque ya lo deja claro.
- **El "próximo paso" es obligatorio**: cada comando termina sugiriendo qué hacer ahora (ver siguiente sección).

### Discoverability y enseñanza

- **`from-scratch` sin argumentos**: imprime el `--help` (no error, no prompt). El help lista los subcomandos con una línea cada uno y un ejemplo de uso al final.
- **`from-scratch --help` y `from-scratch <subcomando> --help`**: implementados explícitamente. El help de cada subcomando incluye al menos un ejemplo concreto.
- **Subcomando inválido** (`from-scratch lalala`): mensaje del estilo `No conozco el subcomando "lalala". Subcomandos disponibles: init, update. Probá: from-scratch --help`.
- **Hints contextuales después de cada subcomando exitoso**:
  - Tras `init`: `Listo. Reiniciá Claude Code y probá /new-project. Cuando quieras traer novedades del catálogo, corré: from-scratch update`.
  - Tras `update` con cambios: `Listo. Reiniciá Claude Code para que tome los cambios.`.
  - Tras `update` sin cambios: `Tu catálogo está al día. Volvé a correr update cuando quieras revisar si hay novedades.`.
- **Hint en `init` cuando ya hay instalación**: ver sección de Confirmaciones (sugiere `update` en lugar de re-instalar).

## Risks / Trade-offs

- **El catálogo depende de GitHub estar disponible.** → Mitigación: una vez hecho `init`, todo vive en disco; solo `update` requiere red. El usuario sigue trabajando offline.
- **Sobreescritura ciega de v1 puede sorprender a un usuario que editó archivos.** → Mitigación: documentar claramente que `~/.claude/from-scratch/` no debe editarse a mano. En el futuro, agregar detección de modificaciones.
- **El comando `/new-project` depende de que el README del template sea seguible por Claude.** → Mitigación: tratar al README como una superficie de calidad (parte del template, no del catálogo). Si un README es ambiguo, se mejora ahí, no en `from-scratch`.
- **Dependencia de Node ya instalado en la máquina del usuario.** → Aceptado: cualquier usuario de Claude Code ya tiene Node.
- **El handshake de versión exige que el autor recuerde subir la versión mínima cuando hace breaking changes.** → Mitigación: documentar el flujo de release en el repo; eventualmente, automatizar.
- **Como herramienta interna, el descubrimiento es manual.** → Aceptado: en v1 el target es chico y se comparte por canales internos (Slack, README).

## Migration Plan

No aplica: esta es la versión inicial del proyecto. No hay versiones previas que migrar ni usuarios que rollbackear.

## Open Questions

- ¿Qué política de versionado seguimos? (semver clásico, calendar versioning, etc.) Pendiente de definir antes del primer release.
- ¿El comando `/new-project` debería instalarse global o por proyecto? Actualmente asumimos global; un revisor de UX podría sugerir distinto.
- ¿La descripción corta del stack tiene un límite explícito de caracteres? Recomendación inicial: ~80, para que entre en una línea de terminal estándar, pero queda abierto.
- ¿Cómo se siente la experiencia de "leí README y armé el proyecto" cuando el README es largo o ambiguo? Es candidato natural para que el especialista en IA opine.
