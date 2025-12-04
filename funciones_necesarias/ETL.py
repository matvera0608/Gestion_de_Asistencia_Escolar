import traceback
from tkinter import messagebox as mensajeTexto, filedialog as diálogoArchivo
from dateutil.parser import parse
import pandas as pd
import os, difflib
from Conexión import *
from .Fun_adicionales import *

#IMPORTACIÓN PARA CREAR PDF#
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, SimpleDocTemplate

# --- Función principal ---
def sanear_archivo(path):
     ext = path.lower().split(".")[-1]
     # Separador: 2+ espacios, o tab, o punto y coma
     sep_regex = r"\s{2,}|\t|;"
     # Detectar encoding real
     encoding = detectar_encoding(path)
     # print(f"→ Leyendo archivo con encoding detectado: {encoding}")
     
     # Cargar según el tipo
     if ext in ["csv", "txt"]:
          df = pd.read_csv(path, encoding=encoding, sep=sep_regex, engine="python", skip_blank_lines=True)
     elif ext == "xlsx":
          df = pd.read_excel(path)
     else:
          raise ValueError("Formato no soportado")
     
     df = df.loc[:, ~df.columns.str.contains("unnamed", case=False)] #No sé si está bien acá el orden del df
     df.dropna(axis=1, how="all")
     # -------------------------------
     # NORMALIZAR SOLO ENCABEZADOS
     # -------------------------------
     # print("→ Saneando encabezados...")
     df.columns = [normalizar_encabezado(c) for c in df.columns]
     # -------------------------------
     # NORMALIZAR SOLO VALORES
     # -------------------------------
     # print("→ Saneando valores...")
     for col in df.columns:
          df[col] = df[col].apply(normalizar_valor)

     print("→ Archivo saneado correctamente.")
     return df

def convertir_datos_para_mysql(valor):
     """ ACÁ ME ASEGURO DE CONVERTIR LOS DATOS PARA SQL COMO FECHA Y HORA,
     PORQUE LA DB ES MUY ESTRICTA CON LOS VALORES"""
     if valor is None:
          return None
     if not isinstance(valor, str):
          return valor
     
     v = valor.strip()
     if v == "":
          return None
     
     try:
          dt = parse(v, dayfirst=True)
     except:
          return 
     
     
     sólo_tipo_fecha = dt.time().hour == 0 and dt.time().minute == 0 and dt.time().second == 0 \
          and not any(c in v for c in [":"])
     sólo_tipo_hora = any(c in v for c in [":"]) and not any(c in v for c in ["-", "/"])
     
     if sólo_tipo_fecha:
          dt.strftime("%Y-%m-%d")
     if sólo_tipo_hora:
          dt.strftime("%H:%M:%S")
     
     return dt.strftime("%Y-%m-%d %H:%M:%S")

def seleccionar_archivo_siguiendo_extension(nombre_de_la_tabla):
     tipos_de_archivos = (
     ("bloc de notas","*.txt"),
     ("hoja con comas separadas","*.csv"),
     ("hoja de excel","*.xlsx"),)
     
     ruta_archivo = diálogoArchivo.askopenfilename(
     title="Seleccionar archivo a importar",
     filetypes=tipos_de_archivos
     )
     
     _, extensión = os.path.splitext(ruta_archivo)
     extensión = extensión.lower().replace(".", "")
     
     if not ruta_archivo:
          return None, None

     if "." not in ruta_archivo:
          mensajeTexto.showerror("Error", "El archivo seleccionado no tiene extensión válida.")
          return None, None
     
     try:
          datos_crudos = sanear_archivo(ruta_archivo)
     except Exception as e:
          mensajeTexto.showerror("Error al leer archivo", str(e))
          return None, None
     try:
          datos = validar_archivo(ruta_archivo, nombre_de_la_tabla, alias, campos_en_db, datos_crudos)
          if datos is None:
               return None, None
     except Exception as e:
          detalle = traceback.format_exc()  # stack completo
          mensajeTexto.showerror("Error al validar archivo",
               f"Tipo: {type(e).__name__}\nMensaje: {str(e)}\n\nDetalle:\n{detalle}")
          return None, None

     return ruta_archivo, datos
 
