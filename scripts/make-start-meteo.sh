#!/usr/bin/env bash
# Crée output/images/start-meteo.sh à partir du start-qemu.sh généré par Buildroot,
# en ajoutant la redirection du port 8080 (hôte) vers le port 8080 (Linux émulé).
#
# On travaille sur une COPIE, car Buildroot régénère start-qemu.sh à chaque "make".
#
# Usage : ./scripts/make-start-meteo.sh ~/projet/buildroot-2026.08/output/images
set -euo pipefail

IMAGES="${1:?Usage : $0 <dossier output/images de Buildroot>}"
SRC="$IMAGES/start-qemu.sh"
DST="$IMAGES/start-meteo.sh"

[ -f "$SRC" ] || { echo "Introuvable : $SRC" >&2; exit 1; }

sed 's/-netdev user,id=eth0/-netdev user,id=eth0,hostfwd=tcp::8080-:8080/' "$SRC" > "$DST"
chmod +x "$DST"

if grep -q 'hostfwd=tcp::8080-:8080' "$DST"; then
    echo "OK : $DST créé (redirection 8080 ajoutée)."
else
    echo "Attention : l'option '-netdev user,id=eth0' n'a pas été trouvée dans $SRC." >&2
    echo "Modifiez $DST à la main (voir README, section 'Redirection de port')." >&2
    exit 1
fi
