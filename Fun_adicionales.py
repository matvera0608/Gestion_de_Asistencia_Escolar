from Conexión import conectar_base_de_datos, desconectar_base_de_datos
from Fun_Validación_SGAE import validar_datos
from datetime import datetime as fecha_y_hora
from tkinter import messagebox as mensajeTexto
import tkinter as tk

def obtener_selección(treeview):
    try:
      return treeview.selection()
    except tk.TclError:
      mensajeTexto.showerror("ERROR", "La tabla ya no está disponible.")
      return None


def obtener_datos_de_Formulario(nombre_de_la_tabla, cajasDeTexto, campos_de_la_base_de_datos, validarDatos=True):
  global datos, campos_db, lista_de_cajas
  campos_db = campos_de_la_base_de_datos[nombre_de_la_tabla]
  lista_de_cajas = cajasDeTexto[nombre_de_la_tabla]
  
  convertir_datos(campos_db, lista_de_cajas)
  
  if nombre_de_la_tabla not in cajasDeTexto or nombre_de_la_tabla not in campos_de_la_base_de_datos:
    mensajeTexto.showerror("Error", f"Configuración no encontrada para la tabla: {nombre_de_la_tabla}")
    return None
  
  datos = {}

  for campo, caja in zip(campos_db, lista_de_cajas):
    texto = caja.get().strip()
    try:
      if texto.count("/") == 2:
        texto = fecha_y_hora.strptime(texto, "%d/%m/%Y").date()
      elif texto.count(":") == 1 and len(texto) <= 5:
        texto = fecha_y_hora.strptime(texto, "%H:%M").time()
    except ValueError:
      mensajeTexto.showerror("Error", f"Formato inválido en '{campo}': {texto}")
      return None
    datos[campo] = texto
  
  if validarDatos:
    if not validar_datos(nombre_de_la_tabla, datos):
      return None
  return datos

#Esta función me permite obtener el ID de cualquier tabla que se encuentre en mi base de datos antes de eliminar
#ya que SQL obliga poner una condición antes de ejecutar una tarea
def conseguir_campo_ID(nombre_de_la_tabla):
  IDs_mapeados = {
              'alumno': "ID_Alumno",
              'asistencia': "ID_Asistencia",
              'carrera': "ID_Carrera",
              'materia': "ID_Materia",
              'enseñanza': "ID",
              'profesor': "ID_Profesor",
              'nota': "ID"
        }
  return IDs_mapeados.get(nombre_de_la_tabla.strip().lower())

