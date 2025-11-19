from funciones_necesarias import *
from Eventos import *
from Elementos import *
from Creacion_de_widgets import *
import os
import tkinter as tk
from tkinter import ttk
from functools import partial

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
  
  entryBuscar.config(state="normal")
  treeview.config(selectmode="browse")
  treeview.unbind("<Button-1>")
  treeview.unbind("<Key>")
  treeview.bind("<<TreeviewSelect>>", lambda e: mostrar_registro(nombreActual, tabla_treeview, cajasDeTexto))
  
  configurar_ciertos_comboboxes(nombreActual)


def deshabilitar(treeview):
  global permitir_inserción
  
  mostrar_aviso(ventanaSecundaria, "")
  
  if not permitir_inserción:
    return
  tabla_treeview.delete(*tabla_treeview.get_children())
  
 
  for botón in [btnModificar, btnEliminar, btnExportarPDF, btnGuardar, btnImportar, btnCancelar]:
    botón.config(state="disabled")
  
  treeview.bind("<Button-1>", lambda e: "break")
  treeview.bind("<Key>", lambda e: "break")
  treeview.selection_remove(treeview.selection())
  entryBuscar.config(state="readonly")
  for entry in cajasDeTexto.get(nombreActual, []):
    if not entry.winfo_exists():
        continue
      
    tipo_de_widget = getattr(entry, "widget_interno", "")
    try:
      if tipo_de_widget.startswith("cbBox_"):
        entry.set("") 
      elif tipo_de_widget.startswith("txBox_"):
        entry.delete(0, tk.END)
      else:
        entry.delete(0, tk.END)
        
    except Exception:
        try:
          entry.set("") 
        except Exception:
            pass
    try:
        entry.config(state="readonly")
    except Exception:
        pass


def insertar_al_habilitar(tabla_treeview):
  global permitir_inserción
  if not permitir_inserción:
    return
  
  if not hasattr(tabla_treeview, "winfo_exists") or not tabla_treeview.winfo_exists():
    return
  
  habilitar(tabla_treeview)
  
  if any(widget.winfo_exists() and widget.get().strip() == "" for widget in cajasDeTexto.get(nombreActual, [])):
    return
  insertar_datos(nombreActual, cajasDeTexto, campos_en_db, tabla_treeview, ventanaSecundaria)

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
  "iniciar_sesion": cargar_imagen("botones", "iniciar_sesion.png"),
  "regresar_al_menu_principal": cargar_imagen("botones", "regresar_al_menu_principal.png"),
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
  ventana.title("Sistema Gestor de Asistencias Escolares")
  ventana.geometry("400x200")
  ventana.configure(bg=colores["blanco"])
  ventana.iconbitmap(ícono)
  ventana.resizable(width=False, height=False)
  ventana.grid_columnconfigure(0, weight=1)
  ventana.grid_rowconfigure(2, weight=1)

  estilo = ttk.Style()
  estilo.theme_use("clam") #clam es el mejor tema para personalizar
  estilo.configure("Boton.TButton", font=("Arial", 10, "bold"), foreground=colores["blanco"], background=colores["celeste_azulado"], padding=5)
  estilo.map("Boton.TButton", background=[("active", colores["celeste_resaltado"])])

  #Etiqueta para rol
  label_usuario_rol = tk.Label(ventana, text="ROL", bg=colores["blanco"], fg=colores["negro"], font=("Arial", 15, "bold"))
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
      crear_etiqueta(ventana, "ROL INVÁLIDO", colores["rojo_error"]).grid(row=2, column=0, pady=10, sticky="n")
      return
    mostrar_pestañas(ventana, permiso)
 
  #Iniciar Sesión
  botón_login = crear_botón(ventana, "Iniciar", imágenes_por_botón["iniciar_sesion"], iniciar_sesion, "normal")
  botón_login.grid(row=3, column=0, sticky="s")
  
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
  
  def regresar():
    for widget in mi_ventana.winfo_children():
      widget.destroy()
    pantallaLogin()
  
  
  botón_regresar = crear_botón(notebook, "Regresar", imágenes_por_botón["regresar_al_menu_principal"], lambda: regresar(), "normal")
  botón_regresar.pack(side="top", pady=50)
  
  lb_obligatoriedad = tk.Label(notebook, text="* Campos obligatorios", bg=ventana.cget("bg"), font=("Arial", 8))
  lb_obligatoriedad.pack(side="bottom", pady=5)
  
  notebook.bind("<<NotebookTabChanged>>", on_tab_change)
  
  ventana.after(1000, setattr(notebook, "carga_inicial", False))

