# from-scratch

CLI que instala y mantiene actualizado el catálogo de comandos y stacks de Claude Code.

## ¿Qué hace?

`from-scratch` copia archivos desde este repo a tu directorio `~/.claude/`, dejando disponibles comandos (`/new-project`) para usarlos dentro de Claude Code.

- **La CLI** descarga archivos y los coloca en el lugar correcto.
- **Los comandos de Claude Code** (archivos `.md` en `~/.claude/commands/`) contienen la inteligencia de scaffolding — Claude los lee y razona sobre ellos.

## Instalación

Antes de instalar, necesitás tener disponible en tu sistema:
- `git`
- `python3` >= 3.8
- `bash`

```bash
curl -fsSL https://raw.githubusercontent.com/dimartinez/from-scratch/main/install.sh | bash
```

El script clona el repo en `~/.from-scratch/` e instala un wrapper en `~/.local/bin/from-scratch`.

Si `~/.local/bin` no está en tu `PATH`, el script te avisa y te muestra el comando para agregarlo:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc
```

Verificá que la instalación funcionó:

```bash
from-scratch --help
```

### Migración desde la versión npm

Si tenías `from-scratch` instalado con `npm install -g`, desinstalala primero:

```bash
npm uninstall -g from-scratch
```

Después corrés el `curl` de arriba normalmente.

## Uso

### Primera instalación del catálogo

```bash
from-scratch init
```

Muestra qué archivos va a instalar y pide confirmación antes de tocar cualquier archivo.

Tras la instalación, **reiniciá Claude Code** para que reconozca los comandos nuevos.

### Actualizaciones

```bash
from-scratch update
```

Hace `git pull` en `~/.from-scratch/`, compara el catálogo con tu copia local, muestra los cambios, y aplica solo lo que confirmás.

Comportamiento ante archivos con cambios locales:

- Archivos que **vos modificaste** después de que la CLI los instaló: la CLI los muestra en el listado con `!` pero los omite sin `--force`.
- Archivos que **no instaló la CLI** (existían antes): la CLI los muestra con `!` y no los pisa sin `--force`.

### Forzar sobreescritura

```bash
from-scratch init --force
from-scratch update --force
```

Sobreescribe archivos en conflicto. Siempre hace backup (`<archivo>.bak.<timestamp>`) antes de pisar.

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

## Cómo funciona internamente

```
~/.from-scratch/          <- clone del repo (desde donde corre la CLI)
~/.local/bin/from-scratch <- wrapper bash
~/.claude/
  commands/
    new-project.md    <- instalado por from-scratch (registrado en state)
  from-scratch/
    stacks/
      java.md          <- instalado por from-scratch
    .state.json        <- metadata interna (no editar a mano)
```

`from-scratch` registra en `~/.claude/from-scratch/.state.json` la lista exacta de archivos que instaló. Antes de sobreescribir un archivo en `~/.claude/commands/`, verifica si lo instaló ella misma. Si el archivo existe pero no fue instalado por la CLI, avisa y no pisa.

## Problemas frecuentes

**`from-scratch: command not found` después de instalar**

`~/.local/bin` no está en tu `PATH`. Agregalo:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc
```

**`from-scratch init` reporta archivos en conflicto (`!`) y no instala**

Hay archivos en `~/.claude/commands/` que no instaló la CLI. Revisalos manualmente y, si querés que la CLI los pise haciendo backup, usá `--force`:

```bash
from-scratch init --force
```

**`from-scratch update` omite archivos que vos modificaste**

La CLI detectó que editaste esos archivos después de instalarlos y los saltea para no pisar tus cambios. Si querés actualizar igual (con backup), usá `--force`:

```bash
from-scratch update --force
```

**Los comandos no aparecen en Claude Code después de `init`**

Reiniciá Claude Code. Los slash commands se cargan al arrancar; no se detectan en caliente.

## Desarrollo de la CLI

Esta sección es para quien clone el repo para modificar el código de la CLI. Si solo querés usar `from-scratch`, alcanza con la sección de [Instalación](#instalación).

### Setup inicial

```bash
git clone https://github.com/dimartinez/from-scratch.git
cd from-scratch
python3 -m venv .venv
.venv/bin/pip install pytest
```

### Flujo de trabajo

Editás archivos en `src/` directamente — no hay compilación. Los cambios son efectivos de inmediato.

Comandos útiles durante el desarrollo:

| Comando | Para qué |
|---------|----------|
| `python3 -m pytest` | Correr todos los tests |
| `python3 -m pytest tests/catalog/` | Correr tests de un módulo |
| `PYTHONPATH=. python3 src/cli.py --help` | Probar la CLI directamente |
