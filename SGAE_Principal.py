from Fun_ABM_SGAE import cargar_datos_en_Combobox, insertar_datos, modificar_datos, eliminar_datos, eliminar_completamente ,buscar_datos, ordenar_datos, exportar_en_PDF, mostrar_registro
from Fun_adicionales import consultar_tabla
from Fun_Validación_SGAE import validar_fecha, validar_fecha_combobox,bloquear_caracter, validar_fecha_final, validar_hora
import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
# --- ELEMENTOS ---
nombreActual = None
colores = {
  "blanco": "#FFFFFF",
  "gris": "#AAAAAA",
  "negro": "#000000",
  "negro_resaltado": "#3A3A3A",
  "celeste_azulado": "#004CFF",
  "celeste": "#569FFF",
  "celeste_resaltado": "#3F72FD",
  "azul_claro": "#A8A8FF",
  "azul_oscuro": "#00004D"
}
dirección_del_ícono = os.path.dirname(__file__)
ícono = os.path.join(dirección_del_ícono, "imágenes","escuela.ico")
ruta_base = os.path.dirname(__file__)
ruta_imagen = os.path.join(ruta_base, "imágenes")
ventanaAbierta = {}
campos_en_db = {
      "alumno": ["Nombre", "FechaDeNacimiento", "IDCarrera"],
      "asistencia": ["Estado", "Fecha_Asistencia", "IDAlumno"],
      "carrera": ["Nombre", "Duración"],
      "materia": ["Nombre", "Horario", "IDCarrera"],
      "enseñanza": ["IDMateria", "IDProfesor"],
      "profesor": ["Nombre"],
      "nota": ["IDAlumno", "IDMateria", "valorNota", "tipoNota", "fecha"]
  }
lista_IDs = [] 

# os.system(".\Giteo.bat")

# --- FUNCIONES AUXILIARES ---
def cargar_imagen(nombre_imagen):
  ruta = os.path.join(ruta_imagen, nombre_imagen)
  if(not os.path.exists(ruta)):
    print(f"Imagen no encontrada: {ruta}")
    return None
  imagen = Image.open(ruta)
  imagen = imagen.resize((25, 25), Image.Resampling.LANCZOS)
  return ImageTk.PhotoImage(imagen)

def crear_etiqueta(contenedor, texto, fuenteLetra=("Arial", 10, "bold")):
  color_padre = contenedor.cget("bg")
  return tk.Label(contenedor, text=texto, fg=colores["negro"], bg=color_padre, font=fuenteLetra)

def crear_entrada(contenedor, ancho, estado="readonly",estilo="Entrada.TEntry"):
  return ttk.Entry(contenedor, width=ancho, style=estilo, state=estado)

def crear_listaDesp(contenedor, ancho, estado="readonly"):
  return ttk.Combobox(contenedor, width=ancho, state=estado)

def crear_botón(contenedor, texto, comando, ancho, estado ,estilo="Boton.TButton"):
  ancho = len(texto)
  return ttk.Button(contenedor, text=texto, width=ancho, command= lambda: comando(), style=estilo, cursor='hand2', state=estado)

def crear_tabla_Treeview(contenedor, tabla):
  global lista_IDs
  columnas = campos_en_db[tabla]
  estilo = ttk.Style()
  estilo_treeview = f"Custom.Treeview"
  estilo_encabezado = f"Custom.Treeview.Heading"
  
  estilo.configure(estilo_treeview, font=("Arial", 8), foreground=colores["negro"], background=colores["blanco"], bordercolor=colores["negro"], fieldbackground=colores["blanco"], relief="solid")
  estilo.configure(estilo_encabezado, font=("Courier New", 10), foreground=colores["negro"], background=colores["celeste"], bordercolor=colores["negro"])
  estilo.layout(estilo_treeview, [('Treeview.treearea', {'sticky': 'nswe'})])
  tabla_Treeview = ttk.Treeview(contenedor, columns=columnas, show="headings", style=estilo_treeview)
  
  for columna in columnas:
    tabla_Treeview.heading(columna, anchor="center", text=columna)
    tabla_Treeview.column(columna, anchor="center", width=max(100, len(columna)*12))
  
  tabla_Treeview.tag_configure("par", background=colores["blanco"])
  tabla_Treeview.tag_configure("impar", background=colores["celeste"])

  datos = consultar_tabla(tabla)
  
  for item in tabla_Treeview.get_children():
    tabla_Treeview.delete(item)
  
  for fila in datos:
    id_val = fila[0]
    valores_visibles = fila[1:]
    tabla_Treeview.insert("", "end", iid=str(id_val), values=valores_visibles)


  # for index, fila in enumerate(datos):
  #   tag = "par" if index % 2 == 0 else "impar"
  #   tabla_Treeview.insert("", "end", values=fila, tags=(tag,))
  
  tabla_Treeview.grid(row=0, column=0, sticky="nsew")
    
  return tabla_Treeview 

