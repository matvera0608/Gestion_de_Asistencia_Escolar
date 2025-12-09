import os, pandas as pd
from datetime import datetime
archivo_origen = "asistencia.txt"
archivo_destino = "asistencia.xlsx"

if not os.path.isfile(archivo_origen):
    print(f"El archivo {archivo_origen} no existe.")
    exit(1)

# Leer y separar por tabulador
with open(archivo_origen, encoding="utf-8") as f:
    lineas = [linea.strip().split("\t") for linea in f]

# Detectar la cantidad máxima de columnas
max_cols = max(len(fila) for fila in lineas)

# Normalizar todas las filas (incluyendo encabezado)
lineas_norm = [fila + [""]*(max_cols - len(fila)) for fila in lineas]

# Encabezado y datos
encabezado = lineas_norm[0]
filas = lineas_norm[1:]

# Crear DataFrame y exportar
df = pd.DataFrame(filas, columns=encabezado)
def fecha_valida(fecha):
    try:
        datetime.strptime(fecha, "%d/%m/%Y")
        return True
    except ValueError:
        return False

# Buscar la columna que contiene la palabra "fecha"
columna_fecha = next((col for col in df.columns if "fecha" in col.lower()), None)

if columna_fecha:
    df["FechaValida"] = df[columna_fecha].apply(fecha_valida)

    errores = df[df["FechaValida"] == False]

    if not errores.empty:
        print("⚠️ Se encontraron fechas inválidas:")
        print(errores[[columna_fecha]])
    else:
        print("✔ Todas las fechas son válidas")
else:
    print("⚠️ No se encontró ninguna columna que contenga 'fecha'")

df.to_excel(archivo_destino, index=False)

print(f"Conversión completa: {archivo_destino}")