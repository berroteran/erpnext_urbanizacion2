#!/usr/bin/env bash
# sync-wsl.sh — sincroniza el repo de Windows al bench WSL (sin migrate)
# Uso desde WSL: bash /mnt/c/Users/Mistake/Desktop/Erp\ Next/erpnext-bel-urbanizacion/scripts/sync-wsl.sh

set -e

WIN_REPO="/mnt/c/Users/Mistake/Desktop/Erp Next/erpnext-bel-urbanizacion"
BENCH_APP="/home/frappe/frappe-bench/apps/urbanizacion"

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

echo "[sync-wsl] ✓ Sincronizado $(date '+%H:%M:%S')"
