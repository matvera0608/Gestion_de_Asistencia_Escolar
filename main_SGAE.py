import elementos_necesarios.Creacion_de_widgets as wid
import elementos_necesarios.Disenho as dis
import elementos_necesarios.Elementos as ele

import funciones_necesarias.Operaciones_ABM as abm
import funciones_necesarias.Fun_adicionales as fun
import funciones_necesarias.Fun_Botones_ABM as btn_abm

from Eventos import *
import control_form as cf
import os
import tkinter as tk
from tkinter import ttk
from functools import partial

# --- EJECUCIÓN DE LA VENTANA PRINCIPAL ---

mi_ventana = tk.Tk()

íconos_por_tabla = {
  "alumno": os.path.join(ele.ruta_raíz_proyecto, "imágenes", "alumno.ico"),
  "asistencia": os.path.join(ele.ruta_raíz_proyecto, "imágenes", "asistencia.ico"),
  "carrera": os.path.join(ele.ruta_raíz_proyecto, "imágenes", "carrera.ico"),
  "materia": os.path.join(ele.ruta_raíz_proyecto, "imágenes", "materia.ico"),
  "enseñanza": os.path.join(ele.ruta_raíz_proyecto, "imágenes", "enseñanza.ico"),
  "profesor": os.path.join(ele.ruta_raíz_proyecto, "imágenes", "profesor.ico"),
  "nota": os.path.join(ele.ruta_raíz_proyecto, "imágenes", "nota.ico")
}

imágenes_por_botón = {
  "iniciar_sesion": ele.cargar_imagen("botones", "iniciar_sesion.png"),
  "regresar_al_menu_principal": ele.cargar_imagen("botones", "regresar_al_menu_principal.png"),
  "cancelar": ele.cargar_imagen("botones", "cancelar.png"),
  "agregar": ele.cargar_imagen("botones", "agregar.png"),
  "modificar": ele.cargar_imagen("botones", "modificar.png"),
  "eliminar": ele.cargar_imagen("botones", "eliminar.png"),
  "guardar": ele.cargar_imagen("botones", "guardar.png"),
  "importar": ele.cargar_imagen("botones", "importar_desde.png"),
  "exportar": ele.cargar_imagen("botones", "exportar_como_pdf.png"),
}

def pantallaLogin():
  ventana = mi_ventana
  ventana.title("Sistema Gestor de Asistencias Escolares")
  ventana.geometry("400x200")
  ventana.configure(bg=dis.colores["blanco"])
  ventana.iconbitmap(ele.ícono)
  ventana.resizable(width=False, height=False)
  ventana.grid_columnconfigure(0, weight=1)
  ventana.grid_rowconfigure(2, weight=1)

  estilo = ttk.Style()
  estilo.theme_use("clam") #clam es el mejor tema para personalizar
  estilo.configure("Boton.TButton", font=("Arial", 10, "bold"), foreground=dis.colores["blanco"], background=dis.colores["celeste_azulado"], padding=5)
  estilo.map("Boton.TButton", background=[("active", dis.colores["celeste_resaltado"])])

  #Etiqueta para rol
  label_usuario_rol = tk.Label(ventana, text="ROL", bg=dis.colores["blanco"], fg=dis.colores["negro"], font=("Arial", 15, "bold"))
  label_usuario_rol.grid(row=0, column=0, pady=(20, 5), sticky="n")
  
  rolesVálidos = {
    "docente": ("alumno", "asistencia", "materia", "nota"),
    "personal administrativo": ("carrera", "profesor", "materia", "enseñanza"),
    }
  
  rol_orden_logico = [
    "docente",
    "personal administrativo"
  ]
  #Entry para el usuario
  rol = rol_orden_logico
  
  cbBox_usuario = ttk.Combobox(ventana, values=rol, state="readonly", width=20, font=("Arial", 15))
  cbBox_usuario.set("Seleecione el rol")
  cbBox_usuario.grid(row=1, column=0, sticky="n")
  
  
  def iniciar_sesion():
    selección_de_rol = cbBox_usuario.get()
    permiso = rolesVálidos.get(selección_de_rol)
    
    if not permiso:
      wid.crear_etiqueta(ventana, "ROL INVÁLIDO", dis.colores["rojo_error"]).grid(row=2, column=0, pady=10, sticky="n")
      return
    mostrar_pestañas(ventana, permiso)
 
  #Iniciar Sesión
  botón_login = wid.crear_boton(ventana, "Iniciar", imágenes_por_botón["iniciar_sesion"], iniciar_sesion)
  botón_login.config(state="normal")
  botón_login.grid(row=3, column=0, sticky="s")
  
  return ventana

