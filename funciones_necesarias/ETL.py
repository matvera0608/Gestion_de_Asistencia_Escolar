from datetime import datetime
import re
from dateutil.parser import parse
from tkinter import messagebox as mensajeTexto, filedialog as diálogoArchivo
import csv
import pandas as pd
import os
from Conexión import *
from .Fun_adicionales import *

def convertir_datos_para_mysql(valor):
     """ ACÁ ME ASEGURO DE CONVERTIR LOS DATOS PARA SQL COMO FECHA Y HORA,
     PORQUE LA DB ES MUY ESTRICTA CON LOS VALORES"""
     if valor is None:
          return None
     if not isinstance(valor, str):
          return valor
     try:
          v = valor.strip()
          # → Si es un horario (formato HH:MM o HH:MM:SS) 
          if re.fullmatch(r"\d{1,2}:\d{2}(:\d{2})?", v): 
               try: 
                    t = datetime.strptime(v, "%H:%M:%S") if ":" in v[3:] \
                    else datetime.strptime(v, "%H:%M")
                    return t.strftime("%H:%M:%S") 
               except:
                    return None # → Si es una fecha (formato YYYY-MM-DD o DD/MM/YYYY) 
          
          if re.fullmatch(r"\d{4}-\d{2}-\d{2}", v) or re.fullmatch(r"\d{2}/\d{2}/\d{4}", v): 
               try: 
                    d = parse(v, dayfirst=True) 
                    return d.strftime("%Y-%m-%d") 
               except: 
                    return None # → De lo contrario, devolver texto return v 
     except Exception:
          return v
 
def seleccionar_archivo_siguiendo_extension(nombre_de_la_tabla, treeview):
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
        return
     if "." not in ruta_archivo:
          mensajeTexto.showerror("Error", "El archivo seleccionado no tiene extensión válida.")
          return
     
     match extensión:
          case "xlsx":
               try:
                    datos = pd.read_excel(ruta_archivo)
               except Exception as e:
                    mensajeTexto.showerror("Error al leer Excel", str(e))
                    return
          case "csv":
               datos = pd.read_csv(ruta_archivo,sep="\t",engine="python" ,encoding="utf-8")
          case "txt":
               with open(ruta_archivo, "r", encoding="utf-8") as archivo:
                    lector = csv.reader(archivo, delimiter="\t")
                    filas = list(lector)
          
               encabezado = [col.strip() for col in filas[0]]
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
               datos = validar_archivo(ruta_archivo, nombre_de_la_tabla, alias, campos_en_db, treeview, datos_crudos)
               if datos is None:
                    return None, None
          case _:
               print("No compatible el formato de archivo")
               return

     return ruta_archivo, datos
 
def validar_archivo(ruta_archivo, nombre_de_la_tabla, alias, campos_en_db, treeview, datos):
     """ VALIDAMOS EL ARCHIVO ASEGURANDO QUE EL NOMBRE SE LLAME EXACTAMENTE IGUAL, DETECTANDO LOS CAMPOS QUE REALMENTE EXISTAN,
     DESPUÉS SI FALTAN QUE TIRE UN AVISO Y QUE VERIFIQUE UN REGISTRO INVÁLIDO """
     
     #Se agregó más control, cuando el nombre del archivo no coincide exactamente con una de las tablas tira un error loco
     nombre_de_archivo_base = os.path.splitext(os.path.basename(ruta_archivo))[0].lower()
          
     if nombre_de_archivo_base not in nombre_de_la_tabla.lower() and \
     nombre_de_la_tabla.lower() not in nombre_de_archivo_base:
          mensajeTexto.showerror("ERROR DE IMPORTACIÓN", f"El nombre del archivo {os.path.basename(ruta_archivo)} no coincide con la tabla {nombre_de_la_tabla}")
          return
     
     #Este sirve para obtener los campos
     campos_oficiales = campos_en_db.get(nombre_de_la_tabla, [])
     alias_invertido = {v.strip(): k for k, v in alias.items()}
     campos_archivo_aliasados = [alias_invertido.get(c.strip(), c.strip()) for c in datos.columns if c.strip()]

     # Verificar que todos los campos del archivo estén en la tabla
     campos_invalidos = [c for c in campos_archivo_aliasados if c and c not in campos_oficiales]
     if campos_invalidos:
          mensajeTexto.showerror("ERROR DE IMPORTACIÓN", f"Los siguientes campos no existen en la tabla {nombre_de_la_tabla}: {', '.join(campos_invalidos)}")
          return
     
     campos_faltantes = [c for c in campos_oficiales if c not in campos_archivo_aliasados]
     if campos_faltantes:
          mensajeTexto.showerror("ERROR DE IMPORTACIÓN",f"Faltan columnas obligatorias en el archivo: {', '.join(campos_faltantes)}")
          return
     
     for i, fila in enumerate(datos.values): #Validar largo de la fila
          if len(fila) != len(campos_oficiales):
               mensajeTexto.showerror("ERROR DE IMPORTACIÓN",f"❌ Error en registro {i+1}: cantidad de valores incorrecta ({len(fila)} en vez de {len(campos_oficiales)})")
               return

     filas_traducidas_a_nombres_legibles = []
     
     for _, fila in datos.iterrows():
          dict_fila = fila.to_dict()
          traducción, error = traducir_IDs(nombre_de_la_tabla, dict_fila)
          if error:
               mensajeTexto.showerror(f"ERROR DE DATOS", f"❌ {error}")
               return
     
          filas_traducidas_a_nombres_legibles.append(traducción)
     datos = pd.DataFrame(filas_traducidas_a_nombres_legibles)
    
     for columna in datos.columns:
          columna_lower = columna.lower()
          if "fecha" in columna_lower or "horario" in columna_lower:
               datos[columna] = datos[columna].apply(convertir_datos_para_mysql)
          
          if datos[columna].apply(lambda x: isinstance(x, str) and (x.count('/') > 0 or x.count(':') > 2)).any():
               mensajeTexto.showerror(f"ERROR DE DATOS", f"❌ Formato de fecha/hora inválido en la columna '{columna}' después de la conversión. Revise el archivo original.")
               return
           
     for _, fila in datos.iterrows():
          treeview.insert("", "end", values=tuple(fila))
          
     return datos
       
def subir_DataFrame(nombre_de_la_tabla):
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