#!/usr/bin/env bash

set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
DESKTOP_DIR="$ROOT_DIR/desktop"

echo "======================================"
echo " Expense Desktop Build"
echo "======================================"

echo ""
echo "[1/8] Nettoyage des anciens builds..."

rm -rf "$BACKEND_DIR/build"
rm -rf "$BACKEND_DIR/dist"
rm -rf "$BACKEND_DIR/.pyarmor_dist"

rm -rf "$FRONTEND_DIR/dist"

rm -rf "$DESKTOP_DIR/.vite"
rm -rf "$DESKTOP_DIR/release"

echo "Nettoyage terminé."


echo ""
echo "[2/8] Build frontend Vue..."

cd "$FRONTEND_DIR"

npm install

npm run build

echo "Frontend généré : $FRONTEND_DIR/dist"


echo ""
echo "[3/8] Copie du frontend vers Electron..."

rm -rf "$DESKTOP_DIR/resources/frontend"

mkdir -p "$DESKTOP_DIR/resources/frontend"

cp -r "$FRONTEND_DIR/dist/"* \
      "$DESKTOP_DIR/resources/frontend/"

echo "Frontend copié."


echo ""
echo "[4/8] Obfuscation backend avec PyArmor..."

cd "$BACKEND_DIR"

if [ ! -d ".venv" ]; then
    echo "Erreur : environnement virtuel backend absent."
    exit 1
fi

source .venv/Scripts/activate

pip install -r requirements.txt

pyarmor gen \
    -O .pyarmor_dist \
    server.py \
    accounts \
    config \
    expenses \
    tenants

echo "Backend obfusqué."


echo ""
echo "[5/8] Compilation backend avec PyInstaller..."

pyinstaller expense-server.spec

echo "Backend généré : $BACKEND_DIR/dist/expense-server.exe"


echo ""
echo "[6/8] Copie du backend vers Electron..."

rm -rf "$DESKTOP_DIR/resources/backend"

mkdir -p "$DESKTOP_DIR/resources/backend"

cp "$BACKEND_DIR/dist/expense-server.exe" \
   "$DESKTOP_DIR/resources/backend/"

echo "Backend copié."


echo ""
echo "[7/8] Package Electron..."

cd "$DESKTOP_DIR"

npm install

npm run package

echo "Package Electron terminé."


echo ""
echo "[8/8] Génération installateur Windows..."

npm run dist

echo ""
echo "======================================"
echo " Build terminé avec succès"
echo "======================================"

echo ""
echo "Résultat :"
echo "$DESKTOP_DIR/release/"