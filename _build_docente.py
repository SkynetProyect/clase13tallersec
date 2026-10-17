from _docgen import *

d = new_doc()
banner(d, "Guía docente de la sesión", "Clase 13 — Forense digital: principios, cadena de custodia, volatilidad y adquisición")

h1(d, "1. Ubicación y propósito de la sesión")
para(d, "Primera sesión de la Unidad 5 (13/10/2026) y primera con el formato nuevo: **sin presentación**. "
        "Usted dicta una guía oral de **45 minutos** y las parejas hacen un laboratorio de **hasta 2 horas** con dos máquinas virtuales. "
        "Lo que no se termine pasa a la sesión siguiente. Los tres temas del cronograma se cubren así:")
table(d, [5.2, 11.39], [
    ["Tema del cronograma", "Dónde se cubre en el laboratorio"],
    ["Principios metodológicos y cadena de custodia", "Partes 0, 1 y 3: formato de custodia con traspaso entre dos custodios, hash en cada paso, decisiones justificadas según ISO/IEC 27037 y NIST SP 800-86."],
    ["Volatilidad de los EMP (elementos materiales probatorios)", "Parte 2: instantánea volátil en el orden de RFC 3227, recuperación de un script borrado desde `/proc` (solo posible con el proceso vivo) y demostración de que la evidencia desaparece del sistema vivo tras la «contención»."],
    ["Adquisición forense de memoria y de discos", "Parte 2 (RAM con AVML), Parte 4 (disco con bloqueo de escritura, dc3dd, verificación) y Parte 5 (validar que lo adquirido sirve: Volatility 3 y Sleuth Kit)."],
])
h2(d, "Resultados de aprendizaje de la sesión")
bullets(d, [
    "Aplicar las cuatro fases de NIST SP 800-86 y los principios de ISO/IEC 27037 (auditabilidad, repetibilidad, reproducibilidad, justificabilidad) a un caso.",
    "Llevar una cadena de custodia con los factores del art. 254 de la Ley 906 de 2004 y demostrar integridad con SHA-256 en cada traspaso.",
    "Ordenar las fuentes de evidencia por volatilidad (RFC 3227) y justificar el orden de captura.",
    "Adquirir memoria RAM y un disco, verificar la copia y comprobar que es analizable.",
])

h1(d, "2. Cronograma de la guía oral (45 minutos)")
table(d, [2.2, 4.0, 10.39], [
    ["Minutos", "Bloque", "Qué hace"],
    ["0–4", "Gancho", "Caso: «el administrador vio el servidor lento, lo reinició y luego llamó a seguridad». Pregunta al grupo: ¿qué se perdió? Anote las respuestas; se retoman en el minuto 28."],
    ["4–16", "Tema 1: principios y custodia", "Ver 3.1. Demo de 90 s: voltear un byte y comparar SHA-256."],
    ["16–28", "Tema 2: volatilidad", "Ver 3.2. Demo de 90 s: `ss -tnp` y `ls -l /proc/PID/fd` con un proceso que tiene un archivo borrado abierto, antes y después de matarlo."],
    ["28–41", "Tema 3: adquisición", "Ver 3.3. Muestre en pantalla los comandos que usarán (`avml`, `blockdev --setro`, `dc3dd`)."],
    ["41–45", "Lanzamiento", "Formar parejas, asignar número (P01…), explicar entregables y reglas. Las máquinas ya deben estar preparadas (sección 4)."],
])
para(d, "**Si va corto:** sacrifique la comparación RAW/E01/AFF4 (3.3). **Si sobra:** pida al grupo que ordene en el tablero las fuentes de evidencia de un servidor antes de revelar el orden de RFC 3227.")

