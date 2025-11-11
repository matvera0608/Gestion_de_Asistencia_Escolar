import tkinter as tk
from tkinter import ttk
from Elementos import *
from funciones_necesarias import *


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
  ancho_mín = 150
  
  for columna in columnas:
    nombre_legible = alias.get(columna, columna)
    tabla_Treeview.heading(columna, anchor="center", text=nombre_legible)
    tabla_Treeview.column(columna, anchor="center",width=ancho_mín, minwidth=ancho_mín, stretch=False)
  
  def reconfigurar_ancho_columnas(event):
    ancho_disponible = event.width
    num_columnas = len(columnas)
    
    if ancho_disponible > (num_columnas * ancho_mín):
        nuevo_ancho = ancho_disponible // num_columnas
        for col in columnas:
          tabla_Treeview.column(col, width=nuevo_ancho)
    else:
      pass
            
            
  barraVertical = tk.Scrollbar(frame_tabla, orient="vertical", command=tabla_Treeview.yview)
  barraHorizontal = tk.Scrollbar(frame_tabla, orient="horizontal", command=tabla_Treeview.xview)

  tabla_Treeview.configure(yscrollcommand=barraVertical.set, xscrollcommand=barraHorizontal.set)

  tabla_Treeview.grid(row=0, column=0, sticky="nsew")
  barraVertical.grid(row=0, column=1, sticky="ns")
  barraHorizontal.grid(row=1, column=0, sticky="ew")
  
  frame_tabla.grid_rowconfigure(0, weight=1)
  frame_tabla.grid_columnconfigure(0, weight=1)
  frame_tabla.bind("<Configure>", reconfigurar_ancho_columnas)
  
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


def crear_widgets(marco, nombre_de_la_tabla, campos, ventana):
  listaDesplegable = {}
  cajasDeTexto.setdefault(nombre_de_la_tabla, [])
  listaDesplegable.setdefault(nombre_de_la_tabla, [])
  
  mapa_de_tipos_de_datos = {
    "txBox_Fecha":"fecha",
    "txBox_Hora":"hora",
    "txBox_Nombre":"nombre",
    "txBox_Duración": "duración",
    "txBox_Valor":"nota"
  } 
  
  for i, (texto_etiqueta, nombre_Interno) in enumerate(campos):
    crear_etiqueta(marco, texto_etiqueta).grid(row=i + 2, column=1, sticky="w", pady=5)
    combo = crear_listaDesp(marco, 30)
    combo.widget_interno = nombre_Interno
    combo.grid(row=i + 2, column=2, sticky="ew", pady=5)
    listaDesplegable[nombre_de_la_tabla].append(combo)
    cajasDeTexto[nombre_de_la_tabla].append(combo)
   
  cargar_datos_en_Combobox(nombre_de_la_tabla, listaDesplegable[nombre_de_la_tabla])  
  for tabla, campos in campos_por_tabla.items():
    for etiqueta, widget_interno in campos:
      widget = next((w for w in cajasDeTexto.get(tabla, []) if getattr(w, "widget_interno", "") == widget_interno), None)
      if widget and widget.winfo_exists():
        tipo = next((t for prefijo, t in mapa_de_tipos_de_datos.items() if widget_interno.startswith(prefijo)), None)
        if tipo:
          aplicar_validación(widget, ventana, tipo)

def configurar_ciertos_comboboxes(cbBox_tabla):
  for etiqueta, widget_interno in campos_por_tabla.get(cbBox_tabla, []):
    try:
      for widget in cajasDeTexto.get(cbBox_tabla, []):
        if not widget.winfo_exists():
            continue
        
        if getattr(widget, "widget_interno", "") == widget_interno:
          if widget_interno.startswith("cbBox_"):
            if cbBox_tabla.lower() == "asistencia" and widget_interno.startswith("cbBox_Estado"):
              widget["values"] = ["presente", "ausente"]
              widget.set("presente")
            widget.config(state="readonly")
          elif widget_interno.startswith("txBox_"):
            widget.config(state="normal")
    except Exception as e:
      print(f"Error configurando {widget}: {e}")
      

def cerrar_abm(ventana):
  try:
    for widget in list(ventana.winfo_children()):
      try:
        widget.unbind("<Button-1>")
        widget.unbind("<Key>")
      except Exception:
        pass
  except Exception:
    pass

  global permitir_inserción
  permitir_inserción = False

  try:
    ventana.destroy()
  except Exception:
    pass