# Configuration Buildroot

Placez ici la configuration compacte de votre système (`defconfig`) pour pouvoir
reconstruire exactement la même image.

## Générer le fichier

Depuis le dossier de Buildroot :

```bash
cd ~/projet/buildroot-2026.08
make savedefconfig BR2_DEFCONFIG=/chemin/vers/ce/depot/configs/meteo_defconfig
```

## Reconstruire le système depuis cette configuration

```bash
cd ~/projet/buildroot-2026.08
make defconfig BR2_DEFCONFIG=/chemin/vers/ce/depot/configs/meteo_defconfig
make -j2
```

## Éléments de configuration utilisés dans ce projet

| Réglage | Valeur |
|---|---|
| Point de départ | `qemu_aarch64_virt_defconfig` |
| Toolchain | External toolchain, Bootlin (aarch64, glibc) |
| Paquet ajouté | `python3` (*Target packages → Interpreter languages and scripting*) |
| Overlay | Dossier contenant `root/weather.py` (*System configuration → Root filesystem overlay directories*) |