def validar_archivo(ruta_archivo, nombre_de_la_tabla, alias, campos_en_db, datos):
     # filas → ya sanitizadas
     # aquí solo validás:
     # - que las columnas coincidan
     # - que los tipos sean correctos
     # - que claves foráneas existan
     # - que no haya vacíos en campos obligatorios
     
     """ VALIDAMOS EL ARCHIVO ASEGURANDO QUE EL NOMBRE SE LLAME EXACTAMENTE IGUAL, DETECTANDO LOS CAMPOS QUE REALMENTE EXISTAN,
     DESPUÉS SI FALTAN QUE TIRE UN AVISO Y QUE VERIFIQUE UN REGISTRO INVÁLIDO """
     
     #===================================================================
     # 1. VALIDACIÓN INTELIGENTE DEL NOMBRE DE ARCHIVO DONDE TENGAN UNA SIMILITUD
     #===================================================================
     errores = []
     similitud = 0.85
     nombre_de_archivo= os.path.splitext(os.path.basename(ruta_archivo))[0]
     nombre_de_archivo_normalizado = nombre_de_archivo.lower().replace("_", "").replace(" ", "")
     nombre_de_la_tabla_normalizado = nombre_de_la_tabla.lower().replace("_", "").replace(" ", "")

     # Intentar coincidencias aproximadas
     mejor_coincidencia = difflib.get_close_matches(nombre_de_archivo_normalizado, [nombre_de_la_tabla_normalizado.lower()] , n=1, cutoff=similitud)

     
     if not mejor_coincidencia:
          errores.append(f"El nombre del archivo {os.path.basename(ruta_archivo)} no coincide con la tabla {nombre_de_la_tabla}")
          
     #===================================================================
     # 2. VALIDACIÓN INTELIGENTE DE NOMBRE DE CAMPOS CON EL FIN DE FLEXIBILIZAR UN POCO 
     #===================================================================
     
     campos_oficiales = campos_en_db.get(nombre_de_la_tabla, [])
     campos_oficiales_normalizados = [normalizar_encabezado(c) for c in campos_oficiales]
     alias_invertido = {normalizar_encabezado(v): k for k, v in alias.items()}
     alias_válidos = list(alias_invertido.keys()) + campos_oficiales_normalizados
     columnas_finales_de_campos = []
     
     #Se recorre con un for el archivo para validar cada atributo dentro del archivo.
     for columna_original in datos.columns:
          c_norm = normalizar_encabezado(columna_original)
          # 1) Coincidencia exacta por alias
          if c_norm in alias_invertido:
               columnas_finales_de_campos.append(alias_invertido[c_norm])
               continue
          # 2) Coincidencia exacta por nombre oficial
          if c_norm in campos_oficiales_normalizados:

               indice = campos_oficiales_normalizados.index(c_norm)
               columnas_finales_de_campos.append(campos_oficiales[indice])
               continue

          # 3) Coincidencia aproximada (difflib)
          mejor = difflib.get_close_matches(c_norm, alias_válidos, n=1, cutoff=similitud)
          if mejor:
               mejor_norm = mejor[0]
               if mejor_norm in alias_invertido:
                    columnas_finales_de_campos.append(alias_invertido[mejor_norm])
               else:
                    # Es un nombre oficial
                    indice = campos_oficiales_normalizados.index(mejor_norm)
                    columnas_finales_de_campos.append(campos_oficiales[indice])
               continue

          # 4) Nada coincide → inválido
          errores.append(f"El encabezado «{columna_original}» no coincide con ningún campo de la tabla {nombre_de_la_tabla}")
     
     
     #----------------------------------------------
     # VALIDACIÓN: misma cantidad de columnas
     #----------------------------------------------
     if len(columnas_finales_de_campos) == len(datos.columns):
          datos.columns = columnas_finales_de_campos
     elif len(columnas_finales_de_campos) != len(datos.columns):
          errores.append(f"El archivo tiene {len(datos.columns)} columnas, "f"pero solo se pudieron mapear {len(columnas_finales_de_campos)}."
          )
          mensajeTexto.showerror("ERROR DE COLUMNAS", "\n".join(errores))
          return None
     
     #===================================================================
     # 3. VALIDACIÓN INTELIGENTE DE CAMPOS INVÁLIDOS
     #===================================================================
     campos_invalidos = [c for c in columnas_finales_de_campos if c and c not in campos_oficiales]
     if campos_invalidos:
          errores.append(f"Los siguientes campos no existen en la tabla {nombre_de_la_tabla}: {', '.join(campos_invalidos)}")
          
     #===================================================================
     # 4. VALIDACIÓN INTELIGENTE DE CAMPOS FALTANTES
     #===================================================================
     
     campos_faltantes = [c for c in campos_oficiales if c not in columnas_finales_de_campos]
     if campos_faltantes:
          errores.append(f"Faltan columnas obligatorias en el archivo: {', '.join(campos_faltantes)}")
          

     #===================================================================
     # 5. VALIDACIÓN DE CANTIDAD DE CAMPOS
     #===================================================================
     
     for i, fila in enumerate(datos.values): #Validar largo de la fila
          if len(fila) != len(campos_oficiales):
               errores.append(f"❌ Error en registro {i+1}: cantidad de valores incorrecta ({len(fila)} en vez de {len(campos_oficiales)})")
              
     #===================================================================
     # 6. TRADUCCIÓN DE CAMPOS CLAVES O CRUDOS A NOMBRES LEGIBLES
     #===================================================================
     
      # Mostrar todos los errores juntos
     if errores:
          mensajeTexto.showerror("ERROR DE IMPORTACIÓN", "\n".join(errores))
          return None

     # 6. Traducción de IDs
     filas_traducidas = []
     for _, fila in datos.iterrows():
          traduccion, error = traducir_IDs(nombre_de_la_tabla, fila)
          if error:
               errores.append(f"❌ {error}")
          else:
               filas_traducidas.append(traduccion)

     if errores:
          mensajeTexto.showerror("ERROR DE DATOS", "\n".join(errores))
          return None

     return pd.DataFrame(filas_traducidas)

