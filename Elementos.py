from PIL import Image, ImageTk
import os
# --- ELEMENTOS ---

dirección_del_ícono = os.path.dirname(__file__)
ícono = os.path.join(dirección_del_ícono, "imágenes","escuela.ico")
ruta_base = os.path.dirname(os.path.abspath(__file__))
ruta_imagen = os.path.join(ruta_base, "imágenes")
nombreActual = None
permitir_inserción = False
ventanaAbierta = {}
campos_en_db = {
      "alumno": ["Nombre", "FechaDeNacimiento", "IDCarrera"],
      "asistencia": ["Estado", "Fecha_Asistencia", "IDAlumno", "IDProfesor"],
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
    

colores = {
  "blanco": "#FFFFFF",
  "gris": "#AAAAAA",
  "negro": "#000000",
  "negro_resaltado": "#3A3A3A",
  "celeste_azulado": "#004CFF",
  "celeste": "#90C0FF",
  "celeste_resaltado": "#3F72FD",
  "azul": "#0000FF",
  "azul_claro": "#C5C5FF",
  "azul_oscuro": "#00004D"
}

consultas = {
      "alumno": {
          "select": """SELECT a.ID_Alumno, a.Nombre, 
                      DATE_FORMAT(a.FechaDeNacimiento, '%d/%m/%Y') AS Fecha, 
                      c.Nombre AS Carrera
                      FROM alumno a
                      JOIN carrera c ON a.IDCarrera = c.ID_Carrera""",
          "buscables": ["a.Nombre", "c.Nombre"]
      },
      "asistencia":{
          "select": """SELECT asis.ID, asis.Estado, DATE_FORMAT(asis.Fecha_Asistencia, '%d/%m/%Y') AS Fecha, al.Nombre AS Alumno, p.Nombre AS Profesor
                              FROM asistencia AS asis
                              JOIN alumno AS al ON asis.IDAlumno = al.ID_Alumno
                              JOIN profesor AS p ON asis.IDProfesor = p.ID_Profesor""",
          "buscables": ["asis.Estado", "al.Nombre"]
          },
       "enseñanza":{
          "select": """SELECT e.ID, m.Nombre AS Materia, p.Nombre AS Profesor
                              FROM enseñanza AS e
                              JOIN profesor AS p ON e.IDProfesor = p.ID_Profesor
                              JOIN materia AS m ON e.IDMateria = m.ID_Materia""",
          "buscables": ["m.Nombre", "p.Nombre"]
          },
      "carrera":{
          "select": """SELECT c.ID_Carrera, c.Nombre, c.Duración
                              FROM carrera AS c""",
          "buscables": ["c.Nombre", "c.Duración"]
          },
      "materia": {
          "select": """SELECT m.ID_Materia, m.Nombre, 
                              TIME_FORMAT(m.HorarioEntrada,'%H:%i') AS HorarioEntrada, TIME_FORMAT(m.HorarioSalida,'%H:%i') AS HorarioSalida,
                              c.Nombre AS Carrera
                      FROM materia m
                      JOIN carrera c ON m.IDCarrera = c.ID_Carrera""",
          "buscables": ["m.Nombre", "c.Nombre"]
      },
      "profesor":{
          "select":"""SELECT pro.ID_Profesor, pro.Nombre
                              FROM profesor AS pro""",
          "buscables": ["pro.Nombre"]
          },
      "nota":{
          "select": """SELECT n.ID, al.Nombre AS Alumno, m.Nombre AS Materia, p.Nombre AS Profesor,
                              REPLACE(CAST(n.valorNota AS CHAR(10)), '.', ',') AS Nota, 
                              n.tipoNota, DATE_FORMAT(n.fechaEvaluación, '%d/%m/%Y') AS FechaEv
                              FROM nota AS n
                              JOIN alumno AS al ON n.IDAlumno = al.ID_Alumno
                              JOIN materia AS m ON n.IDMateria = m.ID_Materia
                              JOIN profesor AS p ON n.IDProfesor = p.ID_Profesor""",
          "buscables": ["al.Nombre", "m.Nombre", "n.tipoNota"]
          }
    }

# --- FUNCIONES DE CARGA Y CONFIGURACIÓN ---
def cargar_imagen(ruta_subcarpeta_imagen, nombre_imagen, tamaño=(25, 25)):
    ruta = os.path.join(ruta_imagen, ruta_subcarpeta_imagen, nombre_imagen)
    if(not os.path.exists(ruta)):
        print(f"Imagen no encontrada: {ruta}")
        return None
    try:
        imagen = Image.open(ruta)
        imagen = imagen.resize(tamaño, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(imagen)
    except Exception as e:
        print(f"❌ Error al cargar imagen {nombre_imagen}: {e}")
        return None
    

def consulta_semántica(consultas_meta, nombre_de_la_tabla, valorBúsqueda, operador_like="%{}%"):
    meta = consultas_meta.get(nombre_de_la_tabla.lower())
    if not meta:
        raise ValueError(f"No existe metadata para la tabla '{nombre_de_la_tabla}'")

    select_sql = meta["select"].strip()
    buscables = meta.get("buscables", [])
    orden = meta.get("orden")
    
    if not valorBúsqueda:
        sql = select_sql
        if orden:
            sql = f"{sql} ORDER BY {orden}"
        params = ()
        return sql, params
    
    if not buscables:
        sql = select_sql
        if orden:
            sql = f"{sql} ORDER BY {orden}"
        params = ()
        return sql, params
    
    condiciones = " OR ".join(f"{campo} LIKE %s" for campo in buscables)
    sql = f"{select_sql} WHERE {condiciones}"
    if orden:
        sql = f"{sql} ORDER BY {orden}"
    params = tuple(operador_like.format(valorBúsqueda) for _ in buscables)
        
    return sql, params





