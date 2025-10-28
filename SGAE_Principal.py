from Fun_ABM_SGAE import cargar_datos_en_Combobox, insertar_datos, modificar_datos, eliminar_datos, guardar_datos, buscar_datos, ordenar_datos, exportar_en_PDF, mostrar_registro
from Fun_adicionales import consultar_tabla,ocultar_encabezado, mostrar_encabezado, consultas
from Fun_Validación_SGAE import aplicar_validación_fecha, aplicar_validación_hora
from Eventos import mover_con_flechas
from Elementos import colores, ícono, ruta_base, cargar_imagen
import os
import tkinter as tk
from tkinter import ttk
from functools import partial

# --- ELEMENTOS ---
nombreActual = None
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
alias = {
"IDCarrera": "Carrera",
"IDMateria": "Materia",
"IDProfesor": "Profesor",
"IDAlumno": "Alumno",
"FechaDeNacimiento": "Fecha de nacimiento",
"valorNota": "Nota",
"tipoNota": "Evaluación",
"Fecha_Asistencia": "Fecha",
}


def crear_etiqueta(contenedor, texto, fuenteLetra=("Arial", 10, "bold")):
  color_padre = contenedor.cget("bg")
  return tk.Label(contenedor, text=texto, fg=colores["negro"], bg=color_padre, font=fuenteLetra)


def crear_entrada(contenedor, ancho, estado="readonly",estilo="Entrada.TEntry"):
  return ttk.Entry(contenedor, width=ancho, style=estilo, state=estado)


def crear_listaDesp(contenedor, ancho, estado="readonly"):
  return ttk.Combobox(contenedor, width=ancho, state=estado)


def crear_botón(contenedor, texto, imágen, comando, estado, estilo="Boton.TButton"):
  return ttk.Button(contenedor, text=texto, image=imágen, compound="left", width=10, command= lambda: comando(), style=estilo, state=estado, cursor='hand2')


def crear_tabla_Treeview(contenedor, tabla):
  columnas = campos_en_db[tabla]

  estilo = ttk.Style()
  estilo_treeview = f"Custom.Treeview"
  estilo_encabezado = f"Custom.Treeview.Heading"
  
  estilo.configure(estilo_treeview, font=("Arial", 8), foreground=colores["negro"], background=colores["blanco"], bordercolor=colores["negro"], fieldbackground=colores["blanco"], relief="solid")
  estilo.configure(estilo_encabezado, font=("Courier New", 10), foreground=colores["negro"], background=colores["azul"], bordercolor=colores["negro"])
  estilo.layout(estilo_treeview, [('Treeview.treearea', {'sticky': 'nswe'})])
  
  frame_tabla = tk.Frame(contenedor, bg=colores["blanco"])
  frame_tabla.grid(row=0, column=0, sticky="nsew")
  
  tabla_Treeview = ttk.Treeview(frame_tabla, columns=columnas, show="headings", style=estilo_treeview)
  ancho = 175
  
  def fijar_ancho(event):
    region = event.widget.identify_region(event.x, event.y)
    if region == "separator":
      event.widget.after(1, lambda: [
      event.widget.column(col, width=ancho, minwidth=ancho, stretch=False)
      for col in columnas 
      ])
  for columna in columnas:
    nombre_legible = alias.get(columna, columna)
    tabla_Treeview.heading(columna, anchor="center", text=nombre_legible)
    tabla_Treeview.column(columna, anchor="center",width=ancho, minwidth=ancho, stretch=False)
  tabla_Treeview.bind("<ButtonRelease-1>", fijar_ancho)
  
  barraVertical = tk.Scrollbar(frame_tabla, orient="vertical", command=tabla_Treeview.yview)
  barraHorizontal = tk.Scrollbar(frame_tabla, orient="horizontal", command=tabla_Treeview.xview)

  tabla_Treeview.configure(yscrollcommand=barraVertical.set, xscrollcommand=barraHorizontal.set)

  tabla_Treeview.grid(row=0, column=0, sticky="nsew")
  barraVertical.grid(row=0, column=1, sticky="ns")
  barraHorizontal.grid(row=1, column=0, sticky="ew")
  
  
  frame_tabla.grid_rowconfigure(0, weight=1)
  frame_tabla.grid_columnconfigure(0, weight=1)

  for item in tabla_Treeview.get_children():
    tabla_Treeview.delete(item)
  
  datos = consultar_tabla(tabla)
  
  for índice, fila in enumerate(datos):
    id_val = fila[0]
    valores_visibles = fila[1:]
    
    tag = "par" if índice % 2 == 0 else "impar"
    tabla_Treeview.insert("", "end", iid=str(id_val), values=valores_visibles, tags=(tag,))

  tabla_Treeview.tag_configure("par", background=colores["blanco"])
  tabla_Treeview.tag_configure("impar", background=colores["celeste"])
    
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
  for tabla, campos in campos_por_tabla.items():
    for etiqueta, widget_interno in campos:
      widget = next((w for w in cajasDeTexto.get(tabla, []) if getattr(w, "widget_interno", "") == widget_interno), None)
      if widget and widget_interno.startswith("txBox_Fecha"):
        aplicar_validación_fecha(widget, mi_ventana)
      elif widget and widget_interno.startswith("txBox_Hora"):
        aplicar_validación_hora(widget, mi_ventana)


