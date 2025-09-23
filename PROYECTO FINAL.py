import os
import mysql.connector as MySql
from mysql.connector import Error as error_sql
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mensajeTexto
from PIL import Image, ImageTk

# --- COLORES EN HEXADECIMALES ---
colores = {
  "blanco": "#FFFFFF",
  "gris": "#AAAAAA",
  "negro": "#000000",
  "negro_resaltado": "#3A3A3A",
  "celeste_azulado": "#004CFF",
  "celeste_resaltado": "#3F72FD",
  "azul_claro": "#A8A8FF"
}

dirección_del_ícono = os.path.dirname(__file__)
ícono = os.path.join(dirección_del_ícono,"escuela.ico")
ventanaAbierta = {}
ruta_base = os.path.dirname(__file__)
ruta_imagen = os.path.join(ruta_base, "imágenes")

# --- FUNCIÓN PARA CARGAR IMÁGENES ---
def cargar_imagen(nombre_imagen):
  ruta = os.path.join(ruta_imagen, nombre_imagen)
  if(not os.path.exists(ruta)):
    print(f"Imagen no encontrada: {ruta}")
    return None
  imagen = Image.open(ruta)
  imagen = imagen.resize((25, 25), Image.Resampling.LANCZOS)
  return ImageTk.PhotoImage(imagen)


#Esta es mi función para conectar a la base de datos,
# es decir, contiene la cadena de conexión
def conectar_base_de_datos():
  try:
    cadena_de_conexión = MySql.connect(
        host = 'localhost',
        user = 'root',
        password = 'admin',
        database = 'escuela')
    conexión_exitosa = cadena_de_conexión.is_connected()
    if conexión_exitosa:
      return cadena_de_conexión
  except error_sql as e:
    print(f"Error inesperado al conectar MySql {e}")
    return None

#Y este es para desconectar la base de datos
def desconectar_base_de_datos(conexión):
  desconectando_db = conexión.is_connected()
  if desconectando_db:
    conexión.close()

# --- FUNCIONES DE LECTURA ---
# Esta función sirve sólo para leer datos de la bases de datos escuela
def consultar_tabla(nombre_de_la_tabla):
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

mi_ventana = tk.Tk()


# --- FUNCIONES AUXILIARES PARA CREAR WIDGETS ---
def crear_etiqueta(contenedor, texto, tamaño_letra):
  color_padre = contenedor.cget("bg")
  return tk.Label(contenedor, text=texto, fg=colores["negro"], bg=color_padre, font=("Arial", tamaño_letra, "bold"))

def crear_entrada(contenedor, ancho, estilo="Entrada.TEntry"):
  return ttk.Entry(contenedor, width=ancho, style=estilo)

def crear_botón(contenedor, texto, comando, ancho, estilo="Boton.TButton"):
  ancho = len(texto) + 5 if ancho is None else ancho
  return ttk.Button(contenedor, text=texto, width=ancho, command=comando, style=estilo, cursor='hand2')

# --- EJECUCIÓN DE LA VENTANA PRINCIPAL ---
def pantallaLogin():
  ventana = mi_ventana
  ventana.title("Sistema Gestor de Asistencias")
  ventana.geometry("450x200")
  ventana.configure(bg=colores["blanco"])
  ventana.iconbitmap(ícono)
  ventana.resizable(width=False, height=False)
  ventana.grid_columnconfigure(0, weight=1)
  ventana.grid_rowconfigure(2, weight=1)

  #Etiqueta para rol
  label_usuario_rol = tk.Label(ventana, text="ROL", bg=colores["blanco"], fg=colores["negro"], font=("Arial", 15, "bold"))
  label_usuario_rol.grid(row=0, column=0, pady=(20, 5), sticky="n")
  
  #Entry para el usuario
  txBox_usuario = tk.Entry(ventana, font=("Arial", 15), width=20, fg=colores["negro_resaltado"])
  txBox_usuario.grid(row=1, column=0, pady=(0, 20), sticky="n")
  txBox_usuario.insert(0, "docente")
  
  #Esta función controla que rol es cada usuario
  def validarRol():
    rol = txBox_usuario.get().strip().lower()
    rolesVálidos = ["profesor", "docente", "administrativo", "personal administrativo"]
    
    if rol in rolesVálidos:
      mostrar_pestañas(ventana)
    else:
      print("Error de Login", f"Los roles permitidos son: {', '.join(rolesVálidos).title()}. Ingresar bien los datos")
      return

  #Iniciar Sesión
  botón_login = tk.Button(ventana, text="Iniciar Sesión", width=15)
  botón_login.config(fg="black", bg=colores["gris"], font=("Arial", 15), cursor='hand2', activebackground=colores["gris"],  command= validarRol)
  botón_login.grid(row=2, column=0, pady=30, sticky="s")
  
  return ventana

