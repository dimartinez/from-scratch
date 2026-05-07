## Why

El comando `new-project` configura un proyecto completo listo para trabajar con IA, pero no inicializa OpenSpec, una herramienta central del flujo de desarrollo spec-driven en Despegar. Al no incluirlo como paso explícito, el usuario no recibe feedback visual de que ocurrió, y si falla (por ejemplo, porque `openspec` no está instalado globalmente), el error queda silenciado dentro de la Fase 2.

## What Changes

- Se agrega un paso dedicado en el flujo de `new-project` para ejecutar `openspec init` en el proyecto recién clonado.
- El paso aparece como ítem separado en el `TodoWrite` para dar feedback visual explícito al usuario.
- Se verifica que `openspec` esté disponible en el sistema antes de ejecutar `openspec init`; si no lo está, se reporta un error accionable y se continúa con los pasos restantes (no se aborta el flujo).
- El paso se ubica al final de la Fase 2 (después del clone y configuración del template), antes del skills sync.

## Capabilities

### New Capabilities

- `new-project-openspec-init`: Inicialización de OpenSpec como paso explícito y visible dentro del flujo de `new-project`, con verificación de disponibilidad y manejo de error accionable.

### Modified Capabilities

- `new-project-command`: El flujo del comando agrega un paso en la Fase 2.

## Impact

- `catalog/commands/new-project.md`: se modifica el flujo y las instrucciones del Paso 2.
- Sin impacto en `src/`, `tests/`, ni en el catálogo de stacks.
- Requiere que el usuario tenga `openspec` instalado globalmente (`npm install -g @fission-ai/openspec`).
