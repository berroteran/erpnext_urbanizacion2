#!/usr/bin/env bash
# migrate-local.sh — sync + migrate + clear-cache en urbanizacion.local
# Uso desde WSL: bash /mnt/c/Users/Mistake/Desktop/Erp\ Next/erpnext-bel-urbanizacion/scripts/migrate-local.sh

set -e

BENCH="/home/frappe/frappe-bench"
SITE="urbanizacion.local"
WIN_REPO="/mnt/c/Users/Mistake/Desktop/Erp Next/erpnext-bel-urbanizacion"
BENCH_APP="$BENCH/apps/urbanizacion"

echo "[migrate-local] Sincronizando archivos..."
rsync -a --delete \
  --exclude='.git' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='*.pyo' \
  --exclude='.claude' \
  --exclude='docs' \
  --exclude='*.xlsx' \
  --exclude='*.txt' \
  "$WIN_REPO/" "$BENCH_APP/"

echo "[migrate-local] Corriendo bench migrate..."
cd "$BENCH"
bench --site "$SITE" migrate

echo "[migrate-local] Limpiando caché..."
bench --site "$SITE" clear-cache

echo "[migrate-local] ✓ Listo $(date '+%H:%M:%S')"