h1(d, "3. Guion por bloque")
h2(d, "3.1 Principios metodológicos y cadena de custodia (12 min)")
bullets(d, [
    "**Dos marcos, un mismo orden de ideas.** NIST SP 800-86: recolección → examen → análisis → informe. ISO/IEC 27037: identificación → recolección → adquisición → preservación. Aclare que 800-86 es de 2006 y sigue siendo la referencia de NIST; la integración con la respuesta a incidentes se actualizó en SP 800-61r3 (abril de 2025), que verán en la clase 16.",
    "**Principios de 27037:** relevancia, confiabilidad y suficiencia de la evidencia; y los cuatro atributos del proceso: auditabilidad, repetibilidad, reproducibilidad, justificabilidad. Pregunta útil: «si otro perito repite mi procedimiento, ¿obtiene el mismo hash?».",
    "**Roles:** DEFR (primer respondiente) y DES (especialista). En el laboratorio la pareja los alterna.",
    "**Cadena de custodia en Colombia:** Ley 906/2004, art. 254 y ss. Factores: identidad, estado original, condiciones de recolección, embalaje y envío, lugares y fechas de permanencia, cambios hechos por cada custodio, y nombre y firma de quien tuvo contacto. El art. 255 fija la responsabilidad en quien entra en contacto con el elemento. Conecte con el Manual de la Fiscalía. Mensajes de datos: Ley 527/1999.",
    "**Demo:** `echo hola > a.txt; shasum -a 256 a.txt; printf 'x' | dd of=a.txt bs=1 seek=1 conv=notrunc; shasum -a 256 a.txt`. Un byte cambia todo el hash: eso es lo que hace verificable la custodia.",
    "**Por qué SHA-256 y no MD5:** SWGDE y las guías vigentes piden algoritmos sin colisiones prácticas; MD5 solo como dato adicional de compatibilidad.",
])
h2(d, "3.2 Volatilidad de los EMP (12 min)")
bullets(d, [
    "**Orden de RFC 3227 (de más a menos volátil):** registros y caché → tabla ARP, de rutas, de procesos, estadísticas del kernel, memoria → sistemas de archivos temporales → disco → registros remotos → topología → medios de respaldo.",
    "**Matiz que debe decir en voz alta:** muchos peritos capturan la RAM primero porque contiene casi todo lo demás; RFC 3227 pone antes ARP, conexiones y procesos porque cambian en segundos. Una instantánea scripteada de 30 s antes de lanzar AVML es el compromiso del laboratorio. Pida que lo justifiquen en P2.",
    "**Huella del respondiente:** toda acción modifica el sistema (ejecutar herramientas, escribir salidas). Por eso se trabaja desde un medio externo (disco RESPUESTA) y se documenta cada comando.",
    "**Demo:** abra una conexión con `nc`, muestre `ss -tnp`, ciérrela y repita. Pregunte qué pasó con la prueba.",
    "**Apagar o no apagar:** apagado ordenado escribe en disco y limpia caché; cortar la energía conserva el disco tal cual pero pierde la RAM y todo lo que siga en la caché de escritura (de ahí el `sync` previo). Se decide caso a caso y se justifica (P4).",
])
h2(d, "3.3 Adquisición forense de memoria y de discos (13 min)")
bullets(d, [
    "**Memoria:** en Linux, AVML (Microsoft, binario estático en espacio de usuario) y LiME (módulo de kernel, exige cabeceras del kernel exacto); en Windows, WinPmem, Magnet RAM Capture o DumpIt. Se usa AVML por no requerir compilar nada. Formatos: LiME (lo lee Volatility), RAW y AFF4.",
    "**Análisis posterior:** Volatility 3 (`banners.Banners`, `linux.pslist`, `linux.psaux`, `linux.sockstat`, `linux.lsof`). Necesita la tabla de símbolos (ISF) del kernel exacto; sin ella no analiza. Es la gran diferencia con Windows y vale una explicación de dos minutos.",
    "**Disco:** nunca trabajar sobre el original. Bloqueador de escritura por hardware o software (`blockdev --setro`, Linux; en VM, medio de solo lectura), copia bit a bit (`dc3dd`, `ewfacquire`, FTK Imager), hash de origen = hash de imagen, y trabajar sobre una copia de la imagen.",
    "**Formatos de imagen:** dd/RAW simple; E01 (Expert Witness) con metadatos del caso y compresión; AFF4. SWGDE 17-F-002-2.1 detalla los controles de verificación.",
    "**Lo que no se ve en un dump de disco apagado:** procesos, conexiones, claves en memoria. De ahí la secuencia memoria → disco.",
    "**Archivos borrados:** en NTFS el borrado quita la entrada de directorio pero la MFT y los clústeres persisten hasta ser sobrescritos. Es lo que recuperarán en la Parte 5 (FAT32: el borrado marca el primer byte del nombre y libera la cadena de clústeres, pero los datos siguen).",
])

