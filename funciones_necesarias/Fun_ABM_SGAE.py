from Conexión import *
from .Fun_adicionales import *
from .Fun_Validación_SGAE import *
import tkinter as tk
from dateutil.parser import parse
from tkinter import messagebox as mensajeTexto, filedialog as diálogoArchivo
#IMPORTACIÓN PARA CREAR PDF#
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, SimpleDocTemplate
# from reportlab.pdfbase import pdfmetrics
# from reportlab.pdfbase.ttfonts import TTFont

#IMPORTACIÓN PARA IMPORTAR ARCHIVOS TXT, EXCEL O CSV
import csv
import pandas as pd
import os
#-------------------------------------#

def insertar_datos(nombre_de_la_tabla, cajasDeTexto, campos_db, tablas_de_datos, ventana):
  conexión = conectar_base_de_datos()
  datos = obtener_datos_de_Formulario(nombre_de_la_tabla, cajasDeTexto, campos_db)
  if not datos:
    return
  
  if detectar_repeticiones_de_datos(datos, nombre_de_la_tabla):
    mostrar_aviso(ventana, "HAY REPETICIÓN DE DATOS", colores["rojo_error"], 10)
    return
  if nombre_de_la_tabla == "materia":
    if verificar_horarioSalida_mayor_horarioEntrada(datos):
      mostrar_aviso(ventana, "EL HORARIO DE SALIDA NO PUEDE SER MENOR O IGUAL\n QUE EL HORARIO DE ENTRADA", colores["rojo_error"], 8)
      return

  datos_traducidos, error = traducir_IDs(nombre_de_la_tabla, datos)
  
  if error:
    mostrar_aviso(ventana, f"❌ {error}", colores["rojo_error"], 10)
    return
  
  if datos_traducidos is None:
    return

  campos = ', '.join(datos_traducidos.keys())
  valores = ', '.join(['%s'] * len(datos_traducidos))
  consulta = f"INSERT INTO {nombre_de_la_tabla} ({campos}) VALUES ({valores})"
  valores_sql = list(datos_traducidos.values())
  try:
    cursor = conexión.cursor()
    cursor.execute(consulta, tuple(valores_sql))
    conexión.commit()
    datos = consultar_tabla(nombre_de_la_tabla)
    
    for item in tablas_de_datos.get_children():
      tablas_de_datos.delete(item)
    
    for índice, fila in enumerate(datos):
      id_val = fila[0]
      valores_visibles = fila[1:]
      tag = "par" if índice % 2 == 0 else "impar"
      
      tablas_de_datos.insert("", "end", iid=str(id_val), values=valores_visibles, tags=(tag,))
          
    campos_oficiales = campos_en_db.get(nombre_de_la_tabla, [])
    
    for i, campo in enumerate(campos_oficiales):
      try:
        entry = cajasDeTexto[nombre_de_la_tabla][i]
      except (KeyError, IndexError):
        continue
      if not entry.winfo_exists():
        continue
      entry.delete(0, tk.END)
    mostrar_aviso(ventana, "✅ SE AGREGÓ LOS DATOS NECESARIOS", colores["verde_éxito"], 10)
  except Exception as e:
    print(f"HA OCURRIDO UN ERROR AL GUARDAR LOS DATOS: {str(e)}")
    return False
  finally:
    desconectar_base_de_datos(conexión)

