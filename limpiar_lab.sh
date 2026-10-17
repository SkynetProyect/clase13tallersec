#!/bin/bash
# Deshace lo que hizo simular_incidente.sh en la VM victima (proceso, binario, cron).
[ "$(id -u)" -eq 0 ] || { echo "Ejecute como root (sudo)."; exit 1; }
pkill -9 -x systemd-update 2>/dev/null || true
rm -f /usr/local/lib/systemd-update /usr/local/lib/.update.sh /etc/cron.d/systemd-update
echo "Laboratorio limpio."