def convertir_datos(campos_db, lista_de_cajas):
  for campo, caja in zip(campos_db, lista_de_cajas):
    valor = caja.get()
    
    if isinstance(valor, str) and "fecha" in campo.lower():
        try:
            fecha_obj = fecha_y_hora.strptime(valor, "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            continue
        valor = fecha_obj
    elif isinstance(valor, str) and "hora" in campo.lower():
        try:
            hora_obj = fecha_y_hora.strptime(valor, "%H:%M:%S").strftime("%H:%M")
        except ValueError:
            continue
        valor = hora_obj
    caja.delete(0, tk.END)  # Limpia el entry
    caja.insert(0, str(valor))  # Inserta el valor convertido

#En esta función se crea un label que muestra la hora actual y se actualiza cada segundo
#pero si el label ya existe, sólo se actualiza su texto.
# # def actualizar_la_hora(contenedor):
# #   color_padre = contenedor.cget('bg')
# #   if hasattr(contenedor, 'label_Hora'):
# #     contenedor.label_Hora.config(text=fecha_y_hora.now().strftime("%H:%M:%S"))
# #   else:
# #     contenedor.label_Hora = tk.Label(contenedor, font=("Arial", 10, "bold"), bg=color_padre, fg="blue")
# #     contenedor.label_Hora.grid(row=20, column=0, sticky="ne", padx=0, pady=0)
# #     contenedor.label_Hora.config(text=fecha_y_hora.now().strftime("%H:%M:%S"))
# #   contenedor.after(1000, lambda: actualizar_la_hora(contenedor))

# def actualizar_la_hora(contenedor):
#   color_padre = contenedor.cget('bg')
  
#   label_Hora = tk.Label(contenedor, font=("Arial", 10, "bold"), bg=color_padre, fg="blue")
#   label_Hora.grid(row=20, column=0, sticky="ne", padx=0, pady=0)
#   label_Hora.config(text=fecha_y_hora.now().strftime("%H:%M:%S"))
#   actualizar_la_hora(contenedor)

# --- Fun_adicionales.py ---


# def iniciar_reloj(etiqueta):
#     hora_actual = time.strftime("%H:%M:%S")
#     etiqueta.config(text=hora_actual)
#     etiqueta.after(1000, iniciar_reloj, etiqueta)

# def actualizar_la_hora(contenedor):
#     reloj = tk.Label(contenedor, font=("Courier New", 12, "bold"))
#     reloj.grid(row=20, column=0, sticky="ne", padx=0, pady=0)
#     iniciar_reloj(reloj)
#     return reloj


# --- FUNCIONES DE LECTURA ---

# def cargar_datos(tabla_Treeview, tabla):
#   conexión = conectar_base_de_datos()
#   if not conexión:
#     return
  
#   for item in tabla_Treeview.get_children():
#     tabla_Treeview.delete(item)

#   cursor = conexión.cursor()
#   # Limpiar datos existentes en el Treeview
  
#   cursor.execute(f"SELECT * FROM {tabla}")
#   filas = cursor.fetchall()
  
#   for i, fila in enumerate(filas):
#     tag = "evenrow" if i % 2 == 0 else "oddrow"
#     tabla_Treeview.insert("", "end", values=fila, tags=(tag,))
#   print(filas)
#   desconectar_base_de_datos(conexión)

# Esta función sirve sólo para leer datos de la bases de datos escuela

def construir_query(nombre_de_la_tabla, filtros):
  consulta_base = ""
  filtro = ""

  if filtros:
      condiciones = [f'{campo} = %s' for campo in filtros.keys()]
      filtro = " WHERE " + " AND ".join(condiciones)

  match nombre_de_la_tabla.lower():
      case "alumno":
          consulta_base = """SELECT a.ID_Alumno, a.Nombre, DATE_FORMAT(a.FechaDeNacimiento, '%d/%m/%Y') AS FechaNacimiento, c.Nombre AS Carrera
                              FROM alumno AS a
                              LEFT JOIN carrera AS c ON a.IDCarrera = c.ID_Carrera
                              ORDER BY a.Nombre;
                          """
      case "asistencia":
          consulta_base = """SELECT asis.ID_Asistencia, asis.Estado, DATE_FORMAT(asis.Fecha_Asistencia, '%d/%m/%Y') AS Fecha, al.Nombre AS Alumno
                              FROM asistencia AS asis
                              LEFT JOIN alumno AS al ON asis.IDAlumno = al.ID_Alumno
                              ORDER BY asis.Fecha_Asistencia"""
      case "carrera":
          consulta_base = """SELECT c.ID_Carrera, c.Nombre, c.Duración
                              FROM carrera AS c
                              ORDER BY c.Nombre"""
      case "materia":
          consulta_base = """SELECT m.ID_Materia, m.Nombre, TIME_FORMAT(m.Horario,'%H:%i') AS Horario, c.Nombre AS Carrera
                              FROM materia AS m
                              LEFT JOIN carrera AS c ON m.IDCarrera = c.ID_Carrera
                              ORDER BY m.Nombre"""
      case "enseñanza":
          consulta_base = """SELECT e.ID, m.Nombre AS Materia, p.Nombre AS Profesor
                              FROM enseñanza AS e
                              LEFT JOIN profesor AS p ON e.IDProfesor = p.ID_Profesor
                              LEFT JOIN materia AS m ON e.IDMateria = m.ID_Materia
                              ORDER BY m.Nombre, p.Nombre"""
      case "profesor":
          consulta_base = """SELECT pro.ID_Profesor, pro.Nombre
                              FROM profesor AS pro
                              ORDER BY pro.Nombre"""
      case "nota":
          consulta_base = """SELECT n.ID, al.Nombre AS Alumno, m.Nombre AS Materia, 
                              REPLACE(CAST(n.valorNota AS CHAR(10)), '.', ',') AS Nota, 
                              n.tipoNota, DATE_FORMAT(n.fecha, '%d/%m/%Y') AS FechaEv
                              FROM nota AS n
                              LEFT JOIN alumno AS al ON n.IDAlumno = al.ID_Alumno
                              LEFT JOIN materia AS m ON n.IDMateria = m.ID_Materia
                              ORDER BY al.Nombre, m.Nombre"""
      case _:
          consulta_base = f"SELECT * FROM {nombre_de_la_tabla}"

  return consulta_base + filtro

def consultar_tabla(nombre_de_la_tabla):
  try:
    conexión = conectar_base_de_datos()
    if conexión:
      cursor = conexión.cursor()
      query = construir_query(nombre_de_la_tabla, {})
      cursor.execute(query)
      res = cursor.fetchall()
      cursor.close()
      desconectar_base_de_datos(conexión)
      return res
  except Exception as Exc:
    mensajeTexto.showerror("ERROR", f"Algo no está correcto o no tiene nada de datos: {Exc}")

def traducir_IDs(nombre_de_la_tabla, datos):
  campos_a_traducir = {
      "alumno": {"IDCarrera": ("ID_Carrera","carrera", "Nombre")},
      "materia": {"IDCarrera": ("ID_Carrera","carrera", "Nombre")},
      "asistencia": {"IDAlumno": ("ID_Alumno","alumno", "Nombre")},
      "enseñanza": {"IDProfesor": ("ID_Profesor","profesor", "Nombre"), "IDMateria": ("ID_Materia", "materia", "Nombre")},
      "nota": {"IDAlumno": ("ID_Alumno","alumno", "Nombre"), "IDMateria": ("ID_Materia","materia", "Nombre")}
  }
  if not datos:
    return None
  # Crear un nuevo diccionario para almacenar los datos traducidos
  datos_traducidos = datos.copy()
  relación = campos_a_traducir.get(nombre_de_la_tabla.lower())
  if not relación:
    return datos
  try:
      with conectar_base_de_datos() as conexión:
        cursor = conexión.cursor()
        for campo_fkID, (campo_idPK, tabla_ref, campo_ref) in relación.items():
          if campo_fkID in datos:
            nombre_a_buscar = datos[campo_fkID]
            consulta = f"SELECT {campo_idPK} FROM {tabla_ref} WHERE {campo_ref} = %s"
            cursor.execute(consulta, (nombre_a_buscar,))
            resultado = cursor.fetchone()
            
            if resultado:
                datos_traducidos[campo_fkID] = resultado[0]
            else:
                mensajeTexto.showerror("ERROR DE DATOS", f"❌ El '{nombre_a_buscar}' no existe en la base de datos.")
                return None
      return datos_traducidos
      
  except Exception as e:
      mensajeTexto.showerror("ERROR DE CONEXIÓN", f"❌ Error al conectar a la base de datos: {e}")
      return None