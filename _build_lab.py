from _docgen import *

d = new_doc()
banner(d, "Guía de laboratorio", "Clase 13 — Custodia, volatilidad y adquisición forense de memoria y disco (Linux)")

h1(d, "1. Qué se evalúa")
para(d, "Usted y su pareja atienden un incidente simulado en un servidor Linux, recolectan la evidencia en el orden correcto, la adquieren, la entregan con cadena de custodia y comprueban que sirve para el análisis. Es el proceso real de un primer respondiente, reducido a 2 horas.")
h2(d, "Resultados de aprendizaje")
bullets(d, [
    "Documentar una cadena de custodia con hash en cada traspaso (Ley 906/2004, art. 254; ISO/IEC 27037).",
    "Capturar la evidencia en el orden de volatilidad de RFC 3227 y justificar las decisiones.",
    "Adquirir memoria RAM y un disco, verificar la integridad y demostrar que la evidencia es analizable.",
])
para(d, "**Aviso legal:** todo se hace solo en las dos VM del curso. Usar estas técnicas o los scripts sobre equipos ajenos sin autorización es delito (Ley 1273 de 2009). El «incidente» es inofensivo: no cifra ni envía datos fuera de su red de laboratorio.")

h1(d, "2. Condiciones de trabajo")
table(d, [4.2, 12.39], [
    ["Elemento", "Detalle"],
    ["Parejas", "Dos integrantes, un solo equipo anfitrión x86 (≥8 GB de RAM, 40 GB libres) con VirtualBox 7.x. Alternan los roles A (primer respondiente, DEFR) y B (analista y custodio, DES) como se indica en cada parte."],
    ["VM víctima (`VICTIMA`)", "**Debian 13 «trixie»**, 2 GB de RAM, usuario con `sudo`, adaptador 1 NAT y adaptador 2 solo-anfitrión. Discos extra: EVIDENCIA (2 GB) y RESPUESTA (4 GB)."],
    ["VM analista (`ANALISTA`)", "Ubuntu 24.04, 2 GB de RAM (4 GB recomendado), adaptador 1 NAT y adaptador 2 solo-anfitrión, 30 GB de disco para guardar las imágenes."],
    ["Herramientas", "AVML (Microsoft), `sha256sum`, `ss`, `dc3dd`, `ewf-tools`, `sleuthkit`, Volatility 3 (`pipx install volatility3`), `strings`, `nc`."],
    ["Tiempo", "Máximo 2 horas. Lo que no termine se continúa en la sesión siguiente. La preparación de las VM no cuenta."],
    ["IA", "Permitida si la declara en `DECLARACION_IA`. Los comandos y hashes deben salir de su propia ejecución."],
])
para(d, "AVML solo existe para x86_64. Los equipos Apple Silicon (ARM) no sirven para este laboratorio: busque una pareja con un equipo x86.")

h1(d, "3. Preparación (antes de la clase)")
para(d, "Si el docente le entregó las VM ya instaladas (OVA), solo verifique la lista de chequeo del final de esta sección.")
bullets(d, [
    "Instale VirtualBox 7.x. Descargue la imagen de instalación de Debian 13 (netinst) y la de Ubuntu 24.04 LTS.",
    "Cree `VICTIMA` y `ANALISTA` con los recursos de la sección 2. En `VICTIMA` añada dos discos dinámicos SATA de 2 GB y 4 GB. Instale Debian con «utilidades estándar del sistema» y «servidor SSH».",
    "En `VICTIMA`, con Internet (NAT): `sudo apt update && sudo apt install -y dosfstools`. Del campus descargue `Clase13_Laboratorio.zip` y de https://github.com/microsoft/avml/releases el binario `avml`. Anote su SHA-256.",
    "Ejecute `sudo ./preparar_discos.sh` (formatea EVIDENCIA y RESPUESTA; confirme que reconoce los discos correctos). Luego: `sudo mount -L RESPUESTA /mnt/respuesta && sudo mkdir -p /mnt/respuesta/herramientas && sudo cp avml triage_volatil.sh /mnt/respuesta/herramientas/ && sudo chmod +x /mnt/respuesta/herramientas/*`. Los scripts `simular_incidente.sh` y `limpiar_lab.sh` quedan en su carpeta personal.",
    "En `ANALISTA`:",
])
code(d, """sudo apt update && sudo apt install -y sleuthkit ewf-tools dc3dd binutils netcat-openbsd pipx
pipx install volatility3 && pipx ensurepath
vol -h | head -3        # si el comando es vol3, use ese nombre en toda la guía
ip -br a                # anote la IP de la red solo-anfitrión (192.168.56.x)
ls ~/symbols            # tabla de símbolos (ISF) del kernel de la víctima, entregada por el docente""")
para(d, "**Lista de chequeo:** ambas VM se ven por `ping` en la red solo-anfitrión · RESPUESTA tiene `herramientas/` con `avml` · `~/symbols` contiene un `.json.xz` de Debian · hay 6 GB libres en `ANALISTA`.")

