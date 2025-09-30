from Conexión import conectar_base_de_datos, desconectar_base_de_datos, error_sql
from Fun_adicionales import obtener_datos_de_Formulario, consultar_tabla, conseguir_campo_ID, traducir_IDs, convertir_datos
from Fun_Validación_SGAE import validar_datos
from tkinter import messagebox as mensajeTexto, filedialog as diálogo
from datetime import datetime as fecha_y_hora
import tkinter as tk
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics as métricasPDF
from reportlab.pdfbase.ttfonts import TTFont as fuente_TTFont
métricasPDF.registerFont(fuente_TTFont("Arial", "Arial.ttf"))

#--- FUNCIONES DEL ABM (ALTA, BAJA Y MODIFICACIÓN) ---
def seleccionar_registro(nombre_de_la_tabla,  ListaDatos, listaID, cajasDeTexto):
  selección = ListaDatos.curselection()

  if not selección:
    return

  índice = selección[0]
  id = listaID[índice]
  cursor = None
  conexión = conectar_base_de_datos()
  if conexión:
    try:
      campos_visibles = {
      "alumno": ["Nombre", "FechaDeNacimiento", "IDCarrera"],
      "asistencia":["Estado", "Fecha_Asistencia", "IDAlumno"],
      "carrera": ["Nombre", "Duración"],
      "materia": ["Nombre", "Horario", "IDCarrera"],
      "enseñanza": ["IDMateria", "IDProfesor"],
      "profesor": [ "Nombre"],
      "nota": ["IDAlumno","IDMateria" , "ValorNota", "TipoNota", "fechaEvaluación"]
      }
      
      # Diccionario de claves primarias según la tabla
      PKs = {
        "alumno": "ID_Alumno",
        "asistencia": "ID_Asistencia",
        "carrera": "ID_Carrera",
        "materia": "ID_Materia",
        "enseñanza": ["IDProfesor", "IDMateria"],
        "profesor": "ID_Profesor",
        "nota": ["IDAlumno", "IDMateria"]
      }
      clave = PKs.get(nombre_de_la_tabla)
      if not clave:
          mensajeTexto.showerror("ERROR", "No se pudo determinar la superclave para esta tabla.")
          return
      cursor = conexión.cursor()
      if isinstance(clave, list):
        condiciones = ' AND '.join([f"{campo} = %s" for campo in clave])
        consulta = f"SELECT {', '.join(campos_visibles[nombre_de_la_tabla])} FROM {nombre_de_la_tabla} WHERE {condiciones}"
        cursor.execute(consulta, id)
      else:
        consulta = f"SELECT {', '.join(campos_visibles[nombre_de_la_tabla])} FROM {nombre_de_la_tabla} WHERE {clave} = %s"
        cursor.execute(consulta, (id,))
      
      fila_seleccionada = cursor.fetchone()
      
      if not fila_seleccionada:
        return
      datos_convertidos = []
      for campo, valor in zip(campos_visibles[nombre_de_la_tabla], fila_seleccionada):
          if campo == "IDAlumno":
            cursor.execute("SELECT Nombre FROM alumno WHERE ID_Alumno = %s", (valor,))
            res = cursor.fetchone()
            datos_convertidos.append(res[0] if res else "Desconocido")
          elif campo == "IDMateria":
            cursor.execute("SELECT Nombre FROM materia WHERE ID_Materia = %s", (valor,))
            res = cursor.fetchone()
            datos_convertidos.append(res[0] if res else "Desconocido")
          elif campo == "IDCarrera":
            cursor.execute("SELECT Nombre FROM carrera WHERE ID_Carrera = %s", (valor,))
            res = cursor.fetchone()
            datos_convertidos.append(res[0] if res else "Desconocido")
          elif campo == "IDProfesor":
            cursor.execute("SELECT Nombre FROM profesor WHERE ID_Profesor = %s", (valor,))
            res = cursor.fetchone()
            datos_convertidos.append(res[0] if res else "Desconocido")
          else:
            datos_convertidos.append(valor)
            
      cajas = cajasDeTexto[nombre_de_la_tabla]
      
      for caja, valor in zip(cajas, datos_convertidos):
          caja.delete(0, tk.END)
          caja.insert(0, str(valor))
      
      convertir_datos(campos_visibles[nombre_de_la_tabla], cajas)
      
    except error_sql as error:
        mensajeTexto.showerror("ERROR", f"ERROR INESPERADO AL SELECCIONAR: {str(error)}")
    finally:
      if cursor:
        cursor.close()
      desconectar_base_de_datos(conexión)