h1(d, "4. El laboratorio (2 horas)")
h2(d, "4.1 Preparación previa (obligatoria, fuera de las 2 horas)")
para(d, "La instalación de las dos VM y la tabla de símbolos no caben en las 2 horas. Recomiendo el primer camino:")
bullets(d, [
    "**Recomendado: distribuya usted los OVA** (Debian 13 con los scripts y AVML ya puestos, y Ubuntu 24.04 con las herramientas y la carpeta `~/symbols`) por USB o red del aula. Todas las parejas parten del mismo kernel y se elimina el principal riesgo de la sesión.",
    "**Alternativa:** cada pareja sigue la sección «Preparación» de su guía (instalar Debian 13 y Ubuntu 24.04, descargar AVML). Entonces usted debe entregarles el ISF ya generado (4.2). Calcule 60 min de tarea.",
    "Requisitos por pareja: **un** equipo anfitrión **x86** con 8 GB de RAM (VM Debian 2 GB + VM Ubuntu 2 GB), 40 GB libres y VirtualBox 7.x. AVML solo existe para x86_64: los equipos Apple Silicon no sirven, póngalos con una pareja x86.",
    "Red: adaptador 1 NAT y adaptador 2 solo-anfitrión (`192.168.56.0/24`) en ambas VM. En la Parte 1 se desactiva el NAT de la víctima («aislamiento de la escena»).",
    "Discos extra en la víctima (controlador SATA, dinámicos): EVIDENCIA 2 GB y RESPUESTA 4 GB. `preparar_discos.sh` los formatea (FAT32 y ext4) y no toca discos con particiones.",
])
h2(d, "4.2 Tabla de símbolos de Volatility 3 (se hace una sola vez)")
para(d, "Volatility 3 en Linux necesita un ISF del kernel exacto de la víctima. Como todas las parejas parten de la misma imagen, se genera una vez:")
code(d, """# 1) Kernel de la víctima
uname -r                         # p. ej. 6.12.xx-amd64
# 2) Primero busque un ISF ya compilado en https://github.com/Abyss-W4tcher/volatility3-symbols (Debian/amd64)
# 3) Si no está: descargue linux-image-<uname -r>-dbg de deb.debian.org (verifique el nombre con apt-cache search)
dpkg -x linux-image-*-dbg_*.deb dbg
dwarf2json linux --elf dbg/usr/lib/debug/boot/vmlinux-<uname -r> | xz > ~/symbols/debian-<uname -r>.json.xz
# 4) Validación con un volcado de prueba hecho en la imagen base
vol -s ~/symbols -f prueba.lime banners.Banners
vol -s ~/symbols -f prueba.lime linux.pslist | head""")
para(d, "Si el kernel de la víctima se actualiza (`apt upgrade`) el ISF deja de servir. **Congele** la imagen: no actualice después de generar el ISF.")
h2(d, "4.3 Archivos de apoyo (carpeta `Clase13_Laboratorio/`)")
table(d, [5.2, 11.39], [
    ["Archivo", "Función"],
    ["`preparar_discos.sh`", "Formatea los dos discos extra de la víctima (EVIDENCIA en FAT32, RESPUESTA en ext4)."],
    ["`simular_incidente.sh`", "Inofensivo. Copia `bash` como `/usr/local/lib/systemd-update`, lo deja enviando un beacon TCP al analista, borra su script con el proceso vivo, crea una entrada en `/etc/cron.d` y escribe y borra archivos en EVIDENCIA. Genera una marca única por pareja."],
    ["`triage_volatil.sh`", "Instantánea de datos volátiles con hora UTC y hash por archivo."],
    ["`limpiar_lab.sh`", "Deshace lo que hizo el simulador."],
    ["`plantilla_informe_Clase13.md`", "Plantilla de entrega con formato de custodia, APORTES y declaración de IA."],
])
h2(d, "4.4 Validación de hallazgos")
para(d, "La marca de cada pareja es `FLAG{` + los 12 primeros hex de SHA-256 de `Forense-2026-2:Pnn` + `}`. Se calcula con:")
code(d, "printf '%s' 'Forense-2026-2:P07' | shasum -a 256 | cut -c1-12")
para(d, "Debe aparecer: (i) en la memoria (variable `SECRET` del proceso `systemd-update`), (ii) en `script_recuperado.sh`, copiado de `/proc/PID/fd/255` y (iii) con el sufijo `-ELIMINADO` en el archivo borrado de la imagen FAT. "
        "La marca no es secreta (está en el script), así que lo que cuenta son los hashes, las marcas de tiempo y las capturas propias de cada pareja.")
