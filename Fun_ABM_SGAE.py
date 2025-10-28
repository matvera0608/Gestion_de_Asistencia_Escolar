from Conexión import conectar_base_de_datos, desconectar_base_de_datos, error_sql
from Fun_adicionales import obtener_datos_de_Formulario, consultar_tabla, conseguir_campo_ID, traducir_IDs, convertir_datos, obtener_selección, consultar_tabla_dinámica
from Fun_Validación_SGAE import validar_datos
import tkinter as tk
from tkinter import messagebox as mensajeTexto, filedialog as diálogoArchivo, simpledialog as diálogo
#IMPORTACIÓN PARA CREAR PDF#
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, SimpleDocTemplate
# from reportlab.pdfbase import pdfmetrics
# from reportlab.pdfbase.ttfonts import TTFont


campos_con_claves = {
  "carrera": ("ID_Carrera","Nombre"),
  "alumno": ("ID_Alumno","Nombre"),
  "profesor": ("ID_Profesor", "Nombre"),
  "materia": ("ID_Materia","Nombre")
  }

campos_foráneos = {"alumno": ("IDCarrera", "carrera"),
                   "asistencia": ("IDAlumno", "alumno"),
                   "materia": ("IDCarrera", "carrera"),
                   "enseñanza": [("IDMateria", "materia"), ("IDProfesor","profesor")], 
                   "nota": [("IDMateria", "materia"), ("IDAlumno", "alumno")]
                   }

#--- FUNCIONES DEL ABM (ALTA, BAJA Y MODIFICACIÓN) ---
def cargar_datos_en_Combobox(tablas_de_datos, combos):
  try:
    with conectar_base_de_datos() as conexión:
      if not conexión:
        return
      cursor = conexión.cursor()
      relación = campos_foráneos.get(tablas_de_datos)
      if not relación:
        return
        
      if not isinstance(combos, (list, tuple)):
        combos = [combos]
      
      if isinstance(relación, tuple):
        relación = [relación]
      
      for comboWid in combos:
        nombre_combo = getattr(comboWid, "widget_interno", "").lower()
        if not nombre_combo.startswith("cbbox"):
          continue
        nombre_combo = nombre_combo.replace("cbbox_", "")
        for campo_foráneo, tabla_ajena in relación:
          if nombre_combo == tabla_ajena:
            id_campo, campoVisible = campos_con_claves[tabla_ajena]
            consulta = f"SELECT {id_campo}, {campoVisible} FROM {tabla_ajena}"
            cursor.execute(consulta)
            registros = cursor.fetchall()
            valores = [fila[1] for fila in registros]
            comboWid["values"] = valores
            comboWid.id_Nombre = {fila[1]: fila[0] for fila in registros}
  except error_sql as sql_error:
    mensajeTexto.showerror("ERROR", f"HA OCURRIDO UN ERROR AL CARGAR DATOS EN COMBOBOX: {str(sql_error)}")
    return