def crear_botonesExcluyentes(contenedor, texto, vari, valor, estado="disabled", estilo="Radiobutton.TRadiobutton"):
  return ttk.Radiobutton(contenedor, text=texto, width=len(texto),variable=vari, value=valor, state=estado, style=estilo, cursor='hand2')


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


def seleccionar_encabezado(event, treeview, var_rb):
  región = treeview.identify_region(event.x, event.y)
  if región == "heading":
    columna = treeview.identify_column(event.x)
    if columna == "#0":
      print("Clic en la columna de ítems (no en las definidas)")
      return
    
    idx = int(columna.replace("#", "")) - 1
    columnas = treeview["columns"]
    if 0 <= idx < len(columnas):
        selección = treeview["columns"][idx]
        texto = alias.get(selección, selección)
        ocultar_encabezado(treeview, selección, var_rb)
        print(f"OCULTANDO {texto}")


def habilitar(treeview):
  tabla_treeview.delete(*tabla_treeview.get_children())
  
  #LO DE ARRIBA COMENTÉ PORQUE NO HAY DATOS EN MEMORIA CACHÉ, TRAJE LA MISMA LÓGICA ZEBRA ROWS PARA QUE A LA HORA DE ITERAR
  #NO ME MUESTREN LOS IDs ARTIFICIALES.
  datos_a_refrescar = consultar_tabla(nombreActual)
  for índice, fila in enumerate(datos_a_refrescar):
    id_val = fila[0]
    valores_visibles = fila[1:]
    tag = "par" if índice % 2 == 0 else "impar"
    treeview.insert("", "end", iid=str(id_val), values=valores_visibles, tags=(tag,))

  for botón in [btnModificar, btnEliminar, btnExportarPDF, btnGuardar, btnImportar, btnCancelar]:
    botón.config(state="normal")
  
  for radiobutton in [rbMostrar, rbOcultar]:
    radiobutton.config(state="normal")
  
  entryBuscar.config(state="normal")
  treeview.config(selectmode="browse")
  treeview.unbind("<Button-1>")
  treeview.unbind("<Key>")
  treeview.bind("<<TreeviewSelect>>", lambda e: mostrar_registro(nombreActual, tabla_treeview, cajasDeTexto))
  
  configurar_ciertos_comboboxes(nombreActual)


def deshabilitar(treeview):
  
  tabla_treeview.delete(*tabla_treeview.get_children())
  
  for botón in [btnModificar, btnEliminar, btnExportarPDF, btnGuardar, btnImportar, btnCancelar]:
    botón.config(state="disabled")
  
  for radiobutton in [rbMostrar, rbOcultar]:
    radiobutton.config(state="disabled")
  var_rb.set("")

  treeview.bind("<Button-1>", lambda e: "break")
  treeview.bind("<Key>", lambda e: "break")
  treeview.selection_remove(treeview.selection())
  entryBuscar.config(state="readonly")
  for entry in cajasDeTexto[nombreActual]:
    entry.delete(0, tk.END)
    try:
      entry.config(state="readonly")
    except:
      pass