def iterar_entry_y_combobox(marco_izquierdo, nombre_de_la_tabla, campos):
  global listaDesplegable
  listaDesplegable = {}
  cajasDeTexto.setdefault(nombre_de_la_tabla, [])
  listaDesplegable.setdefault(nombre_de_la_tabla, [])
  
  for i, (texto_etiqueta, nombre_Interno) in enumerate(campos):
    crear_etiqueta(marco_izquierdo, texto_etiqueta).grid(row=i + 2, column=1, sticky="w", padx=1, pady=5)
    combo = crear_listaDesp(marco_izquierdo, 30)
    combo.widget_interno = nombre_Interno
    combo.grid(row=i + 2, column=2, sticky="ew", padx=1, pady=5)
    listaDesplegable[nombre_de_la_tabla].append(combo)
    cajasDeTexto[nombre_de_la_tabla].append(combo)
  cargar_datos_en_Combobox(nombre_de_la_tabla, listaDesplegable[nombre_de_la_tabla])

def crear_botonesExcluyentes(contenedor, texto, comando, estado="disabled", estilo="Radiobutton.TRadiobutton"):
  return ttk.Radiobutton(contenedor, text=texto, width=len(texto), command= comando(), state=estado, style=estilo, cursor='hand2')

def cerrar_abm(ventana):
    ventana.destroy()
    ventana = None

def configurar_ciertos_comboboxes(cbBox_tabla):
  for etiqueta, widget_interno in campos_por_tabla.get(cbBox_tabla, []):
      try:
        if widget_interno.startswith("cbBox_"):
          for widget in cajasDeTexto.get(cbBox_tabla, []):
            if getattr(widget, "widget_interno", "") == widget_interno:
              widget.config(state="readonly")
        elif widget_interno.startswith("txBox_"):
          for widget in cajasDeTexto.get(cbBox_tabla, []):
            if getattr(widget, "widget_interno", "") == widget_interno:
              widget.config(state="normal")
      except Exception as e:
        print(f"Error configurando {widget}: {e}")

def habilitar():
  if not hasattr(tabla_treeview, "winfo_exists") or not tabla_treeview.winfo_exists():
    return
  for botón in [btnModificar, btnEliminar, btnEliminarTODO, btnOrdenar, btnExportarPDF, btnCancelar]:
    botón.config(state="normal")
    
  entryBuscar.config(state="normal")
  tabla_treeview.config(selectmode="browse")
  tabla_treeview.unbind("<Button-1>")
  tabla_treeview.unbind("<Key>")
  tabla_treeview.bind("<<TreeviewSelect>>", lambda event: mostrar_registro(nombreActual, tabla_treeview, cajasDeTexto))
  
  
  configurar_ciertos_comboboxes(nombreActual)

def deshabilitar():
  if not hasattr(tabla_treeview, "winfo_exists") or not tabla_treeview.winfo_exists():
    return
  for botón in [btnModificar, btnEliminar, btnEliminarTODO, btnOrdenar, btnExportarPDF, btnCancelar]:
    botón.config(state="disabled")
  
  tabla_treeview.bind("<Button-1>", lambda e: "break")
  tabla_treeview.bind("<Key>", lambda e: "break")
  tabla_treeview.selection_remove(tabla_treeview.selection())
  
  for entry in cajasDeTexto[nombreActual]:
    entry.delete(0, tk.END)
    try:
      entry.config(state="readonly")
    except:
      pass

# --- Función doble ---

def insertar():
  tablas_de_datos = tabla_treeview
  if not hasattr(tablas_de_datos, "winfo_exists") or not tablas_de_datos.winfo_exists():
    return
  
  habilitar()
  if any(widget.get().strip() == "" for widget in cajasDeTexto[nombreActual]):
    return
  insertar_datos(nombreActual, cajasDeTexto, campos_en_db, tabla_treeview)

# --- EJECUCIÓN DE LA VENTANA PRINCIPAL ---
mi_ventana = tk.Tk()

# def pantallaLogin():
#   ventana = mi_ventana
#   ventana.title("Sistema Gestor de Asistencias")
#   ventana.geometry("450x200")
#   ventana.configure(bg=colores["blanco"])
#   ventana.iconbitmap(ícono)
#   ventana.resizable(width=False, height=False)
#   ventana.grid_columnconfigure(0, weight=1)
#   ventana.grid_rowconfigure(2, weight=1)

