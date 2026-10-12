#!/usr/bin/env bash
# Script para compilar o executável portátil único via PyInstaller
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "=========================================================="
echo "Compilando NotaCorreta em executável portátil..."
echo "=========================================================="

PYTHONPATH=.:./libs python3 -m PyInstaller \
    --clean \
    --onefile \
    --name nota-correta \
    --paths ./libs \
    src/main.py

echo "=========================================================="
echo "Compilação concluída com sucesso!"
echo "Executável gerado em: dist/nota-correta"
echo "=========================================================="

