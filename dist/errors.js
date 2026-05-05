export function errorUnknownKind(kind) {
    return [
        `El catálogo declara un artefacto de tipo \`${kind}\` que este binario no entiende.`,
        `Causa probable: el catálogo introdujo un tipo de artefacto nuevo y tu binario está desactualizado.`,
        `Probá: \`npm i -g github:dimartinez/from-scratch\` para actualizar.`,
    ].join('\n');
}
export function errorNetworkDown(subcommand) {
    return [
        `No pude alcanzar GitHub para descargar el catálogo.`,
        `Causa probable: sin conexión, o GitHub bloqueado en tu red.`,
        `Probá: revisar tu conexión y volver a correr \`from-scratch ${subcommand}\`. Si es persistente, verificá tu acceso a github.com/dimartinez/from-scratch.`,
    ].join('\n');
}
export function errorManifestInvalid() {
    return [
        `El catálogo descargado tiene un formato que no entiendo.`,
        `Causa probable: el binario está desactualizado respecto al catálogo.`,
        `Probá: \`npm i -g github:dimartinez/from-scratch\` para actualizar el binario.`,
    ].join('\n');
}
export function errorVersionHandshake(current, required) {
    return [
        `Tu binario from-scratch v${current} es más viejo que lo que el catálogo necesita (>= v${required}).`,
        `Probá: \`npm i -g github:dimartinez/from-scratch\`.`,
    ].join('\n');
}
export function errorPermissions(path) {
    return [
        `No tengo permisos para escribir en ~/.claude/${path}.`,
        `Causa probable: el directorio fue creado con otro usuario o tiene permisos restrictivos.`,
        `Probá: \`ls -ld ~/.claude\` para revisar permisos. Si el dueño no sos vos: \`sudo chown -R $(whoami) ~/.claude\`.`,
    ].join('\n');
}
export function errorStackInvalid(name, missingField) {
    return [
        `El stack \`${name}\` tiene un formato inválido (falta el campo ${missingField}).`,
        `Causa probable: el repo tiene un stack mal formado.`,
        `Probá: reportar el problema en github.com/dimartinez/from-scratch/issues. El resto del catálogo se sincronizó igual.`,
    ].join('\n');
}
export function errorFrontmatterInvalid(name) {
    return [
        `El comando \`${name}\` del catálogo tiene un frontmatter YAML que no se puede parsear.`,
        `Causa probable: el repo tiene un commit con un comando mal formado, o tu binario no entiende un campo nuevo.`,
        `Probá: \`npm i -g github:dimartinez/from-scratch\` para descartar binario viejo. Si persiste, reportar en github.com/dimartinez/from-scratch/issues.`,
    ].join('\n');
}
export function errorNameConflict(name) {
    return [
        `Ya existe un archivo en ~/.claude/commands/${name} que from-scratch no instaló.`,
        `Causa probable: tenés un comando propio con el mismo nombre, o lo creó otra herramienta.`,
        `Probá: renombrarlo si querés conservarlo, o re-correr con \`--force\` (la CLI hará un backup en <archivo>.bak.<timestamp> antes de pisar).`,
    ].join('\n');
}
export function errorFileDownloadFailed(source, status) {
    return [
        `No pude descargar el archivo \`${source}\` del catálogo (error ${status}).`,
        `Causa probable: el archivo fue eliminado o renombrado en el repo.`,
        `Probá: \`npm i -g github:dimartinez/from-scratch\` para actualizar. Si persiste, reportar en github.com/dimartinez/from-scratch/issues.`,
    ].join('\n');
}
//# sourceMappingURL=errors.js.map