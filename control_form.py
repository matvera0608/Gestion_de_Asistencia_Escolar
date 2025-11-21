""" SE LLAMA control_form.py. Crear variables para tener como referencia es bueno porque evita el famoso mensaje que no está definido."""
import tkinter as tk
import funciones_necesarias.Fun_adicionales as fun #No sé si está bien que importe módulos de otros archivos
import elementos_necesarios.Creacion_de_widgets as wid

# --- REFERENCIAS GLOBALES A WIDGETS ---
btnAgregar = None
btnModificar = None
btnEliminar = None
btnGuardar = None
btnExportarPDF = None
btnImportar = None
btnCancelar = None
entryBuscar = None
cajasDeTexto = {}
nombreActual = ""
ventanaSecundaria = None
ventanaAbierta = {}
permitir_insercion = True
entry = None

# --- FUNCIONES DE CONTROL DE HABILITACIÓN ---
def habilitar(treeview):
     treeview.delete(*treeview.get_children())

     datos = fun.consultar_tabla(nombreActual)
     for índice, fila in enumerate(datos):
          id_val = fila[0]
          valores_visibles = fila[1:]
          tag = "par" if índice % 2 == 0 else "impar"
          treeview.insert("", "end", iid=str(id_val), values=valores_visibles, tags=(tag,))

     for botón in [btnModificar, btnEliminar, btnExportarPDF, btnGuardar, btnImportar, btnCancelar]:
          if botón is not None:
               botón.config(state="normal")

     entryBuscar.config(state="normal")
     treeview.config(selectmode="browse")
     treeview.unbind("<Button-1>")
     treeview.unbind("<Key>")
     treeview.bind("<<TreeviewSelect>>", lambda e: fun.mostrar_registro(nombreActual, treeview, cajasDeTexto))

     wid.configurar_ciertos_comboboxes(nombreActual)


def deshabilitar(treeview):
     global permitir_insercion
  
     if ventanaSecundaria:
          fun.mostrar_aviso(ventanaSecundaria, "")

     if not permitir_insercion:
          return
     treeview.delete(*treeview.get_children())


     for botón in [btnModificar, btnEliminar, btnExportarPDF, btnGuardar, btnImportar, btnCancelar]:
          if botón is not None:
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