def modificar_datos(nombre_de_la_tabla, cajasDeTexto, campos_db, tablas_de_datos, ventana):
  selección = obtener_selección(tablas_de_datos)
  if not selección:
    return
  if not hasattr(tablas_de_datos, "winfo_exists") or not tablas_de_datos.winfo_exists():
    return
  
  selección = tablas_de_datos.selection()
  if not selección:
    return
  
  try:
    iid = selección[0]
    idSeleccionado = int(iid)
  except ValueError:
    idSeleccionado = iid

  datos = obtener_datos_de_Formulario(nombre_de_la_tabla, cajasDeTexto, campos_db)
  if not datos:
    return
  
  if nombre_de_la_tabla == "materia":
    if verificar_horarioSalida_mayor_horarioEntrada(datos):
      mostrar_aviso(ventana, "EL HORARIO DE SALIDA NO PUEDE SER MENOR\n QUE EL HORARIO DE ENTRADA", colores["rojo_error"], 8)
      return
  
  datos_traducidos, error = traducir_IDs(nombre_de_la_tabla, datos)
  
  if error:
    mostrar_aviso(ventana, f"❌ {error}", colores["rojo_error"], 10)
    return
  
  if datos_traducidos is None or not datos_traducidos:
    return
  
  valores_sql = list(datos_traducidos.values())
  campos_sql = [f"{cam} = %s" for cam in datos_traducidos.keys()]
  set_sql = ', '.join(campos_sql)
  CampoID = conseguir_campo_ID(nombre_de_la_tabla)
  consulta = f"UPDATE {nombre_de_la_tabla} SET {set_sql} WHERE {CampoID} = %s"
  
  valores_sql.append(idSeleccionado)
  try:
    with conectar_base_de_datos() as conexión:
      try:
        cursor = conexión.cursor()
        cursor.execute(consulta, tuple(valores_sql))
        conexión.commit()
      finally:
        desconectar_base_de_datos(conexión)
      datos = consultar_tabla(nombre_de_la_tabla)

      for item in tablas_de_datos.get_children():
          tablas_de_datos.delete(item)

      for índice, fila in enumerate(datos):
        id_val = fila[0]
        valores_visibles = fila[1:]
        tag = "par" if índice % 2 == 0 else "impar"
       
        tablas_de_datos.insert("", "end", iid=str(id_val), values=valores_visibles, tags=(tag,))
      campos_oficiales = campos_en_db.get(nombre_de_la_tabla, [])
    
      for i, campo in enumerate(campos_oficiales):
        try:
          entry = cajasDeTexto[nombre_de_la_tabla][i]
        except (KeyError, IndexError):
          continue
        if not entry.winfo_exists():
          continue
        entry.delete(0, tk.END)    
      # for caja in cajasDeTexto[nombre_de_la_tabla]:
      #   caja.delete(0, tk.END)
      mostrar_aviso(ventana, "✅ SE MODIFICÓ EXITOSAMENTE LOS DATOS", colores["verde_éxito"], 10)
  except Exception as e:
    print(f"HA OCURRIDO UN ERROR AL GUARDAR LOS DATOS: {str(e)}")
    return False
  
def eliminar_datos(nombre_de_la_tabla, cajasDeTexto, tablas_de_datos, ventana):
  if not hasattr(tablas_de_datos, "winfo_exists") or not tablas_de_datos.winfo_exists():
    return
  
  selección = tablas_de_datos.selection()
  
  if not selección:
    return
  
  try:
    iid = selección[0]
    ID_Seleccionado = int(iid)
  except ValueError:
    ID_Seleccionado = iid

  try:
    with conectar_base_de_datos() as conexión:
      cursor = conexión.cursor()
      CampoID = conseguir_campo_ID(nombre_de_la_tabla)
      if not CampoID:
        return
      query = f"DELETE FROM {nombre_de_la_tabla} WHERE {CampoID} = %s"
      cursor.execute(query, (ID_Seleccionado,))
      conexión.commit()

      for item in tablas_de_datos.get_children():
        tablas_de_datos.delete(item)

      datos = consultar_tabla(nombre_de_la_tabla)

      for índice, fila in enumerate(datos):
        id_val = fila[0]
        valores_visibles = fila[1:]
        tag = "par" if índice % 2 == 0 else "impar"
        tablas_de_datos.insert("", "end", iid=str(id_val), values=valores_visibles, tags=(tag,))
      
      for entry in cajasDeTexto[nombre_de_la_tabla]:
        entry.delete(0, tk.END)
      mostrar_aviso(ventana, "✅ SE ELIMINÓ UNA COLUMNA", colores["verde_éxito"], 10)
  except Exception as e:
    print(f"HA OCURRIDO UN ERROR AL GUARDAR LOS DATOS: {str(e)}")
    return False


