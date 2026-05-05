## ADDED Requirements

### Requirement: Un stack es un archivo declarativo mínimo

Cada stack SHALL ser representado como un único archivo dentro del directorio `stacks/` del catálogo, con tres campos visibles:

- **Nombre visible** (cómo aparece en la lista al usuario).
- **Descripción corta** (una línea, recomendación: hasta ~80 caracteres).
- **URL del template** (repositorio Git que contiene el proyecto base).

El archivo NO SHALL contener pasos de setup, dependencias, ni instrucciones de scaffolding: esa información vive en el README del template y la lee Claude en tiempo de ejecución.

#### Scenario: Stack válido

- **WHEN** el archivo `stacks/java.md` declara nombre "Java (Despegar)", descripción "Microservicio Java estándar Despegar", y URL `github.com/despegar/java-template`
- **THEN** el comando `/new-project` puede listar el stack con ese nombre y descripción, y delegar a Claude la URL como destino del clone.

#### Scenario: Stack sin alguno de los campos requeridos

- **WHEN** un archivo de stack carece del nombre visible, la descripción, o la URL del template
- **THEN** la CLI o el comando `/new-project` detecta el stack como inválido y lo reporta claramente al usuario, sin fallar silenciosamente.

### Requirement: Agregar un stack es agregar un archivo

Sumar un nuevo stack al catálogo SHALL ser una operación de "agregar un archivo nuevo en `stacks/` del repo". No SHALL requerir cambios en código de la CLI ni en otros archivos del catálogo.

#### Scenario: Nuevo stack en el repo

- **WHEN** el autor sube un archivo nuevo `stacks/node.md` al repo
- **THEN** tras `from-scratch update` el usuario ve "Node" como opción adicional en la lista de stacks de `/new-project`, sin haber actualizado el binario.

### Requirement: Inicialmente, un solo stack disponible (`java`)

Esta versión SHALL incluir exactamente un stack en el catálogo: `java`, basado en `github.com/despegar/java-template`.

#### Scenario: Stack Java listado por defecto

- **WHEN** el usuario ejecuta `from-scratch init` y luego invoca `/new-project` en Claude Code
- **THEN** la lista de stacks contiene exclusivamente la opción "Java (Despegar)".

### Requirement: La descripción corta es información para el usuario, no para Claude

La descripción corta SHALL existir para que el usuario pueda elegir entre stacks de forma informada al ver la lista. NO SHALL ser usada por Claude como input para el scaffolding (Claude se basa en el README del template, no en este texto).

#### Scenario: Descripción visible en la lista

- **WHEN** `/new-project` muestra la lista de stacks
- **THEN** cada opción aparece con su nombre visible seguido de su descripción corta, en una línea legible.