def abrir_tablas(nombre_de_la_tabla):
  global ventanaSecundaria, btnAgregar, btnModificar, btnEliminar, btnGuardar, btnExportarPDF, btnCancelar, btnImportar, cajasDeTexto, nombreActual
  global tabla_treeview, campos_por_tabla, entryBuscar, botones, acciones, opciones
  global permitir_inserción
  nombreActual = nombre_de_la_tabla
  permitir_inserción = True
  
  # Destruir ventana anterior si existe y limpiar referencias
  if "ventanaSecundaria" in globals() and ventanaSecundaria.winfo_exists():
    ventanaSecundaria.destroy()
  
  # Limpiar referencias antiguas de widgets destruidos DESPUÉS de destruir la ventana
  if nombre_de_la_tabla in cajasDeTexto:
    cajasDeTexto[nombre_de_la_tabla] = []

  

  ventanaSecundaria = tk.Toplevel()
  ventanaSecundaria.geometry("900x600")
  ventanaSecundaria.title(f"{nombre_de_la_tabla.upper()}")
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

  crear_widgets(marco_izquierdo, nombre_de_la_tabla, campos, mi_ventana)
  
  tabla_treeview = crear_tabla_Treeview(marco_derecho, tabla=nombre_de_la_tabla)
  tabla_treeview.config(selectmode="none")

  tabla_treeview.delete(*tabla_treeview.get_children())
  
  crear_etiqueta(marco_izquierdo, "Orden de datos").grid(row=0, column=1, sticky="n")
  opciones = ["ASCENDENTE", "DESCENDENTE"]
  opciónSeleccionado = tk.StringVar(value=opciones[0])
    
  orden = ttk.Combobox(marco_izquierdo, textvariable=opciónSeleccionado, state="readonly", values=opciones)
  orden.grid(row=0, column=2, sticky="n", pady=5)

  for col in tabla_treeview["columns"]:
    nombre_legible = alias.get(col, col)
    tabla_treeview.heading(col, text=nombre_legible, command=lambda campo=col: manejar_click_columna(campo, opciónSeleccionado.get(), nombreActual, tabla_treeview, ordenar_datos, consultas))
    tabla_treeview.bind("<<TreeviewSelect>>", lambda e: mostrar_registro(nombre_de_la_tabla, tabla_treeview, cajasDeTexto))
  
  
  btnCancelar = crear_botón(marco_izquierdo, "Cancelar", imágenes_por_botón["cancelar"], lambda: deshabilitar(tabla_treeview), "disabled")
  btnCancelar.grid(row=0, column=0, pady=10, padx=0, sticky="ew")
  
  btnAgregar = crear_botón(marco_izquierdo, "Agregar",imágenes_por_botón["agregar"], lambda t=tabla_treeview: insertar_al_habilitar(t), "normal")
  btnAgregar.grid(row=1, column=0, pady=10, padx=0, sticky="ew")
  
  btnModificar = crear_botón(marco_izquierdo, "Modificar",imágenes_por_botón["modificar"], lambda: modificar_datos(nombre_de_la_tabla, cajasDeTexto, campos_en_db, tabla_treeview, ventanaSecundaria), "disabled")
  btnModificar.grid(row=2, column=0, pady=10, padx=0, sticky="ew")
  
  btnEliminar = crear_botón(marco_izquierdo, "Eliminar",imágenes_por_botón["eliminar"], lambda: eliminar_datos(nombre_de_la_tabla, cajasDeTexto, tabla_treeview, ventanaSecundaria), "disabled")
  btnEliminar.grid(row=3, column=0, pady=10, padx=0, sticky="ew")
  
  btnGuardar = crear_botón(marco_izquierdo, "Guardar",imágenes_por_botón["guardar"], lambda: insertar_datos(nombreActual, cajasDeTexto, campos_en_db, tabla_treeview, ventanaSecundaria), "disabled")
  btnGuardar.grid(row=4, column=0, pady=10, padx=0, sticky="ew")
  
  btnImportar = crear_botón(marco_izquierdo,"Importar", imágenes_por_botón["importar"], lambda: importar_datos(nombre_de_la_tabla, tabla_treeview), "disabled")
  btnImportar.grid(row=5, column=0, pady=10, padx=0, sticky="ew")
  
  btnExportarPDF = crear_botón(marco_izquierdo, "Exportar", imágenes_por_botón["exportar"], lambda: exportar_en_PDF(nombre_de_la_tabla, tabla_treeview, ventanaSecundaria), "disabled")
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
      "Agregar": partial(insertar_al_habilitar, tabla_treeview),
      "Modificar": partial(modificar_datos, nombreActual, cajasDeTexto, campos_en_db, tabla_treeview),
      "Eliminar": partial(eliminar_datos, nombreActual, cajasDeTexto, tabla_treeview),
      "Guardar": partial(insertar_datos, nombreActual, cajasDeTexto, tabla_treeview, campos_en_db),
      "Importar": partial(importar_datos, nombreActual, tabla_treeview),
      "Exportar": partial(exportar_en_PDF, nombreActual, tabla_treeview),
      "Mostrar": partial(mostrar_registro, nombreActual, tabla_treeview, cajasDeTexto)
  }
  # --- BINDEOS DE EVENTOS ---
  
  ventanaSecundaria.bind("<Key>", lambda e: mover_con_flechas(tabla_treeview, cajasDeTexto[nombre_de_la_tabla], botones, acciones, e))
  ventanaSecundaria.bind("<Control-i>", lambda e: (acciones["Importar"]()))
  ventanaSecundaria.bind("<Control-e>", lambda e: (acciones["Exportar"]()))
  ventanaSecundaria.bind("<Control-a>", lambda e: (acciones["Guardar"]()))


# --- INICIO DEL SISTEMA ---
pantallaLogin()
mi_ventana.protocol("WM_DELETE_WINDOW", lambda: cerrar_abm(mi_ventana))
mi_ventana.mainloop()

os.environ["TK_SILENCE_DEPRECATION"] = "1"