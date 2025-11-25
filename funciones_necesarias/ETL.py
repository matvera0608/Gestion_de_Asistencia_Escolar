import re
from tkinter import messagebox as mensajeTexto, filedialog as diálogoArchivo
from dateutil.parser import parse
import csv
import pandas as pd
import os, difflib
from Conexión import *
from .Fun_adicionales import *

#IMPORTACIÓN PARA CREAR PDF#
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, SimpleDocTemplate

def normalizar_expresión(s):
     return s.strip().lower()

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
     
     match extensión:
          case "xlsx":
               try:
                    datos = pd.read_excel(ruta_archivo)
               except Exception as e:
                    mensajeTexto.showerror("Error al leer Excel", str(e))
                    return None, None
          case "csv":
               datos = pd.read_csv(ruta_archivo,sep="\t",engine="python" ,encoding="utf-8")
          case "txt":
               with open(ruta_archivo, "r", encoding="utf-8") as archivo:
                    contenido = archivo.read()
                    contenido = re.sub(r"\t+", "\t", contenido)  # reemplaza múltiples tabulaciones por una sola. Si el txt tiene tabulaciones adicionales limpia para la importación
                    lector = csv.reader(contenido.splitlines(), delimiter="\t")
                    filas = list(lector)


               encabezado = [col.strip() for col in filas[0]]
               if not filas or len(filas) < 1:
                    mensajeTexto.showerror("Error", "El archivo está vacío o mal formateado.")
                    return None, None
               num_columnas = len(encabezado)

               filas_limpias = []
               for fila in filas[1:]:
                    fila_limpia = [c.strip() for c in fila]

                    if len(fila_limpia) < num_columnas:
                         fila_limpia += [""] * (num_columnas - len(fila_limpia))

                    elif len(fila_limpia) > num_columnas:
                         fila_limpia = fila_limpia[:num_columnas]

                    filas_limpias.append(fila_limpia)
              
               datos_crudos = pd.DataFrame(filas_limpias, columns=encabezado)
               datos_crudos.columns = [c.strip() for c in datos_crudos.columns]
               datos = validar_archivo(ruta_archivo, nombre_de_la_tabla, alias, campos_en_db, datos_crudos)
               if datos is None:
                    return None, None
          case _:
               print("No compatible el formato de archivo")
               return None, None

     return ruta_archivo, datos
 
