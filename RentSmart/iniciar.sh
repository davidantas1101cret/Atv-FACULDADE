#!/usr/bin/env bash
# Inicia o RentSmart (Flask) sem precisar do VS Code.
cd "$(dirname "$0")" || exit 1
[ -d venv ] || python3 -m venv venv || { echo "Python 3 não encontrado."; exit 1; }
./venv/bin/pip install -q -r requirements.txt || exit 1
echo "RentSmart em http://127.0.0.1:5000 (Ctrl+C para encerrar)"
exec ./venv/bin/python main.py
