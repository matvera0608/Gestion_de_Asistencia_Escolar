from Conexión import conectar_base_de_datos, desconectar_base_de_datos, error_sql
from Fun_adicionales import obtener_datos_de_Formulario, consultar_tabla, conseguir_campo_ID, traducir_IDs, convertir_datos, obtener_selección
from Fun_Validación_SGAE import validar_datos
from tkinter import messagebox as mensajeTexto, filedialog as diálogo, ttk
import tkinter as tk
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

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
        # ignorar los que no son combos
        if not nombre_combo.startswith("cbbox"):
            continue
        # limpiar prefijo
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
            break
      
  except error_sql as sql_error:
    mensajeTexto.showerror("ERROR", f"HA OCURRIDO UN ERROR AL CARGAR DATOS EN COMBOBOX: {str(sql_error)}")
    return

def mostrar(tablas_de_datos, muestra):
  if not hasattr(tablas_de_datos, "winfo_exists") or not tablas_de_datos.winfo_exists():
    return
  
  for item in tablas_de_datos:
    tablas_de_datos.delete(item)
  
  registros = muestra()
  
  for fila in registros:
    tablas_de_datos.insert("", "end", values=fila) 

def filtrar(tablas_de_datos, filtro, criterio):
  #En esta función voy a filtrar todos los datos de la treeview.
  if not hasattr(tablas_de_datos, "winfo_exists") or not tablas_de_datos.winfo_exists():
    return
  
  registros = filtro(criterio)
  
  for item in tablas_de_datos.get_children():
      tablas_de_datos.delete(item)

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
        "asistencia": "ID_Asistencia",
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

    for index, fila in enumerate(datos):
        tag = "par" if index % 2 == 0 else "impar"
        tablas_de_datos.insert("", "end", values=fila, tags=(tag,))
    mensajeTexto.showinfo("CORRECTO", "SE AGREGÓ LOS DATOS NECESARIOS")
    # Limpiar las cajas de texto después de insertar
    for i, (campo, valor) in enumerate(datos_traducidos.items()):
      entry = cajasDeTexto[nombre_de_la_tabla][i]
      entry.delete(0, tk.END)
    # Si usas Treeview, no necesitas modificar aquí, porque consultar_tabla debe actualizar el Treeview.
    # Si antes usabas Listbox y ahora Treeview, asegúrate que consultar_tabla inserte los datos en el Treeview.
    # No necesitas modificar esta función para Treeview, solo la función de refresco de la tabla.
  except Exception as e:
    mensajeTexto.showerror("ERROR", f"ERROR INESPERADO AL INSERTAR: {str(e)}")
  finally:
    desconectar_base_de_datos(conexión)

def modificar_datos(nombre_de_la_tabla, cajasDeTexto, campos_db, tablas_de_datos, listaID):
  selección = obtener_selección(tablas_de_datos)
  if not selección:
    return
  if not hasattr(tablas_de_datos, "winfo_exists") or not tablas_de_datos.winfo_exists():
    return
  columna_seleccionada = tablas_de_datos.selection()
  if not columna_seleccionada:
    mensajeTexto.showwarning("ADVERTENCIA", "FALTA SELECCIONAR UNA FILA")
    return

  selección = columna_seleccionada[0]
  índice = tablas_de_datos.index(selección)
  ID_Seleccionado = listaID[índice]

  datos = obtener_datos_de_Formulario(nombre_de_la_tabla, cajasDeTexto, campos_db, validarDatos=True)
  if not datos:
    return
  
  if not validar_datos(nombre_de_la_tabla, datos):
    return
  
  datos_traducidos = traducir_IDs(nombre_de_la_tabla, datos)
  
  if not datos_traducidos:
    return
  
  valores_sql = []
  campos_sql = []
  
  for campo, valor in datos_traducidos.items():
    valores_sql.append(valor)
    campos_sql.append(f"{campo} = %s")
    
  try:
    with conectar_base_de_datos() as conexión:
        cursor = conexión.cursor()
        set_sql = ', '.join(campos_sql)

        if nombre_de_la_tabla.lower() == "nota":
          id_alumno, id_materia = ID_Seleccionado
          consulta = f"UPDATE {nombre_de_la_tabla} SET {set_sql} WHERE IDAlumno = %s AND IDMateria = %s"
          valores_sql.extend([id_alumno, id_materia])
        else:
          CampoID = conseguir_campo_ID(nombre_de_la_tabla)
          consulta = f"UPDATE {nombre_de_la_tabla} SET {set_sql} WHERE {CampoID} = %s"
          valores_sql.append(ID_Seleccionado)
          
        cursor.execute(consulta, tuple(valores_sql))
        conexión.commit()
      
        datos, lista_actualizada = consultar_tabla(nombre_de_la_tabla, listaID)

        for item in tablas_de_datos.get_children():
            tablas_de_datos.delete(item)

        for index, fila in enumerate(datos):
            tag = "par" if index % 2 == 0 else "impar"
            tablas_de_datos.insert("", "end", values=fila, tags=(tag,))
            
        for caja in cajasDeTexto[nombre_de_la_tabla]:
          caja.delete(0, tk.END)
        
        listaID[:] = lista_actualizada
        mensajeTexto.showinfo("CORRECTO", "✅ SE MODIFICÓ EXITOSAMENTE")
  except Exception as e:
    mensajeTexto.showerror("ERROR", f"❌ ERROR AL MODIFICAR: {e}")

