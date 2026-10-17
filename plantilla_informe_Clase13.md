# Informe — Laboratorio Clase 13 (Forense: custodia, volatilidad y adquisición)

PAREJA: P__
INTEGRANTES:
- Nombre 1 — correo — rol inicial (A: primer respondiente / B: analista)
- Nombre 2 — correo — rol inicial

DECLARACION_IA: (ninguna | herramienta y para qué la usó)

APORTES: (qué preguntas/partes respondió y firma cada integrante; ej. «P1, P4, Parte 4: Nombre 1»)

## Formato de cadena de custodia

| Nº | Descripción | Origen | Captura (UTC) | Método y herramienta (versión) | SHA-256 | Entrega (nombre) | Recibe (nombre) | Fecha-hora traspaso (UTC) | Motivo / lugar de almacenamiento |
|----|-------------|--------|---------------|--------------------------------|---------|------------------|-----------------|---------------------------|----------------------------------|
| E01 | Triage volátil (carpeta) | VM víctima | | | | | | | |
| E02 | Script recuperado de /proc | Proceso vivo | | | | | | | |
| E03 | Memoria RAM (.lime) | VM víctima | | | | | | | |
| E04 | Imagen disco EVIDENCIA | Disco virtual | | | | | | | |
| E05 | Archivo recuperado | Imagen E04 | | | | | | | |

## Respuestas

### P1. Principios (ISO/IEC 27037)
### P2. Orden de volatilidad
### P3. Qué desapareció y qué sobrevivió
### P4. Apagado abrupto vs. ordenado
### P5. Hashes y el experimento del byte
### P6. Debilidades de su propia cadena
### P7. Línea de tiempo y mapeo a ATT&CK

## Lista de chequeo
- [ ] Cadena de custodia completa, con hash en cada traspaso
- [ ] Capturas con fecha/hora visibles de cada parte
- [ ] Archivos de evidencia con sus hashes (sin los .lime/.dd; solo logs, hashes y salidas)
- [ ] Respuestas P1–P7 y APORTES
