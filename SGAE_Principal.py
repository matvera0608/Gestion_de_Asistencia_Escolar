from Fun_ABM_SGAE import insertar_datos, modificar_datos, eliminar_datos, ordenar_datos, exportar_en_PDF
from Conexión import conectar_base_de_datos, desconectar_base_de_datos
from Fun_adicionales import consultar_tabla, actualizar_la_hora

import os
import tkinter as tk
from tkinter import ttk
from datetime import date as fecha, time as hora
from datetime import datetime as hora_del_sistema
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
ícono = os.path.join(dirección_del_ícono, "imágenes","escuela.ico")
ruta_base = os.path.dirname(__file__)
ruta_imagen = os.path.join(ruta_base, "imágenes")
ventanaAbierta = {}

# --- FUNCIÓN PARA CARGAR IMÁGENES, CONECTAR BASE DE DATOS Y DE MOSTRAR LA HORA ---
def cargar_imagen(nombre_imagen):
  ruta = os.path.join(ruta_imagen, nombre_imagen)
  if(not os.path.exists(ruta)):
    print(f"Imagen no encontrada: {ruta}")
    return None
  imagen = Image.open(ruta)
  imagen = imagen.resize((25, 25), Image.Resampling.LANCZOS)
  return ImageTk.PhotoImage(imagen)

mi_ventana = tk.Tk()


# --- FUNCIONES AUXILIARES ---

  #Esta función controla que rol es cada usuario
def validarRol(txBox, ventana=mi_ventana):
  rol = txBox.get().strip().lower()
  rolesVálidos = ["profesor", "docente", "administrativo", "personal administrativo"]
  
  if rol in rolesVálidos:
    mostrar_pestañas(ventana)
  else:
    print("Error de Login", f"Los roles permitidos son: {', '.join(rolesVálidos).title()}. Ingresar bien los datos")
    return

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
  
  #Iniciar Sesión
  botón_login = tk.Button(ventana, text="Iniciar Sesión", width=15)
  botón_login.config(fg="black", bg=colores["gris"], font=("Arial", 15), cursor='hand2', activebackground=colores["gris"], command = lambda: mostrar_pestañas(ventana))
  botón_login.grid(row=2, column=0, pady=30, sticky="s")
  
  actualizar_la_hora(ventana)
  
  return ventana

def mostrar_pestañas(ventana):
  global tablaAlumno, tablaAsistencia, tablaCarrera, tablaMateria, tablaMateria_Profesor, tablaProfesor, tablaNota, color_padre
  
  if actualizaciónHora is not None:
    ventana.after_cancel(actualizaciónHora)
    actualizaciónHora = None
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
  
  Lista_de_datos = tk.Listbox(marco_derecho, width=20, height=20, font=("Courier New", 10, "bold"))
  Lista_de_datos.grid(row=0, column=0, sticky="nsew")
  
  consultar_tabla(nombre_de_la_tabla)

# --- INICIO DEL SISTEMA ---
pantallaLogin()
mi_ventana.mainloop()
