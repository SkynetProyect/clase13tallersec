#!/bin/bash
# Instantanea rapida de datos volatiles, de mayor a menor volatilidad (RFC 3227, sec. 2.1).
# Ejecutar desde la unidad RESPUESTA, como root:  sudo /mnt/respuesta/herramientas/triage_volatil.sh /mnt/respuesta/caso
[ "$(id -u)" -eq 0 ] || { echo "Ejecute como root (sudo)."; exit 1; }
DEST="${1:?Uso: $0 DIRECTORIO_DESTINO}"
mkdir -p "$DEST"

# Cada salida lleva hora UTC de inicio y fin y la orden exacta usada.
guardar() {
    local nombre="$1"; shift
    local ini fin
    ini=$(date -u +%FT%TZ)
    { eval "$*"; } > "$DEST/.tmp_$$" 2>&1
    fin=$(date -u +%FT%TZ)
    { echo "# inicio_utc: $ini"; echo "# fin_utc: $fin"; echo "# orden: $*"; cat "$DEST/.tmp_$$"; } > "$DEST/$nombre"
    rm -f "$DEST/.tmp_$$"
    echo "$ini  $nombre"
}

guardar 01_fecha_hora.txt     'date -u; date; timedatectl status; uptime'
guardar 02_red_vecinos.txt    'ip neigh show; ip route show; ip -br addr'
guardar 03_conexiones.txt     'ss -tunap'
guardar 04_procesos.txt       'ps -eo pid,ppid,user,lstart,comm,args --forest'
guardar 05_procesos_borrados.txt 'ls -l /proc/[0-9]*/exe /proc/[0-9]*/fd/* 2>/dev/null | grep -i "(deleted)"'
guardar 06_sesiones.txt       'who -a; w; last -n 15'
guardar 07_persistencia.txt   'ls -la /etc/cron.d /etc/cron.daily /var/spool/cron/crontabs 2>&1; cat /etc/cron.d/* 2>/dev/null; systemctl list-unit-files --state=enabled --no-pager'
guardar 08_montajes.txt       'mount; lsblk -o NAME,SIZE,FSTYPE,LABEL,MOUNTPOINT'

( cd "$DEST" && sha256sum 0*.txt > HASHES_triage.sha256 )
echo "Listo. Hashes en $DEST/HASHES_triage.sha256. Siguiente paso: adquisicion de memoria."
