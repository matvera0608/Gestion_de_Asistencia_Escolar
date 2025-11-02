from PIL import Image, ImageTk
import os
dirección_del_ícono = os.path.dirname(__file__)
ícono = os.path.join(dirección_del_ícono, "imágenes","escuela.ico")
ruta_base = os.path.dirname(os.path.abspath(__file__))
ruta_imagen = os.path.join(ruta_base, "imágenes")


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
      "materia": {
          "select": """SELECT m.ID_Materia, m.Nombre, 
                              TIME_FORMAT(m.Horario,'%H:%i') AS Horario, 
                              c.Nombre AS Carrera
                      FROM materia m
                      JOIN carrera c ON m.IDCarrera = c.ID_Carrera""",
          "buscables": ["m.Nombre", "c.Nombre"]
      },
      "carrera":{
          "select": """SELECT c.ID_Carrera, c.Nombre, c.Duración
                              FROM carrera AS c""",
          "buscables": ["c.Nombre", "c.Duración"]
          },
      "asistencia":{
          "select": """SELECT asis.ID, asis.Estado, DATE_FORMAT(asis.Fecha_Asistencia, '%d/%m/%Y') AS Fecha, al.Nombre AS Alumno
                              FROM asistencia AS asis
                              JOIN alumno AS al ON asis.IDAlumno = al.ID_Alumno""",
          "buscables": ["asis.Estado", "al.Nombre"]
          },
       "enseñanza":{
          "select": """SELECT e.ID, m.Nombre AS Materia, p.Nombre AS Profesor
                              FROM enseñanza AS e
                              JOIN profesor AS p ON e.IDProfesor = p.ID_Profesor
                              JOIN materia AS m ON e.IDMateria = m.ID_Materia""",
          "buscables": ["m.Nombre", "p.Nombre"]
          },
      "profesor":{
          "select":"""SELECT pro.ID_Profesor, pro.Nombre
                              FROM profesor AS pro""",
          "buscables": ["pro.Nombre"]
          },
      "nota":{
          "select": """SELECT n.ID, al.Nombre AS Alumno, m.Nombre AS Materia, 
                              REPLACE(CAST(n.valorNota AS CHAR(10)), '.', ',') AS Nota, 
                              n.tipoNota, DATE_FORMAT(n.fecha, '%d/%m/%Y') AS FechaEv
                              FROM nota AS n
                              JOIN alumno AS al ON n.IDAlumno = al.ID_Alumno
                              JOIN materia AS m ON n.IDMateria = m.ID_Materia""",
          "buscables": ["al.Nombre", "m.Nombre", "n.tipoNota"]
          }
    }

# --- FUNCIÓN PARA CARGAR IMAGENES ---
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