def importar_datos(nombre_de_la_tabla, tablas_de_datos):
  global datos_en_cache
  #Convierte los datos de fecha y hora para SQL
  def convertir_datos_para_mysql(valor):
    if not isinstance(valor, str):
      return valor
    
    try:
      parsed_date = parse(valor, dayfirst=True)
      
      if parsed_date.hour != 0 and parsed_date.minute != 0:
        return parsed_date.strftime("%H:%M:%S")

      else:
        return parsed_date.strftime("%Y-%m-%d")
    
    except Exception:
      return valor
  
  try:
    if not hasattr(tablas_de_datos, "winfo_exists") or not tablas_de_datos.winfo_exists():
      print("La tabla visual no existe o fue cerrada.")
      return
    #Esta es una tupla que contiene tipos de archivos para la importación de datos
    tipos_de_archivos = (
      ("bloc de notas","*.txt"),
      ("hoja con comas separadas","*.csv"),
      ("hoja de excel","*.xslx"))
    
    ruta_archivo = diálogoArchivo.askopenfilename(
        title="Seleccionar archivo a importar",
        filetypes=tipos_de_archivos
      )
  
    extensión = ruta_archivo.split(".")[-1].lower() #<= Obtiene la extensión del archivo, el -1 es para tomar la última parte después del punto, si pusiera 0 tomaría todo el nombre del archivo.
    
    if not ruta_archivo:
      return
    
    #Se agregó más control, cuando el nombre del archivo no coincide exactamente con una de las tablas tira un error loco
    nombre_de_archivo_base = os.path.splitext(os.path.basename(ruta_archivo))[0].lower()
    
    if nombre_de_archivo_base not in nombre_de_la_tabla.lower() and nombre_de_la_tabla.lower() not in nombre_de_archivo_base:
      mensajeTexto.showerror("ERROR DE IMPORTACIÓN", f"El nombre del archivo {os.path.basename(ruta_archivo)} no coincide con la tabla {nombre_de_la_tabla}")
      return
    
    match extensión:
      case "xlsx":
        datos = pd.read_excel(ruta_archivo, encoding="utf-8")
      case "csv":
        datos = pd.read_csv(ruta_archivo,sep="\t",engine="python" ,encoding="utf-8")
        datos = datos.rename(columns=alias)
      case "txt":
        with open(ruta_archivo, "r", encoding="utf-8") as archivo:
          lector = csv.reader(archivo, delimiter="\t")
          datos = list(lector)
          
        encabezado = [col for col in datos[0] if col.strip() != ""]
        filas = [[celda for celda in fila if celda.strip() != ""] for fila in datos[1:]]
        
        datos = pd.DataFrame(filas, columns=encabezado)
        datos = datos.rename(columns=alias)
      case _:
        print("No compatible el formato de archivo")
        return

    for índice, fila in datos.iterrows():
      tablas_de_datos.insert("", "end", values=tuple(fila))
    
    alias_invertido = {v: k for k, v in alias.items()}
    datos = datos.rename(columns=alias_invertido)
    
    filas_traducidas_a_nombres_legibles = []
    
    for _, fila in datos.iterrows():
      dict_fila = fila.to_dict()
      traducción, error = traducir_IDs(nombre_de_la_tabla, dict_fila)
      if error:
        mensajeTexto.showerror(f"ERROR DE DATOS", f"❌ {error}")
        return
      
      filas_traducidas_a_nombres_legibles.append(traducción)
    datos = pd.DataFrame(filas_traducidas_a_nombres_legibles)
    
    # ----------------------------------------------------------------------
    # 3. NORMALIZACIÓN DE FECHAS/HORAS PARA MYSQL
    # ----------------------------------------------------------------------
    for columna in datos.columns:
      columna_lower = columna.lower()
    
      if "fecha" in columna_lower or "horario" in columna_lower:
        datos[columna] = datos[columna].apply(convertir_datos_para_mysql)
        
        if datos[columna].apply(lambda x: isinstance(x, str) and (x.count('/') > 0 or x.count(':') > 2)).any():
          mensajeTexto.showerror(f"ERROR DE DATOS", f"❌ Formato de fecha/hora inválido en la columna '{columna}' después de la conversión. Revise el archivo original.")
          return
    
    if conseguir_campo_ID(nombre_de_la_tabla) in datos.columns:
      datos = datos.drop(columns=[conseguir_campo_ID(nombre_de_la_tabla)])
    
    columnas = datos.columns.tolist()
    columna_con_acentos = [f"`{columna}`" for columna in columnas]
    campos = ', '.join(columna_con_acentos)
    placeholder = ', '.join(['%s'] * len(columnas))
    
    consulta_sql = f"INSERT INTO {nombre_de_la_tabla} ({campos}) VALUES ({placeholder})"
    
    valores_a_importar = [tuple(fila) for fila in datos.values]
    
    #Acá comienza la importación de los registros, es decir, sube a la base de datos
    with conectar_base_de_datos() as conexión:
      cursor = conexión.cursor()
      cursor.executemany(consulta_sql, valores_a_importar)
      conexión.commit()
      
    for item in tablas_de_datos.get_children():
      tablas_de_datos.delete(item)
    
    datos_actualizados = consultar_tabla(nombre_de_la_tabla)
    
    desconectar_base_de_datos(conexión) #DESCONECTO LA BASE DE DATOS EN CASO DE QUE NO USE MÁS, AYUDA A QUE LA CONEXIÓN NO SE LLENE EN MEMORIA.
    
    for índice, fila in enumerate(datos_actualizados): #Este crea el diseño zebra rows iterando 2 variables como índice y la fila. Índice es el ID y fila es cualquier campos diferente
      id_val = fila[0]
      valores_visibles = fila[1:]
      tag = "par" if índice % 2 == 0 else "impar"
      tablas_de_datos.insert("", "end", iid=str(id_val), values=valores_visibles, tags=(tag,))
      
    datos_en_cache[nombre_de_la_tabla] = datos.copy()
    print(f"{len(datos_actualizados)} registros importados correctamente en {nombre_de_la_tabla}")
    
  except Exception as e:
    print(f"OCURRIÓ UNA EXCEPCIÓN: {str(e)}")
  