def insertar_datos(nombre_de_la_tabla, cajasDeTexto, campos_db, Lista_de_datos, listaID):
  conexión = conectar_base_de_datos()
  datos = obtener_datos_de_Formulario(nombre_de_la_tabla, cajasDeTexto, campos_db, validarDatos=True)

  if not datos or not validar_datos(nombre_de_la_tabla, datos):
      return
    
  datos_traducidos = traducir_IDs(nombre_de_la_tabla, datos)
    
  valores_sql = []
  campos_sql = []
  for campo, valor in datos_traducidos.items():
    valores_sql.append(valor)
    campos_sql.append(campo)
    
  if nombre_de_la_tabla.lower() == "nota":
    id_alumno = datos.get("IDAlumno")
    id_materia = datos.get("IDMateria")
    
    campos = ', '.join(list(datos_traducidos.keys()) + ["IDAlumno", "IDMateria"])
    valores = ', '.join(['%s'] * (len(datos_traducidos) + 2))
    consulta = f"INSERT INTO {nombre_de_la_tabla} ({campos}) VALUES ({valores})"
    valores_sql.extend([id_alumno, id_materia])
  else:
    campos = ', '.join(datos_traducidos.keys())
    valores = ', '.join(['%s'] * len(datos_traducidos))
    consulta = f"INSERT INTO {nombre_de_la_tabla} ({campos}) VALUES ({valores})"
    valores_sql = list(datos_traducidos.values())
  try:
    cursor = conexión.cursor()
    cursor.execute(consulta, tuple(valores_sql))
    conexión.commit()
    consultar_tabla(nombre_de_la_tabla, Lista_de_datos, listaID)
    mensajeTexto.showinfo("CORRECTO", "SE AGREGÓ LOS DATOS NECESARIOS")
    for i, (campo, valor) in enumerate(datos_traducidos.items()):
      entry = cajasDeTexto[nombre_de_la_tabla][i]
      entry.delete(0, tk.END)
  except Exception as e:
      mensajeTexto.showerror("ERROR", f"ERROR INESPERADO AL INSERTAR: {str(e)}")
  finally:
      desconectar_base_de_datos(conexión)

def modificar_datos(nombre_de_la_tabla, cajasDeTexto, campos_db, Lista_de_datos, listaID):
    columna_seleccionada = Lista_de_datos.curselection()
    if not columna_seleccionada:
      mensajeTexto.showwarning("ADVERTENCIA", "FALTA SELECCIONAR UNA FILA")
      return

    selección = columna_seleccionada[0]
    ID_Seleccionado = listaID[selección]

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

          consultar_tabla(nombre_de_la_tabla, Lista_de_datos, listaID)
          mensajeTexto.showinfo("CORRECTO", "✅ SE MODIFICÓ EXITOSAMENTE")

    except Exception as e:
      mensajeTexto.showerror("ERROR", f"❌ ERROR AL MODIFICAR: {e}")

