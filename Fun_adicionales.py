from Conexión import conectar_base_de_datos, desconectar_base_de_datos
# from Fun_Validación_SGAE import validar_datos
from datetime import datetime
from datetime import datetime as hora_del_sistema
from tkinter import messagebox as mensajeTexto
import tkinter as tk

actualizaciónHora = None

def obtener_datos_de_Formulario(nombre_de_la_tabla, validarDatos):
  global cajasDeTexto, datos, campos_de_la_base_de_datos

  campos_de_la_base_de_datos = {
      'alumno':     ["FechaDeNacimiento", "Nombre"],
      'asistencia': ["Estado", "Fecha_Asistencia"],
      'carrera':    ["Nombre", "Duración"],
      'materia':    ["Nombre", "Horario"],
      'profesor':   ["Nombre"],
      'nota':       ["valorNota", "tipoNota"]
  }

  # cajasDeTexto = {
  #     'alumno':  (txBox_FechaNacimiento, txBox_NombreAlumno),
  #     'asistencia': (txBox_EstadoDeAsistencia, txBox_FechaAsistencia),
  #     'carrera':  (txBox_NombreCarrera, txBox_Duración),
  #     'materia': (txBox_NombreMateria, txBox_HorarioCorrespondiente),
  #     'profesor': (txBox_NombreProfesor,),
  #     'nota':     (txBox_Valor, txBox_Tipo)
  # }

  datos = {}

  for campo, caja in zip(campos_de_la_base_de_datos[nombre_de_la_tabla], cajasDeTexto[nombre_de_la_tabla]):
    texto = caja.get().strip()

    try:
      if texto.count("/") == 2:
        texto = datetime.strptime(texto, "%d/%m/%Y").date()
      elif texto.count(":") == 1 and len(texto) <= 5:
        texto = datetime.strptime(texto, "%H:%M").time()
    except ValueError:
      mensajeTexto.showerror("Error", f"Formato inválido en '{campo}': {texto}")
      return None
    datos[campo] = texto
  
  # if validarDatos:
  #   if not validar_datos(nombre_de_la_tabla, datos):
  #     return None

  return datos

#Esta función me permite obtener el ID de cualquier tabla que se encuentre en mi base de datos antes de eliminar
#ya que SQL obliga poner una condición antes de ejecutar una tarea
def conseguir_campo_ID(nombre_de_la_tabla):
  IDs = {
              'alumno': "ID_Alumno",
              'asistencia': "ID_Asistencia",
              'carrera': "ID_Carrera",
              'materia': "ID_Materia",
              'profesor': "ID_Profesor",
              'nota': ["IDAlumno", "IDMateria"]
        }
  return IDs.get(nombre_de_la_tabla.strip().lower())