h1(d, "4. Estructura y tiempos")
table(d, [1.6, 10.2, 2.4, 2.39], [
    ["Parte", "Contenido", "Tiempo", "Roles"],
    ["0", "Entorno, hora, apertura de la cadena de custodia", "10 min", "A y B"],
    ["1", "Escena: simulación, documentación y decisión de no apagar", "10–15 min", "A actúa, B documenta"],
    ["2", "Instantánea volátil, artefacto en `/proc`, RAM, hash y «contención»", "25–30 min", "A actúa, B documenta"],
    ["3", "Apagado, desconexión de discos y traspaso de custodia", "10–15 min", "A entrega, B recibe"],
    ["4", "Adquisición del disco y verificación", "20 min", "B actúa, A documenta"],
    ["5", "Validación: Volatility 3 y Sleuth Kit", "20 min", "A y B"],
    ["6", "Cierre de la custodia y entrega", "5–10 min", "A y B"],
])

h1(d, "5. Desarrollo")
h2(d, "Parte 0 — Entorno y apertura de la custodia (10 min)")
bullets(d, [
    "En `ANALISTA` cree la carpeta del caso: `mkdir -p ~/caso_Pnn/{evidencia,logs,salidas}` (reemplace `nn` por el número de su pareja).",
    "Compare la hora de ambas VM en UTC (`date -u` en las dos) y anote la diferencia (`timedatectl` muestra si hay sincronización). Una custodia con relojes sin sincronizar se ataca fácilmente.",
    "En `VICTIMA`: `sudo mount -L RESPUESTA /mnt/respuesta`. Registre las herramientas con su versión y SHA-256: `sha256sum /mnt/respuesta/herramientas/*`.",
    "Abra el formato de custodia de la plantilla `plantilla_informe_Clase13.md`. Tome una captura de cada VM con la hora visible; nómbrelas `P0_*.png`.",
])
h2(d, "Parte 1 — La escena (10–15 min) · A actúa, B documenta")
bullets(d, [
    "En `ANALISTA` deje a la escucha el «servidor del atacante»: `nc -lk 4444 | tee ~/caso_Pnn/logs/beacon.log`. Hará de servidor solo dentro de la red de laboratorio.",
    "En `VICTIMA`: `sudo ./simular_incidente.sh Pnn <IP_analista>`. A partir de aquí **no reinicie ni apague la VM**.",
    "B anota la hora UTC de inicio y describe la escena: usuario conectado, hora, síntoma. Registre qué sabría un administrador real en este momento y qué no.",
    "**Aislamiento sin apagar:** desconecte el adaptador NAT de `VICTIMA` (VirtualBox > Dispositivos > Red) pero deje el adaptador solo-anfitrión. Justifique en una línea por qué no se desconecta todo.",
    "Primera entrada de la cadena: identificador del caso, fecha y hora UTC, nombres de A y B y estado de la VM.",
])
h2(d, "Parte 2 — Volatilidad: instantánea, RAM y contención (25–30 min) · A actúa, B documenta")
para(d, "**2.1 Instantánea volátil** (RFC 3227: de lo más volátil a lo menos). Se ejecuta desde RESPUESTA para no escribir en el disco del sistema:")
code(d, "sudo /mnt/respuesta/herramientas/triage_volatil.sh /mnt/respuesta/caso")
para(d, "Revise `03_conexiones.txt`, `04_procesos.txt` y `05_procesos_borrados.txt`. Busque el proceso que no debería estar ahí (nombre, ruta del binario, padre, línea de comandos) y la conexión hacia `ANALISTA`. Anote el PID, la ruta y el puerto. Registre el triage como **E01**.")
para(d, "**2.2 Un artefacto que solo existe mientras el proceso vive.** El atacante borró su script, pero el proceso lo sigue teniendo abierto:")
code(d, """PID=<pid_del_proceso_sospechoso>
sudo ls -l /proc/$PID/exe /proc/$PID/fd
sudo tr '\\0' ' ' < /proc/$PID/cmdline; echo
sudo cp /proc/$PID/fd/255 /mnt/respuesta/caso/script_recuperado.sh
sha256sum /mnt/respuesta/caso/script_recuperado.sh | sudo tee /mnt/respuesta/caso/hash_script.txt""")
para(d, "Registre el script recuperado como **E02**. Lea su contenido y explique qué hace.")
para(d, "**2.3 Adquisición de la memoria RAM.** Confirme las opciones con `--help`:")
code(d, """sudo /mnt/respuesta/herramientas/avml /mnt/respuesta/caso/memoria_Pnn.lime
sha256sum /mnt/respuesta/caso/memoria_Pnn.lime | sudo tee /mnt/respuesta/caso/hash_memoria.txt
ls -l /mnt/respuesta/caso""")
para(d, "Registre hora de inicio y fin, tamaño (parecido a la RAM de la VM, 2 GB) y hash en la cadena como **E03**.")
para(d, "**2.4 La «contención» que destruye evidencia** (fallo deliberado). El administrador mata el proceso sospechoso:")
code(d, """sudo kill -9 $PID
ss -tnp | grep 4444
ps -p $PID
ls /proc/$PID""")
para(d, "Documente qué sigue y qué ya no existe en el sistema vivo. En la Parte 5 comprobará si sobrevivió en el volcado. **Pregunta P3.**")
h2(d, "Parte 3 — Traspaso y custodia (10–15 min) · A entrega, B recibe")
bullets(d, [
    "Antes de apagar, A anota en la cadena los hashes del triage (`HASHES_triage.sha256`), del script y de la memoria. B los repite en voz alta para verificar.",
    "Ejecute `sync` y anote la hora: sin él, lo último escrito en RESPUESTA puede seguir en la memoria caché y perderse al cortar la energía (**P4**).",
    "Apague **cortando la energía**: `VBoxManage controlvm VICTIMA poweroff`. Es lo equivalente a desenchufar; no hay escrituras de cierre del sistema. Justifique la elección en **P4**.",
    "Con la VM apagada, quite los discos RESPUESTA y EVIDENCIA de `VICTIMA` y conéctelos a `ANALISTA` como **solo lectura**. Por la interfaz: Configuración > Almacenamiento. Por línea de comandos (ajuste nombres de archivo, controlador y puertos con `VBoxManage showvminfo VICTIMA`):",
])
code(d, """VBoxManage storageattach VICTIMA --storagectl SATA --port 1 --device 0 --medium none
VBoxManage storageattach VICTIMA --storagectl SATA --port 2 --device 0 --medium none
VBoxManage modifymedium disk EVIDENCIA.vdi --type readonly
VBoxManage modifymedium disk RESPUESTA.vdi --type readonly
VBoxManage storageattach ANALISTA --storagectl SATA --port 2 --device 0 --type hdd --medium EVIDENCIA.vdi
VBoxManage storageattach ANALISTA --storagectl SATA --port 3 --device 0 --type hdd --medium RESPUESTA.vdi""")
bullets(d, [
    "Complete la fila de traspaso (quién entrega, quién recibe, UTC, motivo). Cada traspaso lleva el hash del elemento.",
])
h2(d, "Parte 4 — Adquisición del disco (20 min) · B actúa, A documenta")
para(d, "En `ANALISTA`, identifique los discos y trabaje siempre con el original en solo lectura:")
code(d, """lsblk -o NAME,SIZE,RO,FSTYPE,LABEL
# Suponga que EVIDENCIA es /dev/sdc y RESPUESTA es /dev/sdd; verifíquelo por tamaño y etiqueta.
sudo blockdev --setro /dev/sdc /dev/sdd
sudo blockdev --getro /dev/sdc        # debe imprimir 1

# Copie lo recolectado y verifique contra los hashes de la Parte 3.
# noload evita que ext4 reproduzca su diario: un montaje «de solo lectura» también escribe sin él.
sudo mkdir -p /mnt/respuesta && sudo mount -o ro,noload /dev/sdd /mnt/respuesta
cp /mnt/respuesta/caso/* ~/caso_Pnn/evidencia/
cd ~/caso_Pnn/evidencia && sha256sum memoria_Pnn.lime script_recuperado.sh   # compare con hash_*.txt

# Imagen del disco EVIDENCIA, con hash de origen calculado durante la copia
sudo dc3dd if=/dev/sdc of=$HOME/caso_Pnn/evidencia/evidencia_Pnn.dd hash=sha256 log=$HOME/caso_Pnn/logs/dc3dd.log
sha256sum ~/caso_Pnn/evidencia/evidencia_Pnn.dd
sudo sha256sum /dev/sdc""")
para(d, "Los tres hashes (log de `dc3dd`, imagen y dispositivo original) deben ser **idénticos**. Regístrelos como **E04**. Si `dc3dd` no está disponible use `dcfldd` o `dd` más `sha256sum`.")
para(d, "**Extensión (si va adelantado):** genere también una imagen E01 con metadatos del caso (`sudo ewfacquire /dev/sdc`) y verifíquela con `ewfverify`. Compare tamaños.")
para(d, "**4.2 Experimento del byte (fallo deliberado).** Trabaje con una **copia**, nunca con la imagen principal:")
code(d, """cp ~/caso_Pnn/evidencia/evidencia_Pnn.dd ~/caso_Pnn/salidas/copia_trabajo.dd
printf '\\x01' | dd of=$HOME/caso_Pnn/salidas/copia_trabajo.dd bs=1 seek=1000000 conv=notrunc
sha256sum ~/caso_Pnn/evidencia/evidencia_Pnn.dd ~/caso_Pnn/salidas/copia_trabajo.dd""")
para(d, "**4.3 Prueba del bloqueo de escritura (solo después de verificar la imagen).** Esto debe fallar; copie el mensaje de error:")
code(d, "sudo dd if=/dev/zero of=/dev/sdc bs=512 count=1")
h2(d, "Parte 5 — Validación: ¿sirve lo que adquirimos? (20 min)")
para(d, "**5-A. Memoria con Volatility 3.** Volatility necesita la tabla de símbolos del kernel exacto de la víctima (`~/symbols`):")
code(d, """cd ~/caso_Pnn/evidencia
vol -s ~/symbols -f memoria_Pnn.lime banners.Banners          # el kernel debe coincidir con `uname -r` de la víctima
vol -s ~/symbols -f memoria_Pnn.lime linux.pslist | tee ../salidas/pslist.txt
vol -s ~/symbols -f memoria_Pnn.lime linux.psaux | grep -i update
vol -s ~/symbols -f memoria_Pnn.lime linux.sockstat | grep 4444
vol -s ~/symbols -f memoria_Pnn.lime linux.lsof --pid <PID> | tee ../salidas/lsof.txt
strings -a memoria_Pnn.lime | grep -m3 'FLAG{'""")
bullets(d, [
    "Responda: ¿el proceso que mató en 2.4 aparece en el volcado? ¿Quién es su padre? ¿Qué conexión tenía? ¿Qué archivo borrado mantenía abierto?",
    "Si un plugin falla o no muestra datos con esta versión de Volatility 3 o de kernel, documente el comando, el mensaje y lo que probó. Es un hallazgo válido, no un error del laboratorio. Mínimo exigido: `banners.Banners`, `linux.pslist` y la búsqueda de la marca con `strings`.",
    "La marca `FLAG{...}` de su pareja debe aparecer en la memoria y en `script_recuperado.sh`. Anótela como evidencia.",
])
para(d, "**5-B. Disco con The Sleuth Kit.** La imagen es un sistema FAT32 sin tabla de particiones, así que no hace falta `-o`:")
code(d, """cd ~/caso_Pnn/evidencia
fsstat evidencia_Pnn.dd | head -20
fls -r evidencia_Pnn.dd                    # archivos presentes
fls -r -d evidencia_Pnn.dd                 # archivos borrados (asterisco)
icat evidencia_Pnn.dd <inodo> > ../salidas/recuperado.txt
head -c 300 ../salidas/recuperado.txt; sha256sum ../salidas/recuperado.txt
strings -a -t d evidencia_Pnn.dd | grep ELIMINADO     # la misma marca, por su posición en el disco""")
para(d, "Registre el archivo recuperado como **E05** (derivado de E04) en la custodia, con su hash. Explique por qué el nombre del archivo borrado aparece alterado.")
h2(d, "Parte 6 — Cierre (5–10 min)")
bullets(d, [
    "Complete todas las filas de la cadena: ninguna celda vacía; cada traspaso con hora UTC y hash.",
    "Guarde en el entregable: informe, cadena de custodia, `hash_*.txt`, `dc3dd.log`, `beacon.log`, salidas de Volatility y Sleuth Kit, el script recuperado y las capturas. **No suba los `.lime` ni los `.dd`**; solo sus hashes.",
    "Si va a reutilizar la VM víctima: `sudo ./limpiar_lab.sh`.",
])

