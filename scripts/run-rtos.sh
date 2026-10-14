#!/usr/bin/env bash
# Lance le RTOS FreeRTOS dans QEMU (Cortex-M3, carte mps2-an385).
# La sortie série (UART0) est redirigée vers le port TCP 5555.
# QEMU attend qu'un client se connecte avant de démarrer le RTOS.
#
# Usage : ./scripts/run-rtos.sh [chemin/vers/RTOSDemo.axf]
set -euo pipefail

AXF="${1:-$HOME/FreeRTOS/FreeRTOS/Demo/CORTEX_MPU_M3_MPS2_QEMU_GCC/build/RTOSDemo.axf}"

if [ ! -f "$AXF" ]; then
    echo "Fichier introuvable : $AXF" >&2
    echo "Compilez d'abord la démo (voir rtos/README.md)." >&2
    exit 1
fi

exec qemu-system-arm \
    -machine mps2-an385 \
    -monitor none -display none \
    -semihosting --semihosting-config enable=on,target=native \
    -kernel "$AXF" \
    -serial tcp::5555,server