#   #Etiqueta para rol
#   label_usuario_rol = tk.Label(ventana, text="ROL", bg=colores["blanco"], fg=colores["negro"], font=("Arial", 15, "bold"))
#   label_usuario_rol.grid(row=0, column=0, pady=(20, 5), sticky="n")
  
#   #Entry para el usuario
#   txBox_usuario = tk.Entry(ventana, font=("Arial", 15), width=20, fg=colores["negro_resaltado"])
#   txBox_usuario.grid(row=1, column=0, pady=(0, 20), sticky="n")
#   txBox_usuario.insert(0, "docente")
  
#   #Esta función controla que rol es cada usuario
#   def validarRol(txBox=txBox_usuario):
#     rol = txBox.get().strip().lower()
#     rolesVálidos = ["profesor", "docente", "administrativo", "personal administrativo"]
    
#     if rol in rolesVálidos:
#       mostrar_pestañas(ventana)
#     else:
#       print("Error de Login", f"Los roles permitidos son: {', '.join(rolesVálidos).title()}. Ingresar bien los datos")
#       return
  
#   #Iniciar Sesión
#   botón_login = tk.Button(ventana, text="Iniciar Sesión", width=15)
#   botón_login.config(fg="black", bg=colores["gris"], font=("Arial", 15), cursor='hand2', activebackground=colores["gris"], command=validarRol)
#   botón_login.grid(row=2, column=0, pady=30, sticky="s")
  
#   # actualizar_la_hora(ventana)
#   return ventana

#Creo un diccionario para tener como referencia de la tabla con el fin de globalizar nombre de la tabla


def mostrar_pestañas(ventana):
  ventana = mi_ventana
  ventana.title("Sistema Gestor de Asistencias")
  ventana.geometry("400x200")
  ventana.configure(bg=colores["blanco"])
  ventana.iconbitmap(ícono)
  ventana.resizable(width=False, height=False)
  ventana.grid_columnconfigure(0, weight=1)
  ventana.grid_rowconfigure(2, weight=1)
  global tablaAlumno, tablaAsistencia, tablaCarrera, tablaMateria, tablaMateria_Profesor, tablaProfesor, tablaNota, color_padre
  
  for widget in ventana.winfo_children():
    widget.destroy()
  
  estilo = ttk.Style()
  estilo.theme_use("clam")
  estilo.configure("TNotebook.Tab", font=("Arial", 8))
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
  notebook.carga_inicial = True
  
  def on_tab_change(event):
    if getattr(notebook, "carga_inicial", False):
      return
    pestaña = notebook.tab(notebook.select(), "text").lower()
    abrir_tablas(pestaña) 
  
  lb_obligatoriedad = tk.Label(notebook, text="* Campos obligatorios, es decir, no puede estar vacíos", bg=ventana.cget("bg"), font=("Arial", 10))
  lb_obligatoriedad.pack(side="bottom", pady=5)
  
  notebook.bind("<<NotebookTabChanged>>", on_tab_change)
  
  notebook.select(None)
  
  ventana.after(100, lambda: setattr(notebook, "carga_inicial", False))
  
