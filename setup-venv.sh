#!/usr/bin/env bash
set -euo pipefail

# Check for python3
if ! command -v python3 &>/dev/null; then
  echo "python3 not found. Please install Python 3.10+"
  exit 1
fi

# Create virtual environment if it doesn't exist
VENV_DIR="./venv"
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment in $VENV_DIR..."
  python3 -m venv "$VENV_DIR"
else
  echo "Virtual environment already exists at $VENV_DIR"
fi

# Upgrade pip and install requirements
echo "Upgrading pip..."
"$VENV_DIR/bin/pip" install --upgrade pip

if [ -f "requirements.txt" ]; then
  echo "Installing requirements..."
  "$VENV_DIR/bin/pip" install -r requirements.txt
else
  echo "No requirements.txt found — skipping pip install"
fi

echo "Virtual environment is ready."
echo "Activate it with:"
echo "  source $VENV_DIR/bin/activate"