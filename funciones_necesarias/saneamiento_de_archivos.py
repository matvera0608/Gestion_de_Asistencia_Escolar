import pandas as pd, os, re, chardet

invisibles = re.compile(r"[\u00A0\u2000-\u200B\u202F\u205F\u3000\t\r\f\v]")
múltiples_espacios = re.compile(r"\s{2,}")
caracteres_raros = re.compile(r"[\"'“”‘’…•→]") 
separadores = re.compile(r"[–—\-|]")

def remover_bom(texto: str) -> str:
    BOM = "\ufeff"  # caracter BOM UTF-8
    if texto.startswith(BOM):
        return texto[len(BOM):]
    return texto


def normalizar_expresión(s):
    return s.lower().strip()

def normalizar_encabezado(columna: str) -> str:

    if columna is None:
        return ""

    columna = str(columna).strip()
    if columna == "":
        return ""
    
    columna = normalizar_expresión(columna)
    

    # Limpieza de caracteres
    columna = invisibles.sub(" ", columna)
    columna = caracteres_raros.sub("", columna)
    columna = separadores.sub("", columna)
    columna = múltiples_espacios.sub(" ", columna)


    return columna

## TE ENVÍO ESTA PARTE PORQUE BLOC DE NOTAS ES MUY PROPENSO A FALLOS
def normalizar_valor(valor):
    if pd.isna(valor):
        return None
    if isinstance(valor, str):
        s = invisibles.sub(" ", valor.strip())
        s = múltiples_espacios.sub(" ", s)
        return s
    return valor

def normalizar_línea(línea: str) -> list[str]:
    línea = remover_bom(línea)
    línea = invisibles.sub(" ", línea).strip()

    # CSV delimitadores comunes
    if "," in línea:
        return [c.strip() for c in línea.split(",")]

    if ";" in línea:
        return [c.strip() for c in línea.split(";")]

    # Tab separado
    línea = re.sub(r"[ \t]{2,}", "\t", línea)
    return línea.split("\t")

# --- Detección automática de codificación ---
def detectar_encoding(path):
    with open(path, "rb") as f:
        data = f.read(2048)
    return chardet.detect(data)["encoding"]

def sanear_archivo_diferente_a_excel(path):
    encoding = detectar_encoding(path)

    with open(path, "r", encoding=encoding, errors="ignore") as file:
        raw_lines = file.readlines()

    lineas = []
    
    for linea in raw_lines:
        # Limpieza dura
        linea = linea.replace("\ufeff", "")
        linea = linea.replace("\u00A0", " ")
        linea = linea.replace("\u200B", "")
        linea = linea.rstrip()

        if linea.strip():
            lineas.append(linea)

    if not lineas:
        raise ValueError("El archivo está vacío o no contiene datos.")


    tipo, delimitador = detectar_delimitador(lineas)

    if tipo == "regex":
        filas = [re.split(delimitador, l.strip()) for l in lineas if l.strip()]
    else:
        filas = [l.split(delimitador) for l in lineas if l.strip()]

    # Normalizar largo
    max_cols = max(len(f) for f in filas)
    filas = [f + [""] * (max_cols - len(f)) for f in filas]

    df = pd.DataFrame(filas)

    print("DEBUG columnas:", df.columns.tolist())
    print("DEBUG primera fila:", df.iloc[0].tolist())

    # Encabezados reales
    df.columns = [normalizar_encabezado(c) for c in df.iloc[0]]
    df = df.drop(index=0).reset_index(drop=True)
    
    # Normalizar valores
    for col in df.columns:
        df[col] = df[col].apply(normalizar_valor)

    # Eliminar columnas vacías
    df = df.loc[:, [c for c in df.columns if c != ""]]

    print("→ Archivo TXT saneado correctamente.")
    return df

def es_excel_valido(path):
    try:
        pd.read_excel(path, nrows=1)
        return True
    except:
        return False

def sanear_dataframe(df: pd.DataFrame) -> pd.DataFrame:
     # -----------------------------------------
     # 1. Normalizar nombres de columnas
     # -----------------------------------------
     nuevas = [normalizar_encabezado(str(col)) for col in df.columns]
     df = df.copy()          # <-- copia segura
     df.columns = nuevas

     # Eliminar columnas vacías o generadas automáticamente por pandas (como 'Unnamed: X')
     df = df.loc[:, [c for c in df.columns if c.strip() != "" and not c.lower().startswith("unnamed")]]
     # -----------------------------------------
     # 2. Normalizar valores celda por celda
     # -----------------------------------------
     for col in df.columns:
          df.loc[:, col] = df[col].astype(str).apply(normalizar_valor)

     return df

def cargar_archivo(path):
     extension = os.path.splitext(path)[1].lower()
     
     if extension in [".xlsx", ".xls"]:
          print("→ Cargando Excel sin saneo de líneas…")
          df = pd.read_excel(path)
          # Normalizar encabezados
          df.columns = [normalizar_encabezado(c) for c in df.columns]
          
          # Normalizar valores
          for col in df.columns:
               df[col] = df[col].apply(normalizar_valor)

          return df
     else:
          print("Cargando archivo delimitado (txt.csv)...")
          return sanear_archivo_diferente_a_excel(path)


def detectar_delimitador(lineas):
    if any(re.search(r"[ \t]{2,}", l) for l in lineas):
        return ("regex", r"[ \t]{2,}")

    posibles = ["\t", "|", ";", ","]
    contador = {d: sum(l.count(d) for l in lineas[:10]) for d in posibles}
    return ("literal", max(contador, key=contador.get))