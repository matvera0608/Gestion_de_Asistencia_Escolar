from Conexión import *
from .Fun_adicionales import *
from .Fun_Validación_SGAE import *
import tkinter as tk
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
import json
#-------------------------------------#

def insertar_datos(nombre_de_la_tabla, cajasDeTexto, campos_db, tablas_de_datos, ventana):
  if not hasattr(tablas_de_datos, "winfo_exists") or not tablas_de_datos.winfo_exists():
    return

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

  datos_traducidos = traducir_IDs(nombre_de_la_tabla, datos)
  
  print(datos_traducidos)
  
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
      
    for i, (campo, valor) in enumerate(datos_traducidos.items()):
      entry = cajasDeTexto[nombre_de_la_tabla][i]
      entry.delete(0, tk.END)
    mostrar_aviso(ventana, "✅ SE AGREGÓ LOS DATOS NECESARIOS", colores["verde_éxito"], 10)
  except Exception as e:
    mensajeTexto.showerror("ERROR", f"ERROR INESPERADO AL INSERTAR: {str(e)}")
  finally:
    desconectar_base_de_datos(conexión)

def modificar_datos(nombre_de_la_tabla, cajasDeTexto, campos_db, tablas_de_datos, ventana):
  selección = obtener_selección(tablas_de_datos)
  if not selección:
    return
  if not hasattr(tablas_de_datos, "winfo_exists") or not tablas_de_datos.winfo_exists():
    return
  
  columna_seleccionada = tablas_de_datos.selection()
  if not columna_seleccionada:
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
  
  datos_traducidos = traducir_IDs(nombre_de_la_tabla, datos)
  
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
          
      for caja in cajasDeTexto[nombre_de_la_tabla]:
        caja.delete(0, tk.END)
      mostrar_aviso(ventana, "✅ SE MODIFICÓ EXITOSAMENTE LOS DATOS", colores["verde_éxito"], 10)
  except Exception as e:
    mensajeTexto.showerror("ERROR", f"❌ ERROR AL MODIFICAR: {e}")

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
    mensajeTexto.showerror("ERROR", f"❌ ERROR INESPERADO AL ELIMINAR: {str(e)}")

datos_en_cache = {}

def guardar_datos(nombre_de_la_tabla, caja, tablas_de_datos, campos_db, ventana):
  global datos_en_cache
  if not hasattr(tablas_de_datos, "winfo_exists") or not tablas_de_datos.winfo_exists():
    return
  try:
    selecciónDatos = tablas_de_datos.selection()
    if not selecciónDatos:
      print("FALTA SELECCIONAR 1 FILA")
      return False
    
    ítem = selecciónDatos[0]
    if not all(entry.get().strip() for entry in caja[nombre_de_la_tabla]):
      mensajeTexto.showinfo("ATENCIÓN", "HAY QUE COMPLETAR TODOS LOS CAMPOS")
      return False
    
    datos = obtener_datos_de_Formulario(nombre_de_la_tabla, caja, campos_db)
    
    if not datos:
      print("NO HAY DATOS QUE GUARDAR")
      return False
    
    datos = convertir_datos(campos_db, caja[nombre_de_la_tabla])
    
    valores = list(datos.values())
    tablas_de_datos.item(ítem, values=valores)
    
    
    if nombre_de_la_tabla not in datos_en_cache:
      datos_en_cache[nombre_de_la_tabla] = []
      
    for entry in caja[nombre_de_la_tabla]:
      entry.delete(0, tk.END)
    mostrar_aviso(ventana, "✅ SE HA GUARDADO EXITOSAMENTE EN UN ARCHIVO", colores["verde_éxito"], 10)

    datos_en_cache[nombre_de_la_tabla].append(datos)
    

    with open("datos_cache.json", "w", encoding="utf-8") as f:
      json.dump(datos_en_cache, f, ensure_ascii=False, indent=2)
    return True
  
  except Exception as e:
    print(f"HA OCURRIDO UN ERROR AL GUARDAR LOS DATOS: {str(e)}")
    return False

def importar_datos(nombre_de_la_tabla, tablas_de_datos):
  global datos_en_cache
  try:
    if not hasattr(tablas_de_datos, "winfo_exists") or not tablas_de_datos.winfo_exists():
      print("La tabla visual no existe o fue cerrada.")
      return
  
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
        
    for item in tablas_de_datos.get_children():
      tablas_de_datos.delete(item)
        
    for índice, fila in datos.iterrows():
      tablas_de_datos.insert("", "end", values=tuple(fila))
    
    alias_invertido = {v: k for k, v in alias.items()}
    datos = datos.rename(columns=alias_invertido)
    
    datos_en_cache[nombre_de_la_tabla] = datos.copy()
    
    print(f"{len(datos)} registros importados correctamente en {nombre_de_la_tabla}")
    
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
    
    # ancho_col = [max(len(str(fila[i])) for fila in datos) * 5 for i in range(len(enc_legible))]
    
    pdf = SimpleDocTemplate(
      ruta_archivo_pdf,
      pagesize=A4,
      rightMargin=40, leftMargin=40,
      topMargin=20, bottomMargin=40
    )
    
    # pdfmetrics.registerFont(TTFont("Arial", "Arial.ttf"))
    # pdfmetrics.registerFont(TTFont("Arial-Bold", "Arialbd.ttf"))
    # pdfmetrics.registerFont(TTFont("Arial-Italic", "Ariali.ttf"))
    # pdfmetrics.registerFont(TTFont("Arial-BoldItalic", "Arialbi.ttf"))
    
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