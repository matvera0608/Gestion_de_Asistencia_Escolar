from Conexión import *
from PIL import Image, ImageTk
import os
import tkinter as tk
from datetime import datetime as fecha_y_hora
# --- ELEMENTOS ---

dirección_del_ícono = os.path.dirname(__file__)
ícono = os.path.join(dirección_del_ícono, "imágenes","escuela.ico")
ruta_base = os.path.dirname(os.path.abspath(__file__))
ruta_imagen = os.path.join(ruta_base, "imágenes")

nombreActual = None
permitir_inserción = False
ventanaAbierta = {}

colores = {
  "blanco": "#FFFFFF",
  "gris": "#AAAAAA",
  "negro": "#000000",
  "negro_resaltado": "#3A3A3A",
  "celeste_azulado": "#004CFF",
  "celeste": "#3F92FF",
  "celeste_resaltado": "#9AB5FF",
  "azul": "#0000FF",
  "azul_claro": "#C5C5FF",
  "azul_oscuro": "#00004D",
  "rojo_error": "#B90000",
  "verde_éxito": "#00AA00",
  "amarillo_alerta": "#CCAE00"
}

campos_en_db = {
      "alumno": ["Nombre", "FechaDeNacimiento", "IDCarrera"],
      "asistencia": ["Estado", "Fecha_Asistencia", "IDAlumno", "IDProfesor", "IDMateria"],
      "carrera": ["Nombre", "Duración"],
      "materia": ["Nombre", "HorarioEntrada", "HorarioSalida", "IDCarrera"],
      "enseñanza": ["IDMateria", "IDProfesor"],
      "profesor": ["Nombre"],
      "nota": ["IDAlumno", "IDMateria","IDProfesor", "valorNota", "tipoNota", "fechaEvaluación"]
  }


alias = {
"IDCarrera": "Carrera",
"IDMateria": "Materia",
"IDProfesor": "Profesor",
"IDAlumno": "Alumno",
"FechaDeNacimiento": "Fecha de nacimiento",
"fechaEvaluación": "Fecha",
"valorNota": "Nota",
"tipoNota": "Evaluación",
"Fecha_Asistencia": "Fecha",
"HorarioEntrada": "Horario de entrada",
"HorarioSalida": "Horario de salida"
}

campos_comunes = [("Nombre*", "txBox_Nombre")]
  
campos_por_tabla = {
"alumno": campos_comunes + [
    ("Fecha de nacimiento*", "txBox_FechaNacimiento"),
    ("Carrera*", "cbBox_Carrera")
],
"asistencia": [
    ("Estado de asistencia*", "cbBox_EstadoAsistencia"),
    ("Fecha*", "txBox_FechaAsistencia"),
    ("Alumno*", "cbBox_Alumno"),
    ("Profesor*", "cbBox_Profesor"),
    ("Materia*", "cbBox_Materia"),
],
"carrera": campos_comunes + [
    ("Duración*", "txBox_Duración")
],
"materia": campos_comunes + [
    ("Horario de entrada*", "txBox_HorarioEntrada"),
    ("Horario de salida*", "txBox_HorarioSalida"),
    ("Carrera*", "cbBox_Carrera")
],
"enseñanza": [
("Materia*", "cbBox_Materia"),
("Profesor*", "cbBox_Profesor")
],
"profesor": campos_comunes,
"nota": [
    ("Alumno*", "cbBox_Alumno"),
    ("Materia*", "cbBox_Materia"),
    ("Profesor*", "cbBox_Profesor"),
    ("Nota*", "txBox_Valor"),
    ("Evaluación*", "txBox_TipoEvaluación"),
    ("Fecha*", "txBox_Fecha")
    ]
}

cajasDeTexto = {}