def mostrar_pestañas(ventana):
  global notebook, tablaAlumno, tablaAsistencia, tablaCarrera, tablaMateria, tablaMateria_Profesor, tablaProfesor, tablaNota, color_padre

  for widget in ventana.winfo_children():
    widget.destroy()
  
  estilo = ttk.Style()
  
  notebook = ttk.Notebook(ventana)
  notebook.pack(expand=True, fill="both")
  
  
  tablaAlumno = tk.Frame(notebook)
  tablaAsistencia = tk.Frame(notebook)
  tablaCarrera = tk.Frame(notebook)
  tablaMateria = tk.Frame(notebook)
  tablaMateria_Profesor = tk.Frame(notebook)
  tablaProfesor = tk.Frame(notebook)
  tablaNota = tk.Frame(notebook)

  notebook.add(tablaAlumno, text="Alumno")
  notebook.add(tablaAsistencia, text="Asistencia")
  notebook.add(tablaCarrera, text="Carrera")
  notebook.add(tablaMateria, text="Materia")
  notebook.add(tablaMateria_Profesor, text="Enseñanza")
  notebook.add(tablaProfesor, text="Profesor")
  notebook.add(tablaNota, text="Nota")
  
  color_padre = estilo.lookup("TNotebook", "background")
  lb_obligatoriedad = tk.Label(notebook, text="* Campos obligatorios, es decir, no puede estar vacíos", bg=color_padre, font=("Arial", 10))
  lb_obligatoriedad.pack(side="bottom", pady=5)
  
  notebook.bind("<<NotebookTabChanged>>", lambda event: abrir_tablas(notebook.tab(notebook.select(), "text").lower()))
  