#En esta función deseo meter la lógica de cada ABM, entries, labels, botones del CRUD y una listBox
def abrir_tablas(nombre_de_la_tabla):
  global ventanaSecundaria, btnAgregar, btnModificar, btnEliminar, btnEliminarTODO, btnOrdenar, btnExportarPDF, btnCancelar, cajasDeTexto, nombreActual
  global tabla_treeview, rbMostrar, rbOcultar, campos_por_tabla, entryBuscar
  nombreActual = nombre_de_la_tabla
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

  campos_comunes = [("Nombre*", "txBox_Nombre")]
  
  campos_por_tabla = {
    "alumno": campos_comunes + [
      ("Fecha de nacimiento*", "txBox_FechaNacimiento"),
      ("Carrera*", "cbBox_Carrera")
    ],
    "asistencia": [
      ("Estado*", "txBox_EstadoAsistencia"),
      ("Fecha*", "txBox_FechaAsistencia"),
      ("Alumno*", "cbBox_Alumno")
    ],
    "carrera": campos_comunes + [
        ("Duración*", "txBox_Duración")
    ],
    "materia": campos_comunes + [
      ("Horario*", "txBox_Horario"),
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
        ("Nota*", "txBox_Valor"),
        ("Evaluación*", "txBox_TipoEvaluación"),
        ("Fecha y Hora*", "txBox_FechaHora"),
    ]
  }
  cajasDeTexto = {}
  cajasDeTexto[nombre_de_la_tabla] = []
  
  def aplicar_validación_fecha(widget):
    vcmd_key = (mi_ventana.register(validar_fecha_combobox), "%P")
    widget.config(validate="key", validatecommand=vcmd_key)
    widget.bind("<FocusOut>", lambda e: validar_fecha_final(e))
    widget.bind("<KeyPress>", lambda e: bloquear_caracter(e))
    
  for tabla, campos in campos_por_tabla.items():
    for etiqueta, widget_interno in campos:
      widget = next((w for w in cajasDeTexto.get(tabla, []) if getattr(w, "widget_interno", "") == widget_interno),None)
      if widget and widget_interno.startswith("txBox"):
          aplicar_validación_fecha(widget)
      
      
  # --- Creamos un estilo global ---
  estilo = ttk.Style()
  estilo.theme_use("clam") #clam es el mejor tema para personalizar
  estilo.configure("Boton.TButton", font=("Arial", 10, "bold"), foreground=colores["blanco"], background=colores["celeste_azulado"], padding=10)
  estilo.configure("Radiobutton.TRadiobutton", font=("Arial", 10, "bold"), foreground=colores["blanco"], background=colores["azul_claro"])
  estilo.configure("Entrada.TEntry", padding=5, relief="flat", foreground=colores["negro"], fieldbackground=colores["blanco"])
  estilo.map("Boton.TButton", background=[("active", colores["celeste_resaltado"])])

  campos = campos_por_tabla.get(nombre_de_la_tabla, None)
  if not campos:
    return
  
  crear_etiqueta(ventanaSecundaria, "Buscar").grid(row=2, column=0)
  entryBuscar = crear_entrada(ventanaSecundaria, 40)
  entryBuscar.grid(row=3, column=0)
  entryBuscar.bind("<KeyRelease>", lambda event: buscar_datos(nombre_de_la_tabla, tabla_treeview, campos_en_db, campos_comunes))
  
  iterar_entry_y_combobox(marco_izquierdo, nombre_de_la_tabla, campos)
  
  
  rbMostrar = crear_botonesExcluyentes(marco_izquierdo, "Mostrar", lambda: None)
  rbMostrar.grid(row=0, column=1, sticky="n")
  rbOcultar = crear_botonesExcluyentes(marco_izquierdo, "Ocultar", lambda: None)
  rbOcultar.grid(row=0, column=2, sticky="n")
  
  tabla_treeview = crear_tabla_Treeview(marco_derecho, tabla=nombre_de_la_tabla)
  tabla_treeview.config(selectmode="none")
  
  btnCancelar = crear_botón(marco_izquierdo, "Cancelar", lambda: deshabilitar(), 10, "disabled")
  btnCancelar.grid(row=0, column=0, pady=10, padx=0, sticky="ew")
  
  btnAgregar = crear_botón(marco_izquierdo, "Agregar", lambda: insertar(), 10, "normal")
  btnAgregar.grid(row=1, column=0, pady=10, padx=0, sticky="ew")
  
  btnModificar = crear_botón(marco_izquierdo, "Modificar", lambda: modificar_datos(nombre_de_la_tabla, cajasDeTexto, campos_en_db, tabla_treeview, lista_IDs), 10, "disabled")
  btnModificar.grid(row=2, column=0, pady=10, padx=0, sticky="ew")
  
  btnEliminar = crear_botón(marco_izquierdo, "Eliminar", lambda: eliminar_datos(nombre_de_la_tabla, cajasDeTexto, campos_en_db, tabla_treeview, lista_IDs), 10, "disabled")
  btnEliminar.grid(row=3, column=0, pady=10, padx=0, sticky="ew")
  
  btnEliminarTODO = crear_botón(marco_izquierdo, "Eliminar Todo", lambda: eliminar_completamente(nombre_de_la_tabla, cajasDeTexto, campos_en_db, tabla_treeview, lista_IDs), 10, "disabled")
  btnEliminarTODO.grid(row=4, column=0, pady=10, padx=0, sticky="ew")
  
  btnOrdenar = crear_botón(marco_izquierdo, "Ordenar", lambda: ordenar_datos(nombre_de_la_tabla, tabla_treeview), 10, "disabled")
  btnOrdenar.grid(row=5, column=0, pady=10, padx=0, sticky="ew")
  
  btnExportarPDF = crear_botón(marco_izquierdo, "Exportar", lambda: exportar_en_PDF(nombre_de_la_tabla, tabla_treeview), 10, "disabled")
  btnExportarPDF.grid(row=6, column=0, pady=10, padx=0, sticky="ew")


# --- INICIO DEL SISTEMA ---

# pantallaLogin()
mostrar_pestañas(mi_ventana)
mi_ventana.protocol("WM_DELETE_WINDOW", lambda: cerrar_abm(mi_ventana))
mi_ventana.mainloop()