# --- Función doble ---

def insertar(tabla_treeview):
  if not hasattr(tabla_treeview, "winfo_exists") or not tabla_treeview.winfo_exists():
    return
  habilitar(tabla_treeview)
  if any(widget.get().strip() == "" for widget in cajasDeTexto[nombreActual]):
    return
  insertar_datos(nombreActual, cajasDeTexto, campos_en_db, tabla_treeview)


  # --- ESTOS SON PARA LOS EVENTOS.


# --- EJECUCIÓN DE LA VENTANA PRINCIPAL ---

mi_ventana = tk.Tk()

íconos_por_tabla = {
  "alumno": os.path.join(ruta_base, "imágenes", "alumno.ico"),
  "asistencia": os.path.join(ruta_base, "imágenes", "asistencia.ico"),
  "carrera": os.path.join(ruta_base, "imágenes", "carrera.ico"),
  "materia": os.path.join(ruta_base, "imágenes", "materia.ico"),
  "enseñanza": os.path.join(ruta_base, "imágenes", "enseñanza.ico"),
  "profesor": os.path.join(ruta_base, "imágenes", "profesor.ico"),
  "nota": os.path.join(ruta_base, "imágenes", "nota.ico")
}

imágenes_por_botón = {
  "cancelar": cargar_imagen("botones", "cancelar.png"),
  "agregar": cargar_imagen("botones", "agregar.png"),
  "modificar": cargar_imagen("botones", "modificar.png"),
  "eliminar": cargar_imagen("botones", "eliminar.png"),
  "guardar": cargar_imagen("botones", "guardar.png"),
  "importar": cargar_imagen("botones", "importar_desde.png"),
  "exportar": cargar_imagen("botones", "exportar_como_pdf.png")
}

def pantallaLogin():
  ventana = mi_ventana
  ventana.title("Sistema Gestor de Asistencias")
  ventana.geometry("400x200")
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
  
  rolesVálidos = {
    "profesor": ("alumno", "asistencia", "materia", "nota"),
    "profesora": ("alumno", "asistencia", "materia", "nota"),
    "docente": ("alumno", "asistencia", "materia", "nota"),

    "administrativo": ("carrera", "profesor", "materia", "enseñanza"),
    "personal administrativo": ("carrera", "profesor", "materia", "enseñanza"),
    "coordinador": ("carrera", "profesor", "materia", "enseñanza"),
    "coordinadora": ("carrera", "profesor", "materia", "enseñanza"),
    "secretario": ("carrera", "profesor", "materia", "enseñanza"),
    "secretaria": ("carrera", "profesor", "materia", "enseñanza")
    }
  
  #Esta función controla que rol es cada usuario
  def validarRol(txBox=txBox_usuario):
    try:
      rol = txBox.get().strip().lower()
      if rol in rolesVálidos:
        permiso = rolesVálidos[rol]
        print(f"ACCESO CONCEDIDO: BIENVENIDOS A {rol.title()}")
        mostrar_pestañas(ventana, permiso)
      else:
        print(f"ACCESO DENEGADO: Los roles permitidos son: {', '.join(rolesVálidos.keys())}")
        
    except Exception as e:
      print(f"ERROR DE TIPEO {e}")
  
  #Iniciar Sesión
  botón_login = tk.Button(ventana, text="Iniciar Sesión", width=15)
  botón_login.config(fg="black", bg=colores["gris"], font=("Arial", 15), cursor='hand2', activebackground=colores["gris"], command=validarRol)
  botón_login.grid(row=2, column=0, pady=30, sticky="s")
  
  return ventana

