class FromScratchError(Exception):
    code: str = "UNKNOWN"
    remediation: str = ""

    def __init__(self, message: str = ""):
        super().__init__(message)
        self.message = message


class NetworkError(FromScratchError):
    code = "NETWORK_ERROR"
    remediation = (
        "Verificá tu conectividad o proxy. "
        "Reintentá con: from-scratch update"
    )

    def __init__(self, message: str = "No se pudo conectar a GitHub"):
        super().__init__(message)


class ManifestParseError(FromScratchError):
    code = "MANIFEST_PARSE_ERROR"
    remediation = (
        "Si el problema persiste, re-cloná con: "
        "rm -rf ~/.from-scratch && curl -fsSL https://raw.githubusercontent.com/dimartinez/from-scratch/main/install.sh | bash"
    )

    def __init__(self, message: str = "El catálogo no se pudo parsear"):
        super().__init__(message)


class CatalogFileNotFoundError(FromScratchError):
    code = "CATALOG_FILE_NOT_FOUND"
    remediation = (
        "Intentá: from-scratch update "
        "Si persiste, re-cloná con: rm -rf ~/.from-scratch && curl -fsSL https://raw.githubusercontent.com/dimartinez/from-scratch/main/install.sh | bash"
    )

    def __init__(self, path: str = ""):
        message = f"Falta el archivo '{path}' referenciado por catalog.json" if path else "Archivo del catálogo no encontrado"
        super().__init__(message)
        self.path = path


class StateCorruptError(FromScratchError):
    code = "STATE_CORRUPT"
    remediation = (
        "Para regenerar el state desde cero: "
        "rm ~/.claude/from-scratch/.state.json && from-scratch init"
    )

    def __init__(self, message: str = "El state file está corrupto"):
        super().__init__(message)


class GitFastForwardError(FromScratchError):
    code = "GIT_FAST_FORWARD_ERROR"
    remediation = (
        "Revisá los cambios locales con: cd ~/.from-scratch && git status\n"
        "Para descartarlos: cd ~/.from-scratch && git reset --hard origin/main"
    )

    def __init__(self, message: str = "El clone local tiene cambios que impiden el fast-forward"):
        super().__init__(message)
