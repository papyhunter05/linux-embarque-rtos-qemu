# Partie RTOS : FreeRTOS sur Cortex-M3 (QEMU)

Ce dossier contient `app_main.c`, qui **remplace** le fichier du même nom dans la démo
FreeRTOS `CORTEX_MPU_M3_MPS2_QEMU_GCC` (carte émulée `mps2-an385`).

## Ce que fait la tâche

- Période exacte de **1000 ms** avec `vTaskDelayUntil` (compense le temps d'exécution).
- Création **statique** (`xTaskCreateStatic`) : la configuration de la démo utilise
  `configUSE_STATIC_ALLOCATION`.
- Tâche **privilégiée** (`portPRIVILEGE_BIT`) : elle accède directement aux registres de
  l'UART malgré la protection mémoire (MPU) de la démo.
- Mesures **simulées** par des signaux en triangle :

| Mesure | Plage | Période du signal |
|---|---|---|
| Température | 20,0 à 28,0 °C | 60 s |
| Humidité | 50,0 à 65,0 % | 90 s |
| Pression | 1012,0 à 1016,0 hPa | 200 s |

- Envoi d'une ligne `T,H,P` par seconde sur l'**UART0** (CMSDK UART, base `0x40004000`),
  par exemple : `22.5,55.0,1013.2`.

L'écriture se fait directement sur l'UART (sans `printf`) pour que les mesures sortent
à coup sûr sur la liaison série.

## Compiler

```bash
sudo apt install -y gcc-arm-none-eabi make qemu-system-arm

cd ~
git clone --depth 1 --recurse-submodules --shallow-submodules https://github.com/FreeRTOS/FreeRTOS.git

cd ~/FreeRTOS/FreeRTOS/Demo/CORTEX_MPU_M3_MPS2_QEMU_GCC
cp app_main.c app_main.c.orig                    # sauvegarde de l'original
cp /chemin/vers/ce/depot/rtos/app_main.c .
make
```

Le résultat est `build/RTOSDemo.axf`.

> Le dossier `CORTEX_M3_MPS2_QEMU_GCC` (sans « MPU ») n'existe pas dans toutes les versions
> du dépôt FreeRTOS. Ce projet utilise la démo MPU, présente dans la version utilisée.

## Lancer

```bash
./scripts/run-rtos.sh
```

QEMU attend qu'un client se connecte sur le port 5555 avant de démarrer le RTOS.
Pour vérifier la sortie, dans un autre terminal :

```bash
nc localhost 5555
```

Une ligne par seconde doit apparaître.