def mostrar_pestañas(ventana, permiso):
  ventana.geometry("350x200")
  global tablaAlumno, tablaAsistencia, tablaCarrera, tablaMateria, tablaMateriaProfesor, tablaProfesor, tablaNota
  
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
  
  def regresar():
    for widget in mi_ventana.winfo_children():
      widget.destroy()
    pantallaLogin()
  
  
  botón_regresar = wid.crear_boton(notebook, "Regresar", imágenes_por_botón["regresar_al_menu_principal"], lambda: regresar())
  botón_regresar.config(state="normal")
  botón_regresar.pack(side="top", pady=50)
  
  lb_obligatoriedad = tk.Label(notebook, text="* Campos obligatorios", bg=ventana.cget("bg"), font=("Arial", 8))
  lb_obligatoriedad.pack(side="bottom", pady=5)
  
  notebook.bind("<<NotebookTabChanged>>", on_tab_change)
  
  ventana.after(1000, setattr(notebook, "carga_inicial", False))

#Aquí se encontrará los eventos en esta función, acciones es un diccionario que sirve para eventuar luego.
def abrir_tablas(nombre_de_la_tabla):
    
  # Destruir ventana anterior si existe y limpiar referencias
  if "ventanaSecundaria" in globals() and ventanaSecundaria.winfo_exists():
    ventanaSecundaria.destroy()
  
  # Limpiar referencias antiguas de widgets destruidos DESPUÉS de destruir la ventana
  if nombre_de_la_tabla in ele.cajasDeTexto:
    ele.cajasDeTexto[nombre_de_la_tabla] = []


  ventanaSecundaria = tk.Toplevel()
  ventanaSecundaria.geometry("900x600")
  ventanaSecundaria.title(f"{nombre_de_la_tabla.upper()}")
  ventanaSecundaria.configure(bg=dis.colores["azul_claro"])
  
  ele.ventanaAbierta[nombre_de_la_tabla] = ventanaSecundaria
  
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

  marco_izquierdo = tk.Frame(ventanaSecundaria, bg=dis.colores["azul_claro"], padx=15, pady=15)
  marco_izquierdo.grid(row=0, column=0, sticky="nsew")

  marco_derecho = tk.Frame(ventanaSecundaria, bg=dis.colores["azul_claro"], padx=15, pady=15)
  marco_derecho.grid(row=0, column=1, sticky="nsew")

  marco_izquierdo.grid_columnconfigure(0, weight=0)
  marco_izquierdo.grid_columnconfigure(1, weight=1)
  
  marco_derecho.grid_columnconfigure(0, weight=1)
  marco_derecho.grid_rowconfigure(0, weight=1)

  
  # --- Creamos un estilo global ---
  estilo = ttk.Style()
  estilo.theme_use("clam") #clam es el mejor tema para personalizar
  estilo.configure("Boton.TButton", font=("Arial", 10, "bold"), foreground=dis.colores["blanco"], background=dis.colores["celeste_azulado"], padding=10)
  estilo.configure("Radiobutton.TRadiobutton", font=("Arial", 10, "bold"), foreground=dis.colores["blanco"], background=dis.colores["azul_claro"])
  estilo.configure("Entrada.TEntry", padding=5, relief="flat", foreground=dis.colores["negro"], fieldbackground=dis.colores["blanco"])
  estilo.map("Boton.TButton", background=[("active", dis.colores["celeste_resaltado"])])

  campos = ele.widgets_para_tablas.get(nombre_de_la_tabla, None)
  if not campos:
    return
  
  wid.crear_etiqueta(ventanaSecundaria, "Buscar").grid(row=2, column=0)
  cf.entryBuscar = wid.crear_entrada(ventanaSecundaria, 40)
  cf.entryBuscar.grid(row=3, column=0, sticky="ew")
  cf.entryBuscar.bind("<KeyRelease>", lambda e: fun.buscar_datos(nombre_de_la_tabla, treeview, cf.entryBuscar, ele.consultas))

  wid.crear_widgets(marco_izquierdo, nombre_de_la_tabla, campos, mi_ventana)
  
  # --- Cargar y mostrar imagen de la tabla en marco_derecho ---
  imagen_busqueda = ele.cargar_imagen("","busqueda.png")
  if imagen_busqueda:
    lbimagen = tk.Label(ventanaSecundaria, image=imagen_busqueda, bg=dis.colores["azul_claro"])
    lbimagen.image = imagen_busqueda 
    lbimagen.grid(row=3, column=1, sticky="w", padx=(5, 0))
  
  treeview = wid.crear_Treeview(marco_derecho, tabla=nombre_de_la_tabla)
  treeview.config(selectmode="none")
  treeview.delete(*treeview.get_children())
  
  wid.crear_etiqueta(marco_izquierdo, "Orden de datos").grid(row=0, column=1, sticky="n")
  opciones = ["ASCENDENTE", "DESCENDENTE"]
  opciónSeleccionado = tk.StringVar(value=opciones[0])
    
  orden = ttk.Combobox(marco_izquierdo, textvariable=opciónSeleccionado, state="readonly", values=opciones)
  orden.grid(row=0, column=2, sticky="n", pady=5)

  for col in treeview["columns"]:
    nombre_legible = ele.alias.get(col, col)
    treeview.heading(col, text=nombre_legible, command=lambda campo=col: ele.manejar_click_columna(campo, opciónSeleccionado.get(), nombre_de_la_tabla, treeview, fun.ordenar_datos, ele.consultas))
    treeview.bind("<<TreeviewSelect>>", lambda e: fun.mostrar_registro(nombre_de_la_tabla, treeview, ele.cajasDeTexto))
  
  
  
  cf.btnCancelar = wid.crear_boton(marco_izquierdo, "Cancelar", imágenes_por_botón["cancelar"], lambda: btn_abm.limpiar_TODO(nombre_de_la_tabla, treeview))
  cf.btnCancelar.grid(row=0, column=0, pady=10, padx=0, sticky="ew")
  
  cf.btnAgregar = wid.crear_boton(marco_izquierdo, "Agregar",imágenes_por_botón["agregar"], lambda: btn_abm.nuevo_registro(nombre_de_la_tabla, treeview))
  cf.btnAgregar.grid(row=1, column=0, pady=10, padx=0, sticky="ew")
  
  cf.btnModificar = wid.crear_boton(marco_izquierdo, "Modificar",imágenes_por_botón["modificar"], lambda: btn_abm.editar_registro(nombre_de_la_tabla, treeview))
  cf.btnModificar.grid(row=2, column=0, pady=10, padx=0, sticky="ew")
  
  cf.btnEliminar = wid.crear_boton(marco_izquierdo, "Eliminar",imágenes_por_botón["eliminar"], lambda: abm.eliminar_datos(nombre_de_la_tabla, ele.cajasDeTexto, treeview, ventanaSecundaria))
  cf.btnEliminar.grid(row=3, column=0, pady=10, padx=0, sticky="ew")
  
  cf.btnGuardar = wid.crear_boton(marco_izquierdo, "Guardar",imágenes_por_botón["guardar"], lambda: btn_abm.guardar_registros(nombre_de_la_tabla, ele.cajasDeTexto, ele.campos_en_db, treeview, ventanaSecundaria))
  cf.btnGuardar.grid(row=4, column=0, pady=10, padx=0, sticky="ew")
  
  cf.btnImportar = wid.crear_boton(marco_izquierdo,"Importar", imágenes_por_botón["importar"], lambda: abm.importar_datos(nombre_de_la_tabla, treeview, ventanaSecundaria))
  cf.btnImportar.grid(row=5, column=0, pady=10, padx=0, sticky="ew")
  
  cf.btnExportarPDF = wid.crear_boton(marco_izquierdo, "Exportar", imágenes_por_botón["exportar"], lambda: abm.exportar_en_PDF(nombre_de_la_tabla, treeview, ventanaSecundaria))
  cf.btnExportarPDF.grid(row=6, column=0, pady=10, padx=0, sticky="ew")

  botones = [
    cf.btnCancelar,
    cf.btnAgregar,
    cf.btnModificar,
    cf.btnEliminar,
    cf.btnGuardar,
    cf.btnImportar,
    cf.btnExportarPDF
  ]

  acciones = {
    "Cancelar": partial(btn_abm.limpiar_TODO, nombre_de_la_tabla, treeview),
    "Agregar": partial(btn_abm.nuevo_registro,nombre_de_la_tabla, treeview),
    "Modificar": partial(btn_abm.editar_registro,nombre_de_la_tabla, treeview),
    "Guardar": partial(btn_abm.guardar_registros, nombre_de_la_tabla, ele.cajasDeTexto, ele.campos_en_db, treeview, ventanaSecundaria),
    "Eliminar": partial(abm.eliminar_datos, nombre_de_la_tabla, ele.cajasDeTexto, treeview, ventanaSecundaria),
    "Importar": partial(abm.importar_datos, nombre_de_la_tabla, treeview, ventanaSecundaria),
    "Exportar": partial(abm.exportar_en_PDF, nombre_de_la_tabla, treeview, ventanaSecundaria),
    "Mostrar": partial(fun.mostrar_registro, nombre_de_la_tabla, treeview, ele.cajasDeTexto)
  }
  
  cf.restaurar_botonera("disabled")
  cf.btnAgregar.config(state="normal")
  
  # --- BINDEOS DE EVENTOS ---
  
  ventanaSecundaria.bind("<Key>", lambda e: mover_con_flechas(treeview, ele.cajasDeTexto[nombre_de_la_tabla], botones, acciones, e))
  ventanaSecundaria.bind("<Control-i>", lambda e: (acciones["Importar"]()))
  ventanaSecundaria.bind("<Control-e>", lambda e: (acciones["Exportar"]()))
  ventanaSecundaria.bind("<Alt-a>", lambda e: (acciones["Guardar"]()))
  ventanaSecundaria.bind("<Control-Key-BackSpace>", lambda e: (acciones["Eliminar"]()))

# --- INICIO DEL SISTEMA ---
pantallaLogin()
mi_ventana.protocol("WM_DELETE_WINDOW", lambda: wid.cerrar_abm(mi_ventana))
mi_ventana.mainloop()

os.environ["TK_SILENCE_DEPRECATION"] = "1"