def normalizar_datos(datos):
     for columna in datos.columns:
          columna_lower = columna.lower()
          if "fecha" in columna_lower or "horario" in columna_lower:
               datos[columna] = datos[columna].map(convertir_datos_para_mysql)
          
          for i, valor in enumerate(datos[columna]):
               if isinstance(valor, str) and (valor.count('/') > 0 or valor.count(':') > 2):
                    mensajeTexto.showerror("ERROR DE DATOS", f"❌ Error en fila {i+1}, columna '{columna}': valor inválido '{valor}'")
                    return None
     return datos

def subir_DataFrame(nombre_de_la_tabla, datos):
     """ ACÁ SUBIMOS EL DATAFRAME OBTENIENDO EL CAMPO ID, 
     PREPARANDO LOS PARÁMETROS PARA SUBIR INCLUSO SI LOS CAMPOS TIENEN NOMBRES DISTINTOS A SQL """
     if conseguir_campo_ID(nombre_de_la_tabla) in datos.columns:
          datos = datos.drop(columns=[conseguir_campo_ID(nombre_de_la_tabla)])
     
     columnas = datos.columns.tolist()
     columna_con_acentos = [f"`{columna}`" for columna in columnas]
     campos = ', '.join(columna_con_acentos)
     placeholder = ', '.join(['%s'] * len(columnas))
     
     consulta_sql = f"INSERT INTO {nombre_de_la_tabla} ({campos}) VALUES ({placeholder})"
     
     valores = [tuple(fila) for fila in datos.values]
     
     
     with conectar_base_de_datos() as conexión:
          cursor = conexión.cursor()
          cursor.executemany(consulta_sql, valores)
          conexión.commit()
     
     desconectar_base_de_datos(conexión)
     return valores

def crear_PDF(ruta_archivo, datos, nombre_de_la_tabla):
     pdf = SimpleDocTemplate(
     ruta_archivo,
     pagesize=A4,
     rightMargin=40, leftMargin=40,
     topMargin=20, bottomMargin=40
     )

     estilos = getSampleStyleSheet()
     
     título_con_estilo = ParagraphStyle(
     'título',
     parent=estilos['Title'],
     fontName='Helvetica-Bold',
     fontSize=25,
     alignment=1,
     spaceAfter=25
     )

     
     encabezado_estilo = ParagraphStyle(
     'encabezado',
     parent=estilos['Normal'],
     fontName='Helvetica-Bold',
     fontSize=16,
     alignment=1
     )

     celda_estilo = ParagraphStyle(
     'celda',
     parent=estilos['Normal'],
     fontName='Helvetica',
     fontSize=12,
     alignment=1
     )
     
     datos_con_estilo = []
     for i, fila in enumerate(datos):
          estilo = encabezado_estilo if i == 0 else celda_estilo
          datos_con_estilo.append([Paragraph(str(c), estilo) for c in fila])

     tabla = Table(datos_con_estilo, repeatRows=1)
     
     tabla.setStyle(TableStyle([
     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
     ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
     ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
     ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#5d5dff")),
     ('FONTSIZE', (0, 0), (-1, 0), 12),
     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
     ('GRID', (0, 0), (-1, -1), 0.8, colors.black),
     ('BOX', (0, 0), (-1, -1), 1, colors.black),
     ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#bef6ff")]),
     ]))
     
     titulo = Paragraph(f"<b>Reporte de {nombre_de_la_tabla.capitalize()}</b>", título_con_estilo)
     espacio = Spacer(1, 30)

     pdf.build([titulo, espacio, tabla])