def eliminar_datos(nombre_de_la_tabla, cajasDeTexto, campos_db, tablas_de_datos, listaID):
  if not hasattr(tablas_de_datos, "winfo_exists") or not tablas_de_datos.winfo_exists():
    return
  columna_seleccionada = tablas_de_datos.selection()
  
  if not columna_seleccionada:
      mensajeTexto.showwarning("ADVERTENCIA", "⚠️ NO SELECCIONASTE NINGUNA FILA")
      return
  try:
      with conectar_base_de_datos() as conexión:
          cursor = conexión.cursor()
          # Recorrer las selecciones y eliminarlas una por una
          for selección in columna_seleccionada:
            índice = tablas_de_datos.index(selección)
            ID_Seleccionado = listaID[índice]
            if nombre_de_la_tabla.lower() == "nota":
              query = f"DELETE FROM {nombre_de_la_tabla} WHERE IDAlumno = %s AND IDMateria = %s"
              if not isinstance(ID_Seleccionado, tuple):
                  mensajeTexto.showerror("ERROR", "ID de nota no es una tupla válida")
                  return
              cursor.execute(query, ID_Seleccionado)
            else:
              # Lógica para otras tablas con clave simple
              CampoID = conseguir_campo_ID(nombre_de_la_tabla)
              if not CampoID:
                  mensajeTexto.showerror("ERROR", "No se ha podido determinar el campo ID para esta tabla")
                  return
              query = f"DELETE FROM {nombre_de_la_tabla} WHERE {CampoID} = %s"
              if ID_Seleccionado is not None:
                  cursor.execute(query, (ID_Seleccionado,))
              else:
                  mensajeTexto.showerror("ERROR", "NO SE HA ENCONTRADO EL ID VÁLIDO")
                  return
          conexión.commit()
          datos, lista_actualizada = consultar_tabla(nombre_de_la_tabla, listaID)

          for item in tablas_de_datos.get_children():
              tablas_de_datos.delete(item)

          for index, fila in enumerate(datos):
              tag = "par" if index % 2 == 0 else "impar"
              tablas_de_datos.insert("", "end", values=fila, tags=(tag,))

          listaID[:] = lista_actualizada
          consultar_tabla(nombre_de_la_tabla, listaID)
          for i, (campo, valor) in enumerate(datos.items()):
            entry = cajasDeTexto[nombre_de_la_tabla][i]
            entry.delete(0, tk.END)
          mensajeTexto.showinfo("ÉXITO", "✅ ¡Se eliminaron los datos correctamente!")

  except Exception as e:
      mensajeTexto.showerror("ERROR", f"❌ ERROR INESPERADO AL ELIMINAR: {str(e)}")

def eliminar_completamente(nombre_de_la_tabla, cajasDeTexto, campos_db, tablas_de_datos, listaID):
  if not hasattr(tablas_de_datos, "winfo_exists") or not tablas_de_datos.winfo_exists():
      return
  try:
    with conectar_base_de_datos() as conexión:
        cursor = conexión.cursor()
        query = f"DELETE FROM {nombre_de_la_tabla}"
        cursor.execute(query)
        conexión.commit()
        for item in tablas_de_datos.get_children():
            tablas_de_datos.delete(item)
        consultar_tabla(nombre_de_la_tabla, listaID)
        mensajeTexto.showinfo("ÉXITO", "✅ ¡Se eliminaron todos los datos!")
  except Exception as e:
    mensajeTexto.showerror("ERROR", f"❌ ERROR INESPERADO AL ELIMINAR TODOS: {str(e)}")