def exportar_en_PDF(nombre_de_la_tabla, tablas_de_datos, ventana):
  try:
    if not hasattr(tablas_de_datos, "winfo_exists") or not tablas_de_datos.winfo_exists():
      return
    datos_a_exportar = tablas_de_datos.get_children()
    datos = []
   
    encabezado = tablas_de_datos["columns"]
    
    enc_legible = [alias.get(col, col) for col in encabezado]
    
    datos.append(enc_legible)

    for i in datos_a_exportar:
      valores = tablas_de_datos.item(i, "values")
      datos.append(valores)

    ruta_archivo_pdf = diálogoArchivo.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("Archivo PDF", "*.pdf")],
        initialfile=f"Reporte_{nombre_de_la_tabla}",
        title="Exportar informe en PDF"
      )
    
    if not ruta_archivo_pdf:
      return   
    
    pdf = SimpleDocTemplate(
      ruta_archivo_pdf,
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
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0000ff")),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.8, colors.black),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#a8f3ff")]),
    ]))
    
    titulo = Paragraph(f"<b>Reporte de {nombre_de_la_tabla.capitalize()}</b>", título_con_estilo)
    espacio = Spacer(1, 30)

    pdf.build([titulo, espacio, tabla])
    mostrar_aviso(ventana, "✅ SE HA EXPORTADO COMO PDF EXITOSAMENTE", colores["verde_éxito"], 10)  
  except Exception as e:
      print("OCURRIÓ UN ERROR", f"Error al exportar en PDF: {str(e)}")
  finally:
    pass

def ordenar_datos(nombre_de_la_tabla, tablas_de_datos, campo, orden):
  if not hasattr(tablas_de_datos, "winfo_exists") or not tablas_de_datos.winfo_exists():
    return
  try:
    sql, params = consulta_semántica(consultas, nombre_de_la_tabla, orden, None, campo)
    
    with conectar_base_de_datos() as conexión:
      cursor = conexión.cursor()
      cursor.execute(sql, params)
      resultado = cursor.fetchall()
      columnas = [desc[0] for desc in cursor.description]
      
      if tablas_de_datos.winfo_exists():
        for item in tablas_de_datos.get_children():
          tablas_de_datos.delete(item)
          
      if not resultado:
        return
    
    visibles = alias_a_traducir[nombre_de_la_tabla]

    for index, fila in enumerate(resultado):
      ID = fila[0]
      valores_visibles = tuple(fila[columnas.index(alias)] for alias in visibles.values())
      tag = "par" if index % 2 == 0 else "impar"
      tablas_de_datos.insert("", "end",iid=ID, values=valores_visibles, tags=(tag,))
  
  except error_sql as e:
    print(f"HA OCURRIDO UN ERROR AL ORDENAR LA TABLA: {str(e)}")
    desconectar_base_de_datos(conexión)

def buscar_datos(nombre_de_la_tabla, tablas_de_datos, busqueda, consultas):
  if not hasattr(tablas_de_datos, "winfo_exists") or not tablas_de_datos.winfo_exists():
    return
  
  try:
    conexión = conectar_base_de_datos()
    cursor = conexión.cursor()
    valor_busqueda = busqueda.get().strip()
    sql, params = consulta_semántica(consultas, nombre_de_la_tabla, None, valor_busqueda or "", None)
    cursor.execute(sql, params)
    resultado = cursor.fetchall()
    
    for item in tablas_de_datos.get_children():
      tablas_de_datos.delete(item)
    
    for i, fila in enumerate(resultado):
      id_a_ocultar = fila[0]
      datos_visibles = fila[1:]
      tag = "par" if i % 2 == 0 else "impar"
      tablas_de_datos.insert("", "end", iid=id_a_ocultar, values=datos_visibles, tags=(tag,))

   
  except error_sql as e:
    print(f"HA OCURRIDO UN ERROR AL BUSCAR: {str(e)}")
  finally:
    cursor.close()
    conexión.close()