#En esta función deseo meter la lógica de cada ABM, entries, labels, botones del CRUD y una listBox
def abrir_tablas(nombre_de_la_tabla):
  global Lista_de_datos, campos_de_la_tabla, ventanaSecundaria

  if nombre_de_la_tabla in ventanaAbierta and ventanaAbierta[nombre_de_la_tabla].winfo_exists():
    return
    

  íconos_por_tabla = {
    "alumno": os.path.join(ruta_base, "imágenes", "alumno.ico"),
    "asistencia": os.path.join(ruta_base, "imágenes", "asistencia.ico"),
    "carrera": os.path.join(ruta_base, "imágenes", "carrera.ico"),
    "materia": os.path.join(ruta_base, "imágenes", "materia.ico"),
    "enseñanza": os.path.join(ruta_base, "imágenes", "enseñanza.ico"),
    "profesor": os.path.join(ruta_base, "imágenes", "profesor.ico"),
    "nota": os.path.join(ruta_base, "imágenes", "nota.ico")
    }
  ventanaSecundaria = tk.Toplevel()
  ventanaSecundaria.title(f"{nombre_de_la_tabla.upper()}")
  ventanaSecundaria.geometry("900x450")
  ventanaSecundaria.resizable(width=False, height=False)
  ventanaSecundaria.configure(bg=colores["azul_claro"])
  
  ventanaAbierta[nombre_de_la_tabla] = ventanaSecundaria
  
  ventanaSecundaria.grid_columnconfigure(0, weight=1, uniform="panels")
  ventanaSecundaria.grid_columnconfigure(1, weight=1, uniform="panels")
  ventanaSecundaria.grid_rowconfigure(0, weight=1)
  
  ruta_ícono = íconos_por_tabla.get(nombre_de_la_tabla)
  if ruta_ícono and os.path.exists(ruta_ícono):
    try:
        ventanaSecundaria.iconbitmap(ruta_ícono)
    except tk.TclError:
        print("Error de Ícono", f"No se pudo cargar el ícono: {ruta_ícono}. Asegúrate de que el archivo existe y es válido (.ico).")
  elif ruta_ícono:
      print("Advertencia de Ícono", f"El archivo de ícono no se encontró en la ruta: {ruta_ícono}.")

  
  marco_izquierdo = tk.Frame(ventanaSecundaria, bg=colores["azul_claro"], padx=15, pady=15)
  marco_izquierdo.grid(row=0, column=0, sticky="nsew")
  
  marco_derecho = tk.Frame(ventanaSecundaria, bg=colores["azul_claro"], padx=15, pady=15)
  marco_derecho.grid(row=0, column=1, sticky="nsew")

  
  marco_izquierdo.grid_columnconfigure(0, weight=0)
  marco_izquierdo.grid_columnconfigure(1, weight=1)
  
  marco_derecho.grid_columnconfigure(0, weight=1)
  marco_derecho.grid_rowconfigure(0, weight=1)

  # Diccionario que mapea los nombres de las tablas a sus campos
  campos_por_tabla = {
      "alumno": [
          ("Nombre*", "txBox_NombreAlumno"),
          ("Fecha que nació*", "txBox_FechaNacimiento"),
          ("Carrera*","txBox_NombreCarrera")
      ],
      "asistencia": [
          ("Estado*", "txBox_EstadoDeAsistencia"),
          ("Fecha que asistió*", "txBox_FechaAsistencia"),
          ("Alumno que asistió*", "txBox_NombreAlumno")
      ],
      "carrera": [
          ("Nombre*", "txBox_NombreCarrera"),
          ("Duración*", "txBox_Duración")
      ],
      "materia": [
          ("Nombre*", "txBox_NombreMateria"),
          ("Horario*", "txBox_HorarioCorrespondiente")
      ],
      "enseñanza": [
          ("Nombre de la asignatura*", "txBox_NombreMateria"),
          ("Nombre del profesor*", "txBox_NombreProfesor")
      ],
      "profesor": [
          ("Nombre*", "txBox_NombreProfesor")
      ],
      "nota": [
          ("Nota*", "txBox_Valor"),
          ("Tipo de evaluación*", "txBox_Tipo"),
          ("Fecha y Hora*", "txBox_Fecha"),
          ("Nombre del estudiante*", "txBox_NombreAlumno"),
          ("Nombre de la asignatura*", "txBox_NombreMateria")
      ]
  }
  # --- Creamos un estilo global ---
  estilo = ttk.Style()
  estilo.theme_use("clam")
  estilo.configure("Boton.TButton", font=("Arial", 10, "bold"), foreground=colores["blanco"], background=colores["celeste_azulado"], padding=10)
  estilo.configure("Entrada.TEntry", padding=5, relief="flat", foreground=colores["negro"], fieldbackground=colores["blanco"])
  estilo.map("Boton.TButton", background=[("active", colores["celeste_resaltado"])])

  campos = campos_por_tabla.get(nombre_de_la_tabla, None)
  if not campos:
    return
  
  for i, (texto_etiqueta, _) in enumerate(campos): #Este for agrega dinámicamente siguiendo la longitud del diccionario
    crear_etiqueta(marco_izquierdo, texto_etiqueta, 10).grid(row=i + int(2.5), column=1, sticky="w", padx=1, pady=5)
    crear_entrada(marco_izquierdo, 20).grid(row=i + int(2.5), column=2, sticky="ew", padx=1, pady=5)
    
  crear_botón(marco_izquierdo, "Agregar", None, 10,).grid(row=1, column=0, pady=15, padx=2, sticky="ew")
  crear_botón(marco_izquierdo, "Modificar", None, 10).grid(row=2, column=0, pady=15, padx=2, sticky="ew")
  crear_botón(marco_izquierdo, "Eliminar", None, 10).grid(row=3, column=0, pady=15, padx=2, sticky="ew")
  crear_botón(marco_izquierdo, "Ordenar", None, 10).grid(row=4, column=0, pady=15, padx=2, sticky="ew")
  crear_botón(marco_izquierdo, "Exportar", None, 10).grid(row=5, column=0, pady=15, padx=2, sticky="ew")
  
  Lista_de_datos = tk.Listbox(marco_derecho, width=30, height=20, font=("Courier New", 10, "bold"))
  Lista_de_datos.grid(row=0, column=0, sticky="nsew")
  
  consultar_tabla(nombre_de_la_tabla)

# --- INICIO DEL SISTEMA ---
pantallaLogin()
mi_ventana.mainloop()