def eliminar_datos(nombre_de_la_tabla, cajasDeTexto, campos_db, Lista_de_datos, listaID):
    columna_seleccionada = Lista_de_datos.curselection()
    
    if not columna_seleccionada:
        mensajeTexto.showwarning("ADVERTENCIA", "⚠️ NO SELECCIONASTE NINGUNA FILA")
        return
      
    try:
        with conectar_base_de_datos() as conexión:
            cursor = conexión.cursor()
            
            # Recorrer las selecciones y eliminarlas una por una
            for index in columna_seleccionada:
                ID_Seleccionado = listaID[index]
                
                if nombre_de_la_tabla.lower() == "nota":
                  # Lógica para la tabla "nota" con clave compuesta (IDAlumno, IDMateria)
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
            consultar_tabla(nombre_de_la_tabla, Lista_de_datos, listaID)
            mensajeTexto.showinfo("ÉXITO", "✅ ¡Se eliminaron los datos correctamente!")

    except Exception as e:
        mensajeTexto.showerror("ERROR", f"❌ ERROR INESPERADO AL ELIMINAR: {str(e)}")

def ordenar_datos(nombre_de_la_tabla, tabla, Lista_de_datos, campo=None, ascendencia=True):
  conexión = conectar_base_de_datos()
  cursor = conexión.cursor()
  if conexión is None:
    mensajeTexto.showerror("ERROR DE CONEXIÓN", "NO SE PUDO CONECTAR A LA BASE DE DATOS")
    return

  Lista_de_datos.delete(0, tk.END)

  #Controla que se obtenga nombre reales de las columnas
  cursor.execute(f"SHOW COLUMNS FROM {nombre_de_la_tabla}")
  columna = [col[0] for col in cursor.fetchall()]
  
  if campo is None:
    nombre_columna = ', '.join(columna)
    campo = tk.simpledialog.askstring("Ordenar", f"¿Qué campo querés ordenar los datos de {nombre_de_la_tabla}?\nCampos válidos: {nombre_columna}")
    if not campo:
      return
    campo = campo.strip()
  
  coincidencia = [col for col in columna if col.lower() == campo.lower()]
  
  if not coincidencia:
    mensajeTexto.showerror("ERROR", f"No existe el campo {campo} en la tabla {nombre_de_la_tabla}")
    return
  campo_real = coincidencia[0]
  orden = "ASC" if ascendencia else "DESC"
  try:
    consulta = {
      "alumno":  f"""SELECT a.ID_Alumno, a.Nombre, DATE_FORMAT(a.FechaDeNacimiento, '%d/%m/%Y')
                    FROM alumno AS a
                    JOIN carrera AS c ON a.IDCarrera = c.ID_Carrera
                    ORDER BY {campo_real} {orden}""",
                
      "asistencia": f"""SELECT asis.ID_Asistencia, asis.Estado, DATE_FORMAT(asis.Fecha_Asistencia, '%d/%m/%Y'), al.Nombre
                                  FROM asistencia AS asis
                                  JOIN alumno AS al ON asis.IDAlumno = al.ID_Alumno;"""
    }
    cursor.execute(consulta[nombre_de_la_tabla].lower())
    resultado = cursor.fetchall()
    
    #Controlo que haya resultados, en caso contrario, me imprime un mensaje de que no hay resultados para criterios específicos
    if not resultado:
      mensajeTexto.showinfo("SIN RESULTADOS", "NO SE ENCONTRARON REGISTROS PARA LOS CRITERIOS ESPECÍFICOS")
      return
    
    #Esta lógica ya pertenece al formato de filas, para que quede bien derechito con el fin de evitar cualquier mezcla o confusión al usuario.
    
    filaVisible = resultado[0][1:] if nombre_de_la_tabla != "nota" else resultado[0]
    
    ancho_de_tablas = [0] * len(filaVisible)
    

    for fila in resultado:
      filaVisible = list(fila[1:] if nombre_de_la_tabla != "nota" else fila)
      
      for i, valor in enumerate(filaVisible):
        valorTipoCadena = str(valor)
        ancho_de_tablas[i] = max(ancho_de_tablas[i], len(valorTipoCadena))
      
      
      formato = "|".join("{:<" + str(ancho) + "}" for ancho in ancho_de_tablas)
      
    #Recorro las filas.
    for fila in resultado:
      filaVisible = list(fila[1:] if nombre_de_la_tabla != "nota" else fila)
    
      match nombre_de_la_tabla.lower():
        case "materia":
          filaVisible[1] = f"{filaVisible[1]} horas"
      filaTipoCadena = [str(valor) for valor in filaVisible]
      #Se agrega una separación para que no se vea pegado
      if len(filaTipoCadena) == len(ancho_de_tablas):
        filas_formateadas = formato.format(*filaTipoCadena)
        Lista_de_datos.insert(tk.END, filas_formateadas)
      else:
        print("❗ Columnas desalineadas:", filaTipoCadena)
        print("🔍 Longitudes -> fila:", len(filaTipoCadena), "| ancho_de_tablas:", len(ancho_de_tablas))
    
  except error_sql as e:
     mensajeTexto.showerror("ERROR", f"HA OCURRIDO UN ERROR AL ORDENAR LA TABLA: {str(e)}")
  finally:
    desconectar_base_de_datos(conexión)