def mostrar_pestañas(ventana, permiso):
  ventana.geometry("350x200")
  global tablaAlumno, tablaAsistencia, tablaCarrera, tablaMateria, tablaMateriaProfesor, tablaProfesor, tablaNota, color_padre
  
  for widget in ventana.winfo_children():
    widget.destroy()
  
  estilo = ttk.Style()
  estilo.theme_use("clam")
  estilo.configure("TNotebook.Tab", font=("Arial", 8))
  
  notebook = ttk.Notebook(ventana)
  notebook.pack(expand=True, fill="both")
  
  pestañas = {
    "alumno": ("Alumno", lambda: tk.Frame(notebook)),
    "asistencia": ("Asistencia", lambda: tk.Frame(notebook)),
    "carrera": ("Carrera", lambda: tk.Frame(notebook)),
    "materia": ("Materia", lambda: tk.Frame(notebook)),
    "enseñanza": ("Enseñanza", lambda: tk.Frame(notebook)),
    "profesor": ("Profesor", lambda: tk.Frame(notebook)),
    "nota": ("Nota", lambda: tk.Frame(notebook))
  }
  
  for clave, (texto, frame) in pestañas.items():
    if clave in permiso:
      marco = frame()
      notebook.add(marco, text=texto)
      
      match clave:
        case "alumno":
          tablaAlumno = marco
        case "asistencia":
          tablaAsistencia = marco
        case "carrera":
          tablaCarrera = marco
        case "materia":
          tablaMateria = marco
        case "enseñanza":
          tablaMateriaProfesor = marco
        case "profesor":
          tablaProfesor = marco
        case "nota":
          tablaNota = marco
  
  notebook.carga_inicial = True
  
  def on_tab_change(event):
    if getattr(notebook, "carga_inicial", True):
      return
    pestaña = notebook.tab(notebook.select(), "text").lower()
    abrir_tablas(pestaña) 
  
  lb_obligatoriedad = tk.Label(notebook, text="* Campos obligatorios", bg=ventana.cget("bg"), font=("Arial", 8))
  lb_obligatoriedad.pack(side="bottom", pady=5)
  
  # notebook.select(tablaAlumno)
  
  notebook.bind("<<NotebookTabChanged>>", on_tab_change)
  
  ventana.after(100, setattr(notebook, "carga_inicial", False))