h2(d, "4.5 Tiempos esperados del laboratorio")
table(d, [1.7, 8.4, 6.49], [
    ["Parte", "Contenido", "Tiempo"],
    ["0", "Verificación del entorno, roles, apertura de la cadena de custodia", "10 min"],
    ["1", "Escena: simulación, documentación y decisión de no apagar", "10–15 min"],
    ["2", "Instantánea volátil, script desde /proc, RAM, hash y «contención»", "25–30 min"],
    ["3", "Traspaso: sync, apagado, desconexión de discos y custodia", "10–15 min"],
    ["4", "Adquisición del disco: bloqueo, dc3dd, verificación y experimento del byte", "20 min"],
    ["5", "Validación: Volatility 3 y Sleuth Kit", "20 min"],
    ["6", "Cierre de la custodia y entrega", "5–10 min"],
])
para(d, "Es un plan ajustado. Un volcado de 2 GB tarda 1–3 min con AVML; copiar y hashear imágenes en VM es lo que más se alarga. Si el grupo va atrasado, la Parte 5 (análisis) pasa a la sesión siguiente, salvo la recuperación del archivo borrado.")
h2(d, "4.6 Riesgos y plan B")
bullets(d, [
    "**Sin probar.** Los scripts de shell pasaron `bash -n` (sintaxis) en mi equipo, pero no se ejecutaron en Debian: no tuve acceso a una VM. **Pruébelos usted de punta a punta** (simulador, triage, AVML, ISF, dc3dd, Sleuth Kit) antes de la sesión.",
    "**AVML:** necesita acceso a `/proc/kcore` o `/dev/crash`; en Debian estándar con VirtualBox sin Secure Boot funciona, pero compruébelo. Si el kernel está en modo «lockdown», fallará. Plan B: LiME, que exige compilar el módulo con las cabeceras del kernel exacto.",
    "**Volatility 3 y el ISF:** si el ISF no coincide con el kernel, no hay análisis de procesos. Plan B: la búsqueda de la marca con `strings` sobre el volcado sigue funcionando y es el mínimo exigido.",
    "**Montajes:** un ext4 «sucio» tras cortar la energía se monta con `-o ro,noload`; sin `noload` el kernel reproduce el diario y escribe. Está en la guía y es un buen punto de discusión.",
    "**Tiempo:** si faltan 20 min, pida a la mitad de la clase solo el apartado 5-A.",
    "**Aviso legal:** repita que se trabaja únicamente en las VM del curso (Ley 1273 de 2009).",
])
h2(d, "4.7 Respuestas esperadas (resumen)")
bullets(d, [
    "**P2:** instantánea → script de `/proc` → RAM → disco; la RAM primero también es aceptable si lo argumentan con SWGDE/SANS. Lo importante: recuperar el script **antes** de cualquier acción que mate el proceso.",
    "**P3:** tras `kill -9`, `ss` ya no muestra la conexión, `/proc/PID` no existe y el script ya no es recuperable, pero `linux.pslist`, `linux.sockstat` y `linux.lsof` del volcado sí lo muestran.",
    "**P4:** `poweroff` de VirtualBox equivale a cortar la energía: no hay escrituras de cierre, pero lo no sincronizado se pierde (de ahí `sync`) y el ext4 queda «sucio». Un apagado ordenado cambia hashes y limpia caché.",
    "**P5:** SHA-256; MD5 con colisiones prácticas; un hash distinto invalida la integridad y rompe la custodia; un byte volteado cambia por completo el hash; montar sin `noload` altera el disco.",
    "**P6:** debilidades típicas: el volcado se escribió en un medio sin hash previo, relojes sin sincronizar, cadena sin testigo, herramienta sin hash de origen, cambios en el sistema por el propio respondiente.",
    "**P7:** ATT&CK: T1036.005 (nombre legítimo), T1059.004 (shell Unix), T1053.003 (cron), T1095 (protocolo de capa no aplicativa) y T1070.004 (borrado de archivos).",
])

h1(d, "5. Referencias")
refs(d)
d.save(BASE + "Guia_Docente_Clase_13 - 2026-2.docx")
print("ok")