def mostrar_registro(nombre_de_la_tabla, tablas_de_datos, cajasDeTexto):
  if not hasattr(tablas_de_datos, "winfo_exists") or not tablas_de_datos.winfo_exists():
    return

  selección = tablas_de_datos.selection()
  if not selección:
    return
  
  iid = selección[0]
  try:
    idSeleccionado = int(iid)
  except ValueError:
    idSeleccionado = iid
  
  cursor = None
  conexión = conectar_base_de_datos()
  if conexión:
    try:
      cursor = conexión.cursor()
      # Diccionario de claves primarias según la tabla
      PKs = {
        "alumno": "ID_Alumno",
        "asistencia": "ID",
        "carrera": "ID_Carrera",
        "materia": "ID_Materia",
        "profesor": "ID_Profesor",
        "enseñanza": "ID",
        "nota": "ID",
      }
      
      clave = PKs.get(nombre_de_la_tabla)
      if not clave:
        mensajeTexto.showerror("ERROR", "No se pudo determinar la superclave para esta tabla.")
        return
      campos_visibles = {
      "alumno": ["Nombre", "FechaDeNacimiento", "IDCarrera"], #Los que empiezan con ID sin guión bajo son claves ajenas o FKs.
      "asistencia":["Estado", "Fecha_Asistencia", "IDAlumno"],
      "carrera": ["Nombre", "Duración"],
      "materia": ["Nombre", "Horario", "IDCarrera"],
      "enseñanza": ["IDMateria", "IDProfesor"],
      "profesor": ["Nombre"],
      "nota": ["IDAlumno", "IDMateria", "valorNota", "tipoNota", "fecha"]
      }

      columnas = ', '.join(campos_visibles[nombre_de_la_tabla.lower()])
      consulta = f"SELECT {columnas} FROM {nombre_de_la_tabla.lower()} WHERE {clave} = %s"
      cursor.execute(consulta, (idSeleccionado,))
      fila_seleccionada = cursor.fetchone()
      
      if not fila_seleccionada:
        return
      
      datos_convertidos = []

      for campo, valor in zip(campos_visibles[nombre_de_la_tabla.lower()], fila_seleccionada):
        if campo == "IDProfesor":
            cursor.execute("SELECT Nombre FROM profesor WHERE ID_Profesor = %s", (valor,))
            res = cursor.fetchone()
            datos_convertidos.append(res[0] if res else "Desconocido")
        elif campo == "IDMateria":
            cursor.execute("SELECT Nombre FROM materia WHERE ID_Materia = %s", (valor,))
            res = cursor.fetchone()
            datos_convertidos.append(res[0] if res else "Desconocido")
        elif campo == "IDAlumno":
            cursor.execute("SELECT Nombre FROM alumno WHERE ID_Alumno = %s", (valor,))
            res = cursor.fetchone()
            datos_convertidos.append(res[0] if res else "Desconocido")
        elif campo == "IDCarrera":
            cursor.execute("SELECT Nombre FROM carrera WHERE ID_Carrera = %s", (valor,))
            res = cursor.fetchone()
            datos_convertidos.append(res[0] if res else "Desconocido")
        else:
            datos_convertidos.append(valor)
            continue
          
      cajas = cajasDeTexto[nombre_de_la_tabla]
      for campo, valor, caja in zip(campos_visibles[nombre_de_la_tabla], datos_convertidos, cajas):
        caja.config(state="normal")
        caja.set(str(valor))
        caja.config(state="readonly" if getattr(caja, "widget_interno", "").startswith("cbBox_") else "normal")
          
      convertir_datos(campos_visibles[nombre_de_la_tabla], cajas)
      
    except error_sql as error:
      mensajeTexto.showerror("ERROR", f"ERROR INESPERADO AL SELECCIONAR: {str(error)}")
    finally:
      cursor.close()
      desconectar_base_de_datos(conexión)

def insertar_datos(nombre_de_la_tabla, cajasDeTexto, campos_db, tablas_de_datos):
  if not hasattr(tablas_de_datos, "winfo_exists") or not tablas_de_datos.winfo_exists():
    return

  conexión = conectar_base_de_datos()
  datos = obtener_datos_de_Formulario(nombre_de_la_tabla, cajasDeTexto, campos_db, validarDatos=True)

  if not datos or not validar_datos(nombre_de_la_tabla, datos):
    return

  datos_traducidos = traducir_IDs(nombre_de_la_tabla, datos)

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
      valores_visibles = fila[1:]   # quitamos el ID de la tupla que mostramos
      tag = "par" if índice % 2 == 0 else "impar"
      tablas_de_datos.insert("", "end", iid=str(id_val), values=valores_visibles, tags=(tag,))
    print("SE AGREGÓ LOS DATOS NECESARIOS")
    for i, (campo, valor) in enumerate(datos_traducidos.items()):
      entry = cajasDeTexto[nombre_de_la_tabla][i]
      entry.delete(0, tk.END)
  except Exception as e:
    mensajeTexto.showerror("ERROR", f"ERROR INESPERADO AL INSERTAR: {str(e)}")
  finally:
    desconectar_base_de_datos(conexión)