h1(d, "6. Entregables")
bullets(d, [
    "`entregable_Pnn.zip` con `informe_Pnn.md` (plantilla), los archivos de la Parte 6 y las capturas `P0_` a `P5_`.",
    "Cadena de custodia con los elementos E01 a E05 (y E06 si hace la extensión E01).",
    "Fecha límite: la que indique el campus; sin la cadena de custodia, la entrega no se califica.",
])

h1(d, "7. Rúbrica (escala 0.0–5.0)")
table(d, [3.2, 3.3, 3.3, 3.3, 3.49], [
    ["Criterio", "Excelente", "Adecuado", "Insuficiente", "No cumple"],
    ["1. Ejecución técnica y verificación de integridad (1.5)\nGrupal",
     "1.5 · RAM y disco adquiridos; los tres hashes del disco coinciden; Volatility 3 y Sleuth Kit prueban que sirven.",
     "1.1 · Adquisiciones completas con un hash sin verificar o una validación incompleta.",
     "0.6 · Solo una evidencia adquirida o sin verificación de hash.",
     "0.0 · Sin evidencia adquirida."],
    ["2. Interpretación y justificación (1.5)\nIndividual",
     "1.5 · Explica por qué en P1–P7 con evidencia propia y cita las referencias.",
     "1.1 · Respuestas correctas con justificación parcial.",
     "0.6 · Respuestas descriptivas sin justificar.",
     "0.0 · Sin respuestas o copiadas."],
    ["3. Cadena de custodia y documentación (1.0)\nIndividual",
     "1.0 · Cada traspaso con quién, cuándo (UTC), por qué y hash; cubre los factores del art. 254.",
     "0.7 · Completa con uno o dos vacíos.",
     "0.4 · Faltan traspasos o hashes.",
     "0.0 · No hay cadena."],
    ["4. Rigor y trabajo en equipo (1.0)\nGrupal",
     "1.0 · Roles alternados, capturas con hora, comandos reproducibles.",
     "0.7 · Roles y capturas con vacíos menores.",
     "0.4 · Poca trazabilidad o un solo integrante trabajó.",
     "0.0 · Sin trazabilidad."],
])
para(d, "Nota final = 0.4 × (criterios 1 y 4 escalados a 5.0) + 0.6 × (promedio de las respuestas que cada integrante declaró en `APORTES`).")
table(d, [10.5, 6.09], [
    ["Ajuste", "Efecto"],
    ["Entrega tardía", "−0.5 por día; 0.0 tras 3 días"],
    ["Salidas borradas o editadas", "Se penaliza en el criterio 4"],
    ["IA no declarada o copia", "Se penaliza en los criterios 2 y 4"],
    ["Hallazgo propio no pedido (p. ej. un artefacto adicional documentado con evidencia)", "Bonificación de hasta +0.3"],
])