def convertir_datos(nombre_de_la_tabla):
  for campo, caja in zip(campos_de_la_base_de_datos[nombre_de_la_tabla], cajasDeTexto[nombre_de_la_tabla]):
    valor = caja.get()
    # Si el campo es una fecha, lo convierte al formato "DD/MM/YYYY"
    if isinstance(valor, str) and "fecha" in campo.lower():
        try:
            fecha_obj = datetime.strptime(valor, "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            continue
        valor = fecha_obj
    # Si el campo es una hora, lo convierte al formato "HH:MM"
    elif isinstance(valor, str) and "hora" in campo.lower():
        try:
            hora_obj = datetime.strptime(valor, "%H:%M:%S").strftime("%H:%M")
        except ValueError:
            continue  # Si no es una hora válida, no la convierte
        valor = hora_obj
    caja.delete(0, tk.END)  # Limpia el entry
    caja.insert(0, str(valor))  # Inserta el valor convertido

#Esta función sirve para actualizar la hora
def actualizar_la_hora(interfaz):
  global actualizaciónHora
  label_Hora = tk.Label(interfaz, text=hora_del_sistema.now().strftime("%I:%M:%S"), font=("Arial", 10), fg="blue", bg=interfaz.cget("bg"))
  label_Hora.config(text=hora_del_sistema.now().strftime("%I:%M:%S"))
  label_Hora.grid(row=20, column=0, sticky="ne", padx=0, pady=0)  # Usá una fila alta para que quede abajo
  actualizaciónHora = interfaz.after(1000, actualizar_la_hora, interfaz)
  
# --- FUNCIONES DE LECTURA ---
# Esta función sirve sólo para leer datos de la bases de datos escuela
def consultar_tabla(nombre_de_la_tabla):
  from SGAE_Principal import Lista_de_datos
  global lista_IDs
  try:
      lista_IDs = []
      conexión = conectar_base_de_datos()
      if conexión:
          cursor = conexión.cursor()

          match nombre_de_la_tabla.lower():
              case "alumno":
                  cursor.execute("""SELECT a.ID_Alumno, a.Nombre, DATE_FORMAT(a.FechaDeNacimiento, '%d/%m/%Y'), c.Nombre
                                  FROM alumno AS a
                                  JOIN carrera AS c ON a.IDCarrera = c.ID_Carrera;""")
              case "asistencia":
                  cursor.execute("""SELECT asis.ID_Asistencia, asis.Estado, DATE_FORMAT(asis.Fecha_Asistencia, '%d/%m/%Y'), al.Nombre
                                  FROM asistencia AS asis
                                  JOIN alumno AS al ON asis.IDAlumno = al.ID_Alumno;""")
              case "carrera":
                  cursor.execute("""SELECT c.ID_Carrera, c.Nombre, c.Duración
                                  FROM carrera AS c;""")
              case "materia":
                  cursor.execute("""SELECT m.ID_Materia, m.Nombre, TIME_FORMAT(m.Horario,'%H:%i'), c.Nombre
                                  FROM materia AS m
                                  JOIN carrera AS c ON m.IDCarrera = c.ID_Carrera;""")
              case "enseñanza":
                  cursor.execute("""SELECT e.IDMateria, m.Nombre, p.Nombre FROM enseñanza AS e
                                 JOIN profesor AS p ON e.IDProfesor = p.ID_Profesor
                                 JOIN materia AS m ON e.IDMateria = m.ID_Materia;""")
              case "profesor":
                  cursor.execute("""SELECT pro.ID_Profesor, pro.Nombre FROM profesor AS pro;""")
              case "nota":
                  cursor.execute("""SELECT n.IDAlumno, n.IDMateria, 
                                          REPLACE(CAST(n.valorNota AS CHAR(10)), '.', ',') AS valorNota, 
                                          n.tipoNota, 
                                          al.Nombre AS NombreAlumno, 
                                          m.Nombre AS NombreMateria
                                  FROM nota AS n
                                  JOIN alumno AS al ON n.IDAlumno = al.ID_Alumno
                                  JOIN materia AS m ON n.IDMateria = m.ID_Materia;""")
              case _:
                  cursor.execute(f"SELECT * FROM {nombre_de_la_tabla};")

          resultado = cursor.fetchall()
          Lista_de_datos.delete(0, tk.END)

          if not resultado:
              mensajeTexto.showinfo("Sin datos", "No hay datos disponibles para mostrar.")
              return

          lista_IDs.clear()
          ancho_de_tablas = []

          for fila in resultado:
              if nombre_de_la_tabla.lower() == "nota":
                lista_IDs.append((fila[0], fila[1]))
                filaVisible = fila[2:]
              else:
                lista_IDs.append(fila[0])
                filaVisible = fila[1:]

              while len(ancho_de_tablas) < len(filaVisible):
                ancho_de_tablas.append(0)

              for i, valor in enumerate(filaVisible):
                valorTipoCadena = str(valor)
                ancho_de_tablas[i] = max(ancho_de_tablas[i], len(valorTipoCadena))

          formato = "|".join("{:<" + str(ancho) + "}" for ancho in ancho_de_tablas) # Formato de visualización

          for fila in resultado:
            if nombre_de_la_tabla.lower() == "nota":
              filaVisible = list(fila[2:])
            else:
              filaVisible = list(fila[1:])

            filaTipoCadena = [str(valor) for valor in filaVisible]
            if len(filaTipoCadena) == len(ancho_de_tablas):
              filas_formateadas = formato.format(*filaTipoCadena)
              Lista_de_datos.insert(tk.END, filas_formateadas)

      desconectar_base_de_datos(conexión)

  except Exception as Exc:
    mensajeTexto.showerror("ERROR", f"Algo no está correcto o no tiene nada de datos: {Exc}")
    
