# from-scratch

CLI que instala y mantiene actualizado el catálogo de comandos y stacks de Claude Code.

## ¿Qué hace?

`from-scratch` copia archivos desde este repo a tu directorio `~/.claude/`, dejando disponibles comandos (`/new-project` y más en el futuro) para usarlos dentro de Claude Code.

Separación de responsabilidades:
- **La CLI** descarga archivos y los coloca en el lugar correcto.
- **Los comandos de Claude Code** (archivos `.md` en `~/.claude/commands/`) contienen la inteligencia de scaffolding — Claude los lee y razona sobre ellos.

## Instalación

```bash
npm i -g github:dimartinez/from-scratch
```

Requiere Node.js >= 18.

## Uso

### Primera instalación

```bash
from-scratch init
```

Descarga el catálogo, te muestra qué va a instalar, y pide confirmación antes de tocar cualquier archivo.

Tras la instalación, **reiniciá Claude Code** para que reconozca los comandos nuevos.

### Actualizaciones

```bash
from-scratch update
```

Compara el catálogo remoto con tu copia local, muestra los cambios, y aplica solo lo que confirmás.

Si hay conflicto con un archivo que no instaló la CLI, te avisa y no lo pisa sin `--force`.

### Forzar sobreescritura

```bash
from-scratch init --force
from-scratch update --force
```

Sobreescribe archivos existentes con conflicto. Siempre hace backup (`<archivo>.bak.<timestamp>`) antes de pisar.

### Ayuda

```bash
from-scratch --help
from-scratch init --help
from-scratch update --help
```

## Comandos incluidos

- `/new-project` — Crea un proyecto nuevo desde un template de stack.

## Stacks disponibles

| Nombre | Descripción |
|--------|-------------|
| Java (Despegar) | Microservicio Java estándar Despegar |

## Agregar un stack nuevo

1. Creá un archivo en `catalog/stacks/<nombre>.md` con el siguiente frontmatter:

   ```yaml
   ---
   name: Mi Stack
   description: Descripción corta (max ~80 chars)
   template_url: github.com/org/mi-template
   ---
   ```

2. Actualizá `catalog/catalog.json` agregando la entrada:

   ```json
   { "kind": "stack", "source": "stacks/<nombre>.md" }
   ```

3. Los usuarios verán el stack nuevo tras su próximo `from-scratch update`.

No es necesario cambiar código de la CLI para agregar un stack.

## Contrato del archivo de stack

Cada archivo de stack (`catalog/stacks/<id>.md`) debe tener frontmatter YAML con los tres campos requeridos:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `name` | string | Nombre visible en la lista de stacks |
| `description` | string | Descripción corta (una línea, ~80 chars) |
| `template_url` | string | URL del repo Git del template |

El cuerpo markdown (después del frontmatter) es libre y la CLI lo ignora. Puede usarse para notas humanas.

## Contrato de los slash commands instalados

Los archivos en `catalog/commands/<nombre>.md` siguen el formato estándar de Claude Code:

- Frontmatter YAML con al menos el campo `description` (línea visible en el menú de `/`)
- Cuerpo markdown con el prompt para Claude (rol + objetivo + restricciones)

## Política de versionado y handshake

Usamos **semver**. El archivo `catalog/catalog.json` declara `requires_binary` con la versión mínima del binario requerida.

Al ejecutarse, la CLI lee ese campo y se planta si su versión es menor:

```
Tu binario from-scratch vX.Y es más viejo que lo que el catálogo necesita (>= vZ.W).
Probá: `npm i -g github:dimartinez/from-scratch`.
```

**Cuando hacer un bump de `requires_binary`:** solo cuando el formato del catálogo o el comportamiento de la CLI cambia de manera no retrocompatible. Cambios puramente en contenido de comandos o stacks no requieren bump.

## Cómo funciona `~/.claude/`

```
~/.claude/
  commands/
    new-project.md    ← instalado por from-scratch (registrado en state)
  from-scratch/
    stacks/
      java.md          ← instalado por from-scratch
    .state.json        ← metadata interna (no editar a mano)
```

`from-scratch` registra en `~/.claude/from-scratch/.state.json` la lista exacta de archivos que instaló. Antes de sobreescribir un archivo en `~/.claude/commands/`, verifica si lo instaló ella misma. Si el archivo existe pero no fue instalado por la CLI, avisa y no pisa.
