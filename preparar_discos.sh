#!/bin/bash
# Prepara los dos discos virtuales vacios de la VM victima (Debian). Ejecutar UNA vez, como root,
# antes de la clase.
#   EVIDENCIA (~2 GB, FAT32): disco "de un usuario"; se adquirira en la Parte 4.
#   RESPUESTA (~4 GB, ext4):  "USB del respondiente": herramientas y salidas.
# Solo formatea discos completos SIN particiones ni sistema de archivos (nunca el del sistema).
set -euo pipefail
[ "$(id -u)" -eq 0 ] || { echo "Ejecute como root (sudo)."; exit 1; }
command -v mkfs.vfat >/dev/null || { echo "Falta dosfstools: apt install -y dosfstools"; exit 1; }

mapfile -t libres < <(lsblk -dnbo NAME,TYPE,SIZE | awk '$2=="disk"{print $1" "$3}' | while read -r n s; do
    if [ -z "$(lsblk -nro FSTYPE "/dev/$n" | tr -d '\n')" ] && [ "$(lsblk -nro NAME "/dev/$n" | wc -l)" -eq 1 ]; then
        echo "$s $n"
    fi
done | sort -n)

[ "${#libres[@]}" -eq 2 ] || { echo "Se esperaban exactamente 2 discos vacios y hay ${#libres[@]}."; exit 1; }

dev_ev="/dev/$(echo "${libres[0]}" | cut -d' ' -f2)"
dev_re="/dev/$(echo "${libres[1]}" | cut -d' ' -f2)"
echo "EVIDENCIA -> $dev_ev   RESPUESTA -> $dev_re"
read -r -p "Se formatearan ambos. Escriba SI para continuar: " r
[ "$r" = "SI" ] || exit 1

mkfs.vfat -F 32 -n EVIDENCIA "$dev_ev"
mkfs.ext4 -F -L RESPUESTA "$dev_re"
mkdir -p /mnt/evidencia /mnt/respuesta
echo "Listo. Se montan por etiqueta: mount -L EVIDENCIA /mnt/evidencia ; mount -L RESPUESTA /mnt/respuesta"
