# Problèmes rencontrés et solutions

Tous les problèmes ci-dessous ont été rencontrés pendant le projet et résolus.

## Compilation de Buildroot

### La compilation s'arrête pendant `host-gcc-final`

- **Cause** : mise en veille de la machine pendant la compilation, qui laisse des fichiers incomplets.
- **Solution** : désactiver la veille, puis nettoyer le paquet fautif.
  ```bash
  systemd-inhibit --what=sleep:idle make
  make host-gcc-final-dirclean
  ```
  Sur Kali : `sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target`

### `Error 137` pendant la génération de GCC

- **Cause** : l'erreur 137 signifie que le processus a été tué par manque de mémoire
  (OOM killer). La compilation de GCC est l'étape la plus gourmande de Buildroot.
- **Solution** : réduire le parallélisme (`make` ou `make -j2`) et, surtout, **éviter de
  compiler GCC** en utilisant la toolchain externe Bootlin
  (*Toolchain → Toolchain type → External toolchain*).

### `ld returned 1 exit status` sur `lto1` et `lto-dump`

- **Cause** : fichiers incomplets laissés par les compilations précédentes interrompues,
  et consommation de mémoire de l'édition de liens.
- **Solution** : même démarche, toolchain externe Bootlin.

### Seul `rootfs.tar` dans `output/images/`

- **Cause** : configuration partie de zéro, sans noyau Linux ni image disque.
- **Solution** : charger la configuration de la cible.
  ```bash
  make qemu_aarch64_virt_defconfig
  ```

### `Your display is too small to run Menuconfig`

- **Cause** : le terminal fait moins de 80 colonnes sur 19 lignes.
- **Solution** : agrandir la fenêtre du terminal (vérifier avec `tput lines; tput cols`).

### `ln: failed to create symbolic link ... sysroot/usr/lib`

- **Cause** : résidus de l'ancienne toolchain dans `output/` après le changement de toolchain.
- **Solution** :
  ```bash
  make clean
  make -j2
  ```

## FreeRTOS

### Le dossier `CORTEX_M3_MPS2_QEMU_GCC` n'existe pas

- **Cause** : la version clonée du dépôt FreeRTOS ne le contient pas.
- **Solution** : utiliser `CORTEX_MPU_M3_MPS2_QEMU_GCC` et adapter son `app_main.c`
  (fichier fourni dans `rtos/`).

## Application et réseau

### `OSError: [Errno 98] Address already in use`

- **Cause** : une ancienne instance de `weather.py` tourne encore sur le port 8080.
- **Solution** :
  ```bash
  ps | grep weather
  kill <PID>
  ```

### L'application ne reçoit rien du RTOS

- **Cause** : adresse `10.0.2.15` utilisée à la place de l'hôte (c'est le Linux invité lui-même).
- **Solution** : utiliser `10.0.2.2`.
  ```bash
  python3 /root/weather.py --tcp 10.0.2.2:5555 &
  ```

### La page web reste vide

1. Vérifier que le RTOS émet : `nc localhost 5555` sur l'hôte.
2. Vérifier que le RTOS est lancé **avant** `weather.py` (sinon le script réessaie toutes les 2 s).
3. Tester l'application depuis l'intérieur du Linux émulé : `wget -qO- http://localhost:8080/api/data`.

## Observation sur le temps réel en émulation

Les lignes reçues avec `nc` arrivent parfois avec des délais irréguliers. Le temps du RTOS
émulé dépend de l'horloge et de la charge de la machine hôte, qui exécute deux émulations
en parallèle. Un émulateur ne garantit donc pas le comportement temps réel : la période
d'une seconde est respectée par construction dans le code, mais sa précision réelle ne peut
être mesurée de façon fiable que sur du matériel.

Pour réduire le phénomène : fermer les applications gourmandes, donner plus de cœurs à
la machine si elle est virtualisée, et vérifier la charge avec `top`.