def ordenar_datos(nombre_de_la_tabla, tablas_de_datos, campo=None, ascendencia=True):
  if not hasattr(tablas_de_datos, "winfo_exists") or not tablas_de_datos.winfo_exists():
    return
  try:
    with conectar_base_de_datos() as conexión:
      cursor = conexión.cursor()
      #Controla que se obtenga nombre reales de las columnas
      cursor.execute(f"SHOW COLUMNS FROM {nombre_de_la_tabla}")
      columna = [col[0] for col in cursor.fetchall()]
      
      if campo is None:
        nombre_columna = ', '.join(columna)
        campo = tk.simpledialog.askstring("Ordenar", f"¿Qué campo querés ordenar los datos de {nombre_de_la_tabla}?\nCampos válidos: {nombre_columna}")
        if not campo:
          return
        campo = campo.strip()
        
        if campo.lower() == "Nombre":
          orden = tk.simpledialog.asktring("Orden", f"¿Que orden deseas para {campo}? ", "palabras válidas: ASCENDENTE o DESCENDENTE")
          if not orden:
            return
      
      coincidencia = [col for col in columna if col.lower() == campo.lower()]
      
      if not coincidencia:
        mensajeTexto.showerror("ERROR", f"No existe el campo {campo} en la tabla {nombre_de_la_tabla}")
        return
        
      campo_real = coincidencia[0]

      consultas = {
          "alumno":  f"""SELECT a.ID_Alumno, a.Nombre, DATE_FORMAT(a.FechaDeNacimiento, '%d/%m/%Y'), c.Nombre as nom
                        FROM alumno AS a
                        JOIN carrera AS c ON a.IDCarrera = c.ID_Carrera
                        ORDER BY {campo_real} ASC""",
                    
          "asistencia": f"""SELECT asis.ID_Asistencia, asis.Estado, DATE_FORMAT(asis.Fecha_Asistencia, '%d/%m/%Y'), al.Nombre
                            FROM asistencia AS asis
                            JOIN alumno AS al ON asis.IDAlumno = al.ID_Alumno
                            ORDER BY {campo_real} ASC"""
        }
        
      consultaSQL = consultas.get(nombre_de_la_tabla.lower(), f"SELECT * FROM {nombre_de_la_tabla} ORDER BY {campo_real} ASC")
      cursor.execute(consultaSQL)
      resultado = cursor.fetchall()
      
      if tablas_de_datos.winfo_exists():
        for item in tablas_de_datos.get_children():
          tablas_de_datos.delete(item)
      
      #Controlo que haya resultados, en caso contrario, me imprime un mensaje de que no hay resultados para criterios específicos
      if not resultado:
        mensajeTexto.showinfo("SIN RESULTADOS", "NO SE ENCONTRARON REGISTROS PARA LOS CRITERIOS ESPECÍFICOS")
        return
      
      filasAMostrar = []
      listasIDs = []
      
      for fila in resultado:
        if nombre_de_la_tabla == "nota":
          listasIDs.append((fila[0], fila[1]))
          filaVisible = list(fila[2:])
        else:
          listasIDs.append(fila[0])
          filaVisible = list(fila[1:])
        filasAMostrar.append(filaVisible)

      for index, filaVisible in enumerate(filasAMostrar): 
        tag = "par" if index % 2 == 0 else "impar"
        tablas_de_datos.insert("", "end", value=filaVisible, tags=(tag,))
            
  except error_sql as e:
    mensajeTexto.showerror("ERROR", f"HA OCURRIDO UN ERROR AL ORDENAR LA TABLA: {str(e)}")

def buscar_datos(nombre_de_la_tabla, tablas_de_datos, campos_db, campo_busqueda):
  selección = obtener_selección(tablas_de_datos)
  if not selección:
    return
 
  if not hasattr(tablas_de_datos, "winfo_exists") or not tablas_de_datos.winfo_exists():
    return
  try:
    conexión = conectar_base_de_datos()
    cursor = conexión.cursor()
    valor_busqueda = campo_busqueda.get().strip()
    consulta = f"SELECT * FROM {nombre_de_la_tabla} WHERE ({campos_db}) LIKE %s"
    cursor.execute(consulta, (f"%{valor_busqueda}%"), )
    resultado = cursor.fetchall()
    
    for item in tablas_de_datos.get_children():
      tablas_de_datos.delete(item)
      
    for fila in resultado:
      tablas_de_datos.insert("", "end", values=fila)
    cursor.close()
    conexión.close()
  except error_sql as e:
    mensajeTexto.showerror("ERROR", f"HA OCURRIDO UN ERROR AL BUSCAR: {str(e)}")

def exportar_en_PDF(nombre_de_la_tabla, tablas_de_datos):
  if not hasattr(tablas_de_datos, "winfo_exists") or not tablas_de_datos.winfo_exists():
    return
  try:
    datos_a_exportar = tablas_de_datos.get_children()
    datos = []

    encabezado = tablas_de_datos["columns"]
    datos.append(encabezado)

    # Obtener los valores de cada fila de la tabla
    for item in datos_a_exportar:
      valores = tablas_de_datos.item(item, "values")
      datos.append(valores)
    
    ruta_archivo_pdf = diálogo.asksaveasfilename(
      defaultextension=".pdf",
      filetypes=[("Archivo PDF", "*.pdf")],
      initialfile=f"Reporte_{nombre_de_la_tabla}",
      title="Exportar informe en PDF"
    )
    
    if not ruta_archivo_pdf:
      return   

    pdf = SimpleDocTemplate(ruta_archivo_pdf)
    tabla = Table(datos)

    # Estilo de la tabla
    tabla.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
    ('TEXTCOLOR', (0,0), (-1,0), colors.black),
    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), 
    ('FONTSIZE', (0,0), (-1,-1), 12), 
    ('GRID', (0,0), (-1,-1), 1, colors.grey), # ⬅️ Ajustado a (0,0) para bordes completos
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.whitesmoke, colors.lightgrey])
    ]))

    # Paso 4: Guardar el archivo PDF
    pdf.build([tabla])
    
    print(f"✅ ÉXITO: El informe de '{nombre_de_la_tabla}' ha sido exportado correctamente a:\n{ruta_archivo_pdf}")
    
  except Exception as e:
      print("OCURRIÓ UN ERROR", f"Error al exportar en PDF: {str(e)}")
  finally:
    pass