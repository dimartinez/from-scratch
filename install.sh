#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${FROM_SCRATCH_REPO_URL:-https://github.com/dimartinez/from-scratch.git}"
INSTALL_DIR="$HOME/.from-scratch"
BIN_DIR="$HOME/.local/bin"
WRAPPER="$BIN_DIR/from-scratch"

# --- Precondition checks ---

if ! command -v git &>/dev/null; then
  echo "ERROR: Necesito git. Instalalo con: xcode-select --install (Mac) o tu package manager." >&2
  exit 3
fi

if ! command -v python3 &>/dev/null; then
  echo "ERROR: Necesito python3. Instalalo con: brew install python@3.12" >&2
  exit 3
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]; }; then
  echo "ERROR: Necesito Python 3.8+. Tenés $PYTHON_VERSION. Instalalo con: brew install python@3.12" >&2
  exit 3
fi

# Check for npm-based previous install
if [ -z "${FROM_SCRATCH_SKIP_NPM_CHECK:-}" ] && command -v npm &>/dev/null; then
  NPM_ROOT=$(npm root -g 2>/dev/null || true)
  if [ -n "$NPM_ROOT" ] && [ -d "$NPM_ROOT/from-scratch" ]; then
    echo "ERROR: Detecté una instalación previa de from-scratch vía npm." >&2
    echo "Antes de continuar, ejecutá:" >&2
    echo "" >&2
    echo "    npm uninstall -g from-scratch" >&2
    echo "" >&2
    echo "Después volvé a correr este install." >&2
    exit 1
  fi
fi

# --- Clone or update ---

if [ -d "$INSTALL_DIR/.git" ]; then
  echo "-> Actualizando from-scratch en $INSTALL_DIR..."
  git -C "$INSTALL_DIR" pull --ff-only
  echo "OK Actualización completa."
else
  echo "-> Clonando from-scratch en $INSTALL_DIR..."
  git clone "$REPO_URL" "$INSTALL_DIR"
  echo "OK Clonación completa."
fi

# --- Install wrapper ---

mkdir -p "$BIN_DIR"

cat > "$WRAPPER" << 'WRAPPER_SCRIPT'
#!/usr/bin/env bash
export PYTHONPATH="$HOME/.from-scratch${PYTHONPATH:+:$PYTHONPATH}"
exec python3 "$HOME/.from-scratch/src/cli.py" "$@"
WRAPPER_SCRIPT

chmod +x "$WRAPPER"

echo "OK Wrapper instalado en $WRAPPER"

# --- PATH hint ---

if ! echo "$PATH" | tr ':' '\n' | grep -qx "$BIN_DIR"; then
  echo ""
  echo "WARN: $BIN_DIR no está en tu PATH. Agregalo con:" >&2
  echo "  echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.zshrc && source ~/.zshrc" >&2
fi

echo ""
echo "Listo. Probá \`from-scratch init\` para instalar el catálogo en ~/.claude/"