def modificar_datos(nombre_de_la_tabla, cajasDeTexto, campos_db, tablas_de_datos):
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

  datos = obtener_datos_de_Formulario(nombre_de_la_tabla, cajasDeTexto, campos_db, validarDatos=True)
  if not datos:
    return
  
  if not validar_datos(nombre_de_la_tabla, datos):
    return
  
  datos_traducidos = traducir_IDs(nombre_de_la_tabla, datos)
  
  if not datos_traducidos:
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
        valores_visibles = fila[1:]   # quitamos el ID de la tupla que mostramos
        tag = "par" if índice % 2 == 0 else "impar"
        # insertamos con iid = id_val (como string)
        tablas_de_datos.insert("", "end", iid=str(id_val), values=valores_visibles, tags=(tag,))
          
      for caja in cajasDeTexto[nombre_de_la_tabla]:
        caja.delete(0, tk.END)
      print("✅ SE MODIFICÓ EXITOSAMENTE")
  except Exception as e:
    mensajeTexto.showerror("ERROR", f"❌ ERROR AL MODIFICAR: {e}")

def eliminar_datos(nombre_de_la_tabla, cajasDeTexto, tablas_de_datos):
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
      print("✅ ¡Se eliminaron los datos correctamente!")
  except Exception as e:
    mensajeTexto.showerror("ERROR", f"❌ ERROR INESPERADO AL ELIMINAR: {str(e)}")

def guardar_datos(nombre_de_la_tabla, tablas_de_datos, caja, campos_db):
  #Esta función se encargará de sólo grabar los datos editados en la tabla.
  #El objetivo de esta función es evitar tener que usar forms para modificar datos.
  if not hasattr(tablas_de_datos, "winfo_exists") or not tablas_de_datos.winfo_exists():
    return
  try:
    selecciónDatos = tablas_de_datos.selection()
    if not selecciónDatos:
      print("FALTA SELECCIONAR 1 FILA")
      return False
    if not all(entry.get().strip() for entry in caja[nombre_de_la_tabla]):
      mensajeTexto.showinfo("ATENCIÓN", "HAY QUE COMPLETAR TODOS LOS CAMPOS")
      return False
    datos = obtener_datos_de_Formulario(nombre_de_la_tabla, caja, campos_db, True)
    if not datos:
      print("NO HAY DATOS QUE GUARDAR")
      return False

    insertar_datos(nombre_de_la_tabla, caja, datos, tablas_de_datos)
    for entry in caja[nombre_de_la_tabla]:
      entry.delete(0, tk.END)
    mensajeTexto.showinfo("ÉXITO", "GUARDADO EXITOSAMENTE")
    return True
  except Exception as e:
    print(f"HA OCURRIDO UN ERROR AL GUARDAR LOS DATOS: {str(e)}")
    return False