consultas = {
      "alumno": {
          "select": """SELECT a.ID_Alumno, a.Nombre AS AlumnoNombre, 
                      DATE_FORMAT(a.FechaDeNacimiento, '%d/%m/%Y') AS Fecha,
                      c.Nombre AS CarreraNombre
                      FROM alumno a
                      JOIN carrera c ON a.IDCarrera = c.ID_Carrera"""
      },
      "asistencia":{
          "select": """SELECT asis.ID, asis.Estado, DATE_FORMAT(asis.Fecha_Asistencia, '%d/%m/%Y') AS Fecha,
                    al.Nombre AS Alumno,
                    p.Nombre AS Profesor,
                    m.Nombre AS Materia
                    FROM asistencia asis
                    JOIN alumno AS al ON asis.IDAlumno = al.ID_Alumno
                    JOIN profesor AS p ON asis.IDProfesor = p.ID_Profesor
                    JOIN materia AS m ON asis.IDMateria = m.ID_Materia"""
          
          },
      "carrera":{
          "select": """SELECT c.ID_Carrera,
                        c.Nombre AS CarreraNombre,
                        c.Duración
                        FROM carrera AS c"""
          },
      "materia": {
          "select": """SELECT m.ID_Materia, m.Nombre as MateriaNombre, 
                    TIME_FORMAT(m.HorarioEntrada,'%H:%i') AS HorarioEntrada, TIME_FORMAT(m.HorarioSalida,'%H:%i') AS HorarioSalida,
                    c.Nombre AS Carrera
                    FROM materia m
                    JOIN carrera c ON m.IDCarrera = c.ID_Carrera"""
      },
      "profesor":{
          "select":"""SELECT pro.ID_Profesor, pro.Nombre
                      FROM profesor AS pro"""
          },
      "nota":{
          "select": """SELECT n.ID, al.Nombre AS AlumnoNom, m.Nombre AS MateriaNom, p.Nombre AS ProfesorNom,
                        REPLACE(CAST(n.valorNota AS CHAR(10)), '.', ',') AS Nota, 
                        n.tipoNota, DATE_FORMAT(n.fechaEvaluación, '%d/%m/%Y') AS FechaEv
                        FROM nota n
                        JOIN alumno AS al ON n.IDAlumno = al.ID_Alumno
                        JOIN materia AS m ON n.IDMateria = m.ID_Materia
                        JOIN profesor AS p ON n.IDProfesor = p.ID_Profesor"""
          },
      "enseñanza":{
          "select": """SELECT e.ID, m.Nombre AS MatNom, p.Nombre AS ProNom
                        FROM enseñanza e
                        JOIN profesor AS p ON e.IDProfesor = p.ID_Profesor
                        JOIN materia AS m ON e.IDMateria = m.ID_Materia"""
          }
    }

alias_a_traducir = {
    "alumno": {
        "Nombre": "AlumnoNombre",
        "FechaDeNacimiento": "Fecha",
        "IDCarrera": "CarreraNombre"
    },
    "materia": {
        "Nombre": "MateriaNombre",
        "HorarioEntrada": "HorarioEntrada",
        "HorarioSalida": "HorarioSalida",
        "IDCarrera": "Carrera"
    },
    "nota": {
        "IDAlumno": "AlumnoNom",
        "IDMateria": "MateriaNom",
        "IDProfesor": "ProfesorNom",
        "Nota": "Nota",
        "Tipo": "tipoNota",
        "FechaEvaluación": "FechaEv"
    },
    "asistencia": {
        "Estado": "Estado",
        "Fecha_Asistencia": "Fecha",
        "IDAlumno": "Alumno",
        "IDProfesor": "Profesor",
        "IDMateria": "Materia"
    },
    "profesor": {
        "Nombre": "Nombre"
    },
    "carrera": {
        "Nombre": "CarreraNombre",
        "Duración": "Duración"
    },
    "enseñanza": {
        "IDMateria": "MatNom", 
        "IDProfesor": "ProNom"
    }
}

alias_a_orden_raw = {
    "asistencia": {
        "IDAlumno": "Alumno",
        "IDProfesor": "Profesor",
        "IDMateria": "Materia"
    },
    "enseñanza":  {
        "Materia":  "m.Nombre",
        "Profesor": "p.Nombre"
    }
}