def exportar_en_PDF(nombre_de_la_tabla, Lista_de_datos):
  try:
      # Paso 1: Obtener los datos directamente del Listbox
      # Esta es la fuente principal de datos para este PDF, no la DB en este caso.
      datos_a_exportar = Lista_de_datos.get(0, tk.END)
      
      if not datos_a_exportar:
          mensajeTexto.showwarning("ADVERTENCIA", "No hay datos para exportar en el Listbox.")
          return

      # Paso 2: Abrir el diálogo para seleccionar la ruta y nombre del archivo PDF
      ruta_archivo_pdf = diálogo.asksaveasfilename(
          defaultextension=".pdf",
          filetypes=[("Archivo PDF", "*.pdf")],
          initialfile=f"Reporte_{nombre_de_la_tabla}_{fecha_y_hora.now().strftime('%Y%m%d_%H%M%S')}", # Nombre de archivo más descriptivo
          title="Exportar informe en PDF"
      )
      
      # Si el usuario presiona "Cancelar" en el diálogo de guardar
      if not ruta_archivo_pdf:
          return # Salir de la función si no se seleccionó un archivo

      # Paso 3: Crear el objeto Canvas de ReportLab y dibujar el contenido
      # Se debe instanciar canvas.Canvas solo una vez.
      pdf_canvas = canvas.Canvas(ruta_archivo_pdf, pagesize=letter)
      
      # Establecer la fuente. "Helvetica" es una fuente estándar garantizada en ReportLab.
      # "Arial" no está incluida por defecto y necesita ser registrada si es obligatoria.
      pdf_canvas.setFont("Arial", 12) # Tamaño de fuente más legible para el cuerpo

      # Coordenadas de inicio para el contenido
      margen_x = 50 # Margen desde la izquierda
      y_inicio = letter[1] - 50 # Margen desde arriba (altura de la página - margen superior)
      line_height = 15 # Espacio entre líneas
      
      # Añadir un título al PDF
      pdf_canvas.setFont("Arial", 16)
      pdf_canvas.drawString(margen_x, y_inicio + 10, f"Informe: {nombre_de_la_tabla.capitalize()}")
      pdf_canvas.setFont("Arial", 12)

      y = y_inicio

      # Iterar sobre los datos y dibujarlos en el PDF
      for i, fila in enumerate(datos_a_exportar):
          if y < margen_x: # Si nos quedamos sin espacio en la página, crear una nueva página
              pdf_canvas.showPage() # Inicia una nueva página
              pdf_canvas.setFont("Arial", 12)
              y = y_inicio
              pdf_canvas.drawString(margen_x, y, f"Informe de Tabla: {nombre_de_la_tabla.capitalize()} (Continuación)")
              y -= line_height

          pdf_canvas.drawString(margen_x, y, f"{fila}") # Añade un número de línea
          y -= line_height

      # Paso 4: Guardar el archivo PDF
      pdf_canvas.save()
      
      print("ÉXITO", f"El informe de '{nombre_de_la_tabla}' ha sido exportado correctamente a:\n{ruta_archivo_pdf}")
      
  except Exception as e: # Captura cualquier tipo de excepción general para depuración
      print("OCURRIÓ UN ERROR", f"Error al exportar en PDF: {str(e)}")
  finally:
    pass