h1(d, "8. Preguntas del informe")
for q in [
    "**P1.** ¿Cuáles de los principios de ISO/IEC 27037 (auditabilidad, repetibilidad, reproducibilidad, justificabilidad) cumplió su procedimiento y cuáles no? Una evidencia propia por principio.",
    "**P2.** Ordene por volatilidad las fuentes que recolectó o pudo recolectar (vecinos ARP, conexiones, procesos, RAM, disco, registros remotos, respaldos). ¿Hizo la instantánea antes o después de la RAM, y recuperó el script antes o después? Justifique con RFC 3227 y SWGDE.",
    "**P3.** Después de la «contención» de 2.4, ¿qué evidencia desapareció del sistema vivo y cuál sobrevivió en el volcado? Muestre salidas de ambos momentos.",
    "**P4.** ¿Por qué cortar la energía y no apagar con `shutdown`? ¿Qué papel tuvo `sync`? ¿Qué se pierde y qué se gana?",
    "**P5.** ¿Por qué SHA-256 y no MD5? ¿Qué demuestra que dos hashes coincidan y qué un hash distinto? Relacione con el experimento del byte y con el montaje `ro,noload`.",
    "**P6.** Señale al menos dos debilidades de su propia cadena de custodia que un abogado de la contraparte atacaría (usando los factores del art. 254 de la Ley 906) y cómo las corregiría.",
    "**P7.** Reconstruya la línea de tiempo del incidente (proceso, conexión, persistencia, archivo borrado) y asigne técnicas de MITRE ATT&CK a cada paso.",
]:
    p = d.add_paragraph(style="List Bullet"); rich(p, q)