# --- FUNCIONES DE CARGA Y CONFIGURACIÓN ---
def consulta_semántica(consultas_meta, nombre_de_la_tabla, sentido_del_orden, valorBúsqueda, ordenDatos, operador_like="%{}%"):
    meta = consultas_meta.get(nombre_de_la_tabla.lower())
    if not meta:
        raise ValueError(f"No existe metadata para la tabla '{nombre_de_la_tabla}'")
    select_sql = meta["select"].strip()
    with conectar_base_de_datos() as conexión:
        cursor = conexión.cursor()
        cursor.execute(f" {select_sql} LIMIT 1")
        columnas = [desc[0] for desc in cursor.description]
        sql = f"SELECT * FROM ({select_sql}) AS sub"
        params = ()
        
        if valorBúsqueda:
            condiciones = " OR ".join(f"{col} LIKE %s" for col in columnas)
            sql +=  f" WHERE {condiciones}"
            params = tuple(operador_like.format(valorBúsqueda) for _ in columnas)
            
        if ordenDatos:
            tabla = nombre_de_la_tabla.lower()
            orden = alias_a_orden_raw.get(tabla, {}).get(ordenDatos)
            if not orden:
                orden = alias_a_traducir.get(tabla, {}).get(ordenDatos, ordenDatos)

            if orden in columnas:
                sentido = "ASC" if str(sentido_del_orden).upper().startswith("ASC") else "DESC"
                sql += f" ORDER BY {orden} {sentido}"
    return sql, params


def mostrar_aviso(contenedor, texto, color=None, tamañoAviso=10, milisegundos=5000):
  
  # Asegúrate de que las indentaciones coincidan EXACTAMENTE con este ejemplo:
  for widget in contenedor.winfo_children(): #Esto recorre los widgets y si existe el aviso reemplaza por el nuevo, ayuda a limpiar y consumir menos recursos
    if isinstance(widget, tk.Label) and widget.winfo_name() == "aviso_temporal": 
      if widget.winfo_exists():
        widget.destroy()
      break
    
  if not texto:
    return
  
  color_actual = contenedor.cget("bg")

  aviso = tk.Label(contenedor, text=texto, fg=color, font=("Arial", tamañoAviso, "bold"), name="aviso_temporal")
  aviso.configure(bg=color_actual)
  aviso.place(relx=0.35, rely=0.2, anchor="n")
  contenedor.after(milisegundos, aviso.destroy)

def cargar_imagen(ruta_subcarpeta_imagen, nombre_imagen, tamaño=(25, 25)):
    ruta = os.path.join(ruta_imagen, ruta_subcarpeta_imagen, nombre_imagen)
    if(not os.path.exists(ruta)):
        print(f"Imagen no encontrada: {ruta}")
        return ImageTk.PhotoImage(Image.new("RGBA", tamaño, (255, 255, 255, 0)))
    try:
        imagen = Image.open(ruta)
        imagen = imagen.resize(tamaño, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(imagen)
    except Exception as e:
        print(f"❌ Error al cargar imagen {nombre_imagen}: {e}")
        return None

#En esta función se crea un label que muestra la hora actual y se actualiza cada segundo
#pero si el label ya existe, sólo se actualiza su texto.
def actualizar_la_hora(contenedor):
  color_padre = contenedor.cget('bg')
  if hasattr(contenedor, 'label_Hora'):
    contenedor.label_Hora.config(text=fecha_y_hora.now().strftime("%H:%M:%S"))
  else:
    contenedor.label_Hora = tk.Label(contenedor, font=("Arial", 10, "bold"), bg=color_padre, fg="blue")
    contenedor.label_Hora.grid(row=20, column=0, sticky="ne", padx=0, pady=0)
    contenedor.label_Hora.config(text=fecha_y_hora.now().strftime("%H:%M:%S"))
  contenedor.after(1000, lambda: actualizar_la_hora(contenedor))