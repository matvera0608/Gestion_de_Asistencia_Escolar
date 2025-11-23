import tkinter as tk
import funciones_necesarias.Fun_adicionales as fun #No sé si está bien que importe módulos de otros archivos
import elementos_necesarios.Creacion_de_widgets as wid
import elementos_necesarios.Elementos as ele

# --- REFERENCIAS GLOBALES A WIDGETS ---
btnAgregar = None
btnModificar = None
btnEliminar = None
btnGuardar = None
btnExportarPDF = None
btnImportar = None
btnCancelar = None
ventanaSecundaria = None
entryBuscar = None


# --- FUNCIONES DE CONTROL DE HABILITACIÓN ---

def restaurar_botonera():
     # Estado por defecto: permitir agregar/modificar/eliminar, guardar deshabilitado
     estados_defecto = {
          'btnAgregar': 'normal',
          'btnModificar': 'normal',
          'btnEliminar': 'normal',
          'btnGuardar': 'disabled',
          'btnCancelar': 'normal',
          'btnImportar': 'normal',
          'btnExportar': 'normal'
     }
     aplicar_estados_botonera(estados_defecto)

     global modo_actual
     modo_actual = None


def aplicar_estados_botonera(estados: dict):
   
     mapping = {
          'btnAgregar': btnAgregar,
          'btnModificar': btnModificar,
          'btnEliminar': btnEliminar,
          'btnGuardar': btnGuardar,
          'btnCancelar': btnCancelar,
          'btnImportar': btnImportar,
          'btnExportar': btnExportarPDF
     }
     for nombre, estado in estados.items():
          widget = mapping.get(nombre)
          if widget is None:
               continue
          try:
               widget.config(state=estado)
          except Exception:
               pass

def habilitar(nombre_de_la_tabla, treeview, cajasDeTexto):
     treeview.delete(*treeview.get_children())
     if not nombre_de_la_tabla:
        return
   
     datos = fun.consultar_tabla(nombre_de_la_tabla)
     #Este for crea el diseño zebra rows de la Treeview
     for índice, fila in enumerate(datos):
          id_val = fila[0]
          valores_visibles = fila[1:]
          tag = "par" if índice % 2 == 0 else "impar"
          treeview.insert("", "end", iid=str(id_val), values=valores_visibles, tags=(tag,))

     entryBuscar.config(state="normal")
     treeview.config(selectmode="browse")
     treeview.unbind("<Button-1>")
     treeview.unbind("<Key>")
     treeview.bind("<<TreeviewSelect>>", lambda e: fun.mostrar_registro(nombre_de_la_tabla, treeview, cajasDeTexto))

     wid.configurar_ciertos_comboboxes(nombre_de_la_tabla)

def deshabilitar(nombre_de_la_tabla, treeview, cajasDeTexto):
     treeview.delete(*treeview.get_children())

     treeview.bind("<Button-1>", lambda e: "break")
     treeview.bind("<Key>", lambda e: "break")
     
     treeview.selection_remove(treeview.selection())
     entryBuscar.config(state="readonly")
     
     
     for entry in cajasDeTexto.get(nombre_de_la_tabla, []):
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
               entry.set("")
               pass
          try:
               entry.config(state="readonly")
          except Exception:
               pass