def ordenar_datos(nombre_de_la_tabla, tablas_de_datos, campo, orden):
  if not hasattr(tablas_de_datos, "winfo_exists") or not tablas_de_datos.winfo_exists():
    return
  try:
    with conectar_base_de_datos() as conexión:
      cursor = conexión.cursor()
      #Controla que se obtenga nombre reales de las columnas
      cursor.execute(f"SHOW COLUMNS FROM {nombre_de_la_tabla}")
      columna = [col[0] for col in cursor.fetchall()]
      campo = campo.strip()
        
      coincidencia = [col for col in columna if col.lower() == campo.lower()]
      
      if not coincidencia:
        mensajeTexto.showerror("ERROR", f"No existe el campo {campo} en la tabla {nombre_de_la_tabla}")
        return
        
      campo_real = coincidencia[0]
      orden_sql = "ASC" if orden.upper().startswith("ASC") else "DESC"
      consultas = {
      "alumno": {
          "select": f"""SELECT a.ID_Alumno, a.Nombre, DATE_FORMAT(a.FechaDeNacimiento, '%d/%m/%Y') AS Fecha, c.Nombre AS Carrera 
                        FROM alumno a
                        JOIN carrera c ON a.IDCarrera = c.ID_Carrera""",
          "buscables": ["a.Nombre", "c.Nombre"]},
      "materia": {
          "select": f"""SELECT m.ID_Materia, m.Nombre, TIME_FORMAT(m.Horario,'%H:%i') AS Horario, c.Nombre AS Carrera
                        FROM materia m
                        JOIN carrera c ON m.IDCarrera = c.ID_Carrera""",
          "buscables": ["m.Nombre", "c.Nombre"]},
      "carrera":{
          "select": f"""SELECT c.ID_Carrera, c.Nombre, c.Duración 
                        FROM carrera AS c""",
          "buscables": ["c.Nombre", "c.Duración"]},
      "asistencia":{
          "select": f"""SELECT asis.ID, asis.Estado, DATE_FORMAT(asis.Fecha_Asistencia, '%d/%m/%Y') AS Fecha, al.Nombre AS Alumno
                        FROM asistencia AS asis
                        JOIN alumno AS al ON asis.IDAlumno = al.ID_Alumno""",
          "buscables": ["asis.Estado", "al.Nombre"]},
       "enseñanza":{
          "select": f"""SELECT e.ID, m.Nombre AS Materia, p.Nombre AS Profesor
                        FROM enseñanza AS e
                        JOIN profesor AS p ON e.IDProfesor = p.ID_Profesor
                        JOIN materia AS m ON e.IDMateria = m.ID_Materia""",
          "buscables": ["m.Nombre", "p.Nombre"]},
      "profesor":{
          "select": f"""SELECT pro.ID_Profesor, pro.Nombre
                        FROM profesor AS pro""",
          "buscables": ["pro.Nombre"]},
      "nota": {
          "select": f"""SELECT n.ID, al.Nombre AS Alumno, m.Nombre AS Materia, 
                              REPLACE(CAST(n.valorNota AS CHAR(10)), '.', ',') AS Nota, 
                              n.tipoNota, DATE_FORMAT(n.fecha, '%d/%m/%Y') AS Fecha
                              FROM nota n
                              JOIN alumno AS al ON n.IDAlumno = al.ID_Alumno
                              JOIN materia AS m ON n.IDMateria = m.ID_Materia""",
          "buscables": ["al.Nombre", "m.Nombre", "n.tipoNota"]}
                }
      
      consultaSQL = consultas[nombre_de_la_tabla]["select"] + f" ORDER BY {campo_real} {orden_sql}"
      cursor.execute(consultaSQL)
      resultado = cursor.fetchall()
      
      if tablas_de_datos.winfo_exists():
        for item in tablas_de_datos.get_children():
          tablas_de_datos.delete(item)
          
      if not resultado:
        return

    for index, fila in enumerate(resultado):
      ID = fila[0]
      valores_visibles = fila[1:]
      tag = "par" if index % 2 == 0 else "impar"
      tablas_de_datos.insert("", "end",iid=ID, values=valores_visibles, tags=(tag,))
  
  except error_sql as e:
    print(f"HA OCURRIDO UN ERROR AL ORDENAR LA TABLA: {str(e)}")

def buscar_datos(nombre_de_la_tabla, tablas_de_datos, entry_busqueda, consultas):
  if not hasattr(tablas_de_datos, "winfo_exists") or not tablas_de_datos.winfo_exists():
    return
  
  try:
    conexión = conectar_base_de_datos()
    cursor = conexión.cursor()
    valor_busqueda = entry_busqueda.get().strip()
    sql, params = consultar_tabla_dinámica(consultas, nombre_de_la_tabla, valor_busqueda or "", operador_like="{}%")
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
    if cursor:
      cursor.close()
    if conexión:
      conexión.close()
    
def exportar_en_PDF(nombre_de_la_tabla, tablas_de_datos):
  try:
    if not hasattr(tablas_de_datos, "winfo_exists") or not tablas_de_datos.winfo_exists():
      return
    datos_a_exportar = tablas_de_datos.get_children()
    datos = []
    
    alias = {
      "IDCarrera": "Carrera",
      "IDMateria": "Materia",
      "IDProfesor": "Profesor",
      "IDAlumno": "Alumno",
      "FechaDeNacimiento": "Fecha de nacimiento",
      "valorNota": "Nota",
      "tipoNota": "Evaluación",
      "Fecha_Asistencia": "Fecha",
    }

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
    
    print("EXPORTADO")
      
  except Exception as e:
      print("OCURRIÓ UN ERROR", f"Error al exportar en PDF: {str(e)}")
  finally:
    pass