#En esta función deseo meter la lógica de cada ABM, entries, labels, botones del CRUD y una listBox
def abrir_tablas(nombre_de_la_tabla):
  global ventanaSecundaria, btnAgregar, btnModificar, btnEliminar, btnGuardar, btnExportarPDF, btnCancelar, btnImportar, cajasDeTexto, nombreActual
  global tabla_treeview, rbMostrar, rbOcultar, campos_por_tabla, entryBuscar, botones, acciones, var_rb
  nombreActual = nombre_de_la_tabla
  if nombre_de_la_tabla in ventanaAbierta and ventanaAbierta[nombre_de_la_tabla].winfo_exists():
    return
    
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
      ("Estado de asistencia*", "txBox_EstadoAsistencia"),
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
        ("Fecha*", "txBox_FechaHora"),
    ]
  }
  cajasDeTexto = {}
  cajasDeTexto[nombre_de_la_tabla] = [] 
      
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
  entryBuscar.bind("<KeyRelease>", lambda e: buscar_datos(nombre_de_la_tabla, tabla_treeview, entryBuscar, consultas))

  iterar_entry_y_combobox(marco_izquierdo, nombre_de_la_tabla, campos)
  
  tabla_treeview = crear_tabla_Treeview(marco_derecho, tabla=nombre_de_la_tabla)
  tabla_treeview.config(selectmode="none")

  tabla_treeview.delete(*tabla_treeview.get_children())
  
  var_rb = tk.StringVar(value="")

  rbOcultar = crear_botonesExcluyentes(marco_izquierdo, "Ocultar",var_rb, "Ocultar")
  rbOcultar.grid(row=0, column=1, sticky="n")
  rbOcultar.bind("<ButtonPress-1>", lambda e: seleccionar_encabezado(e, tabla_treeview, var_rb))
           
  rbMostrar = crear_botonesExcluyentes(marco_izquierdo, "Mostrar",var_rb, "Mostrar")
  rbMostrar.grid(row=0, column=2, sticky="n")
  rbMostrar.bind("<ButtonPress-1>", lambda e: mostrar_encabezado(tabla_treeview, alias, var_rb))
  

  crear_etiqueta(marco_izquierdo, "Orden de datos").grid(row=1, column=1, sticky="n")
  opciones = ["ASCENDENTE", "DESCENDENTE"]
  opciónSeleccionado = tk.StringVar(value=opciones[0])
    
  orden = ttk.Combobox(marco_izquierdo, textvariable=opciónSeleccionado,state="readonly", values=opciones)
  opciónSeleccionado.get()
  orden.grid(row=1, column=2, sticky="n", pady=5)

  for col in tabla_treeview["columns"]:
    nombre_legible = alias.get(col, col)
    tabla_treeview.heading(col, text=nombre_legible, command=lambda campo=col: ordenar_datos(nombre_de_la_tabla, tabla_treeview, campo, opciónSeleccionado.get()))
    tabla_treeview.bind("<<TreeviewSelect>>", lambda e: mostrar_registro(nombre_de_la_tabla, tabla_treeview, cajasDeTexto))
  
 
  btnCancelar = crear_botón(marco_izquierdo, "Cancelar", imágenes_por_botón["cancelar"], lambda: deshabilitar(tabla_treeview), "disabled")
  btnCancelar.grid(row=0, column=0, pady=10, padx=0, sticky="ew")
  
  btnAgregar = crear_botón(marco_izquierdo, "Agregar",imágenes_por_botón["agregar"], lambda: insertar(tabla_treeview), "normal")
  btnAgregar.grid(row=1, column=0, pady=10, padx=0, sticky="ew")
  
  btnModificar = crear_botón(marco_izquierdo, "Modificar",imágenes_por_botón["modificar"], lambda: modificar_datos(nombre_de_la_tabla, cajasDeTexto, campos_en_db, tabla_treeview), "disabled")
  btnModificar.grid(row=2, column=0, pady=10, padx=0, sticky="ew")
  
  btnEliminar = crear_botón(marco_izquierdo, "Eliminar",imágenes_por_botón["eliminar"], lambda: eliminar_datos(nombre_de_la_tabla, cajasDeTexto, tabla_treeview), "disabled")
  btnEliminar.grid(row=3, column=0, pady=10, padx=0, sticky="ew")
  
  btnGuardar = crear_botón(marco_izquierdo, "Guardar",imágenes_por_botón["guardar"], lambda: guardar_datos(nombre_de_la_tabla, tabla_treeview, cajasDeTexto, campos_en_db), "disabled")
  btnGuardar.grid(row=4, column=0, pady=10, padx=0, sticky="ew")
  
  btnImportar = crear_botón(marco_izquierdo,"Importar Registros", imágenes_por_botón["importar"], lambda: None, "disabled")
  btnImportar.grid(row=5, column=0, pady=10, padx=0, sticky="ew")
  
  btnExportarPDF = crear_botón(marco_izquierdo, "Exportar", imágenes_por_botón["exportar"], lambda: exportar_en_PDF(nombre_de_la_tabla, tabla_treeview), "disabled")
  btnExportarPDF.grid(row=6, column=0, pady=10, padx=0, sticky="ew")

  botones = [
    btnCancelar,
    btnAgregar,
    btnModificar,
    btnEliminar,
    btnGuardar,
    btnImportar,
    btnExportarPDF
  ]

  acciones = {
      "Cancelar": partial(deshabilitar, tabla_treeview),
      "Agregar": partial(insertar, tabla_treeview),
      "Modificar": partial(modificar_datos, nombreActual, cajasDeTexto, campos_en_db, tabla_treeview),
      "Eliminar": partial(eliminar_datos, nombreActual, cajasDeTexto, tabla_treeview),
      "Guardar": partial(guardar_datos, nombreActual, tabla_treeview),
      "Exportar": partial(exportar_en_PDF, nombreActual, tabla_treeview),
      "Mostrar": partial(mostrar_registro, nombreActual, tabla_treeview, cajasDeTexto)
  }
  # --- BINDEOS DE EVENTOS ---
  
  ventanaSecundaria.bind("<Key>", lambda e: mover_con_flechas(tabla_treeview, cajasDeTexto[nombre_de_la_tabla], botones, acciones, e))
  
# --- INICIO DEL SISTEMA ---
pantallaLogin()
mi_ventana.protocol("WM_DELETE_WINDOW", lambda: cerrar_abm(mi_ventana))
mi_ventana.mainloop()