h1(d, "9. Problemas frecuentes")
table(d, [5.5, 11.09], [
    ["Síntoma", "Qué revisar"],
    ["`avml` falla o no escribe", "Falta `sudo`, el binario no tiene permiso de ejecución o no hay espacio en RESPUESTA; use `--help`."],
    ["El volcado es mucho menor que la RAM", "Revise `ls -l` y `free -m`; compare con el tamaño esperado (~2 GB)."],
    ["Volatility dice que no hay símbolos", "El ISF no corresponde al kernel exacto (`banners.Banners` vs `uname -r`) o falta `-s ~/symbols`."],
    ["`sdc` o `sdd` no son los discos", "Identifíquelos por tamaño (2 GB y 4 GB) y etiqueta con `lsblk -o NAME,SIZE,LABEL`."],
    ["`mount` falla en ext4", "Use `-o ro,noload`; tras cortar la energía el sistema de archivos queda «sucio», es lo esperado."],
    ["`beacon.log` vacío", "La víctima no llega a `ANALISTA`; revise la IP, el puerto 4444 y que el adaptador solo-anfitrión esté activo."],
    ["No encuentro el proceso sospechoso", "Busque en `04_procesos.txt` un nombre de servicio del sistema cuyo binario esté en `/usr/local/lib`."],
])

h1(d, "10. Referencias")
refs(d)
d.save(BASE + "Guia_Laboratorio_Clase13_Forense_Adquisicion - 2026-2.docx")
print("ok")