def validar_archivo(ruta_archivo, nombre_de_la_tabla, alias, campos_en_db, datos):
     """ VALIDAMOS EL ARCHIVO ASEGURANDO QUE EL NOMBRE SE LLAME EXACTAMENTE IGUAL, DETECTANDO LOS CAMPOS QUE REALMENTE EXISTAN,
     DESPUÉS SI FALTAN QUE TIRE UN AVISO Y QUE VERIFIQUE UN REGISTRO INVÁLIDO """
     
     #===================================================================
     # 1. VALIDACIÓN INTELIGENTE DEL NOMBRE DE ARCHIVO DONDE TENGAN UNA SIMILITUD
     #===================================================================
     
     #Se agregó más control, cuando el nombre del archivo no coincide exactamente con una de las tablas tira un error loco
     nombre_de_archivo= os.path.splitext(os.path.basename(ruta_archivo))[0]
     nombre_de_archivo_normalizado = nombre_de_archivo.lower().replace("_", "").replace(" ", "")
     nombre_de_la_tabla_normalizado = nombre_de_la_tabla.lower().replace("_", "").replace(" ", "")

     # Intentar coincidencias aproximadas
     mejor_coincidencia = difflib.get_close_matches(nombre_de_archivo_normalizado, [nombre_de_la_tabla_normalizado.lower()] , n=1, cutoff=0.85)

     
     if not mejor_coincidencia:
          mensajeTexto.showerror("ERROR DE IMPORTACIÓN", f"El nombre del archivo {os.path.basename(ruta_archivo)} no coincide con la tabla {nombre_de_la_tabla}")
          return
     
     #===================================================================
     # 2. VALIDACIÓN INTELIGENTE DE NOMBRE DE CAMPOS CON EL FIN DE FLEXIBILIZAR UN POCO 
     #===================================================================
     
     #Variables para flexibilizar el nombre de los campos para la importación de datos
     campos_oficiales = campos_en_db.get(nombre_de_la_tabla, [])
     campos_oficiales_normalizados = [normalizar_expresión(c) for c in campos_oficiales]
     alias_invertido = {normalizar_expresión(v): k for k, v in alias.items()}
     alias_válidos = list(alias_invertido.keys()) + campos_oficiales_normalizados
     columnas_finales_de_campos = []
     
     #Se recorre con un for el archivo para validar cada atributo dentro del archivo.
     for columna_original in datos.columns:
        c_norm = normalizar_expresión(columna_original)
        # 1) Coincidencia exacta por alias
        if c_norm in alias_invertido:
          columnas_finales_de_campos.append(alias_invertido[c_norm])
          continue
        # 2) Coincidencia exacta por nombre oficial
        if c_norm in campos_oficiales_normalizados:
          # Buscar el nombre original respetando mayúsculas/minúsculas
          indice = campos_oficiales_normalizados.index(c_norm)
          columnas_finales_de_campos.append(campos_oficiales[indice])
          continue
       
        # 3) Coincidencia aproximada (difflib)
        mejor = difflib.get_close_matches(c_norm, alias_válidos, n=1, cutoff=0.85)
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
        mensajeTexto.showerror(
            "ERROR DE IMPORTACIÓN",
            f"El encabezado «{columna_original}» no coincide con ningún campo de la tabla {nombre_de_la_tabla}."
        )
        return
     
     
     datos.columns = columnas_finales_de_campos
     
     #===================================================================
     # 3. VALIDACIÓN INTELIGENTE DE CAMPOS INVÁLIDOS
     #===================================================================
     
     # Verificar que todos los campos del archivo estén en la tabla
     campos_invalidos = [c for c in columnas_finales_de_campos if c and c not in campos_oficiales]
     if campos_invalidos:
          mensajeTexto.showerror("ERROR DE IMPORTACIÓN", f"Los siguientes campos no existen en la tabla {nombre_de_la_tabla}: {', '.join(campos_invalidos)}")
          return
     
     #===================================================================
     # 4. VALIDACIÓN INTELIGENTE DE CAMPOS FALTANTES
     #===================================================================
     
     campos_faltantes = [c for c in campos_oficiales if c not in columnas_finales_de_campos]
     if campos_faltantes:
          mensajeTexto.showerror("ERROR DE IMPORTACIÓN",f"Faltan columnas obligatorias en el archivo: {', '.join(campos_faltantes)}")
          return
     
     #===================================================================
     # 5. VALIDACIÓN DE CANTIDAD DE CAMPOS
     #===================================================================
     
     for i, fila in enumerate(datos.values): #Validar largo de la fila
          if len(fila) != len(campos_oficiales):
               mensajeTexto.showerror("ERROR DE IMPORTACIÓN",f"❌ Error en registro {i+1}: cantidad de valores incorrecta ({len(fila)} en vez de {len(campos_oficiales)})")
               return
     
     #===================================================================
     # 6. TRADUCCIÓN DE CAMPOS CLAVES O CRUDOS A NOMBRES LEGIBLES
     #===================================================================
     
     
     filas_traducidas = []
     
     for _, fila in datos.iterrows():
          dict_fila = fila.to_dict()
          traducción, error = traducir_IDs(nombre_de_la_tabla, dict_fila)
          if error:
               mensajeTexto.showerror(f"ERROR DE DATOS", f"❌ {error}")
               return
     
          filas_traducidas.append(traducción)
     datos = pd.DataFrame(filas_traducidas)
    
     return datos

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
     ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#3d3dff")),
     ('FONTSIZE', (0, 0), (-1, 0), 14),
     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
     ('GRID', (0, 0), (-1, -1), 0.8, colors.black),
     ('BOX', (0, 0), (-1, -1), 1, colors.black),
     ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#bef6ff")]),
     ]))
     
     titulo = Paragraph(f"<b>Reporte de {nombre_de_la_tabla.capitalize()}</b>", título_con_estilo)
     espacio = Spacer(1, 30)

     pdf.build([titulo, espacio, tabla])