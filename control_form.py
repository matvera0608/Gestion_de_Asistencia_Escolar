""" SE LLAMA control_form.py. Crear variables para tener como referencia es bueno porque evita el famoso mensaje que no está definido."""
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
entryBuscar = None
permitir_insercion = True
entry = None
ventanaSecundaria = None


# --- FUNCIONES DE CONTROL DE HABILITACIÓN ---

def restaurar_botonera():
     btnAgregar.config(state="normal")
     btnModificar.config(state="disabled")
     btnEliminar.config(state="normal")
     btnGuardar.config(state="disabled")
     btnCancelar.config(state="normal")
     
     global modo_actual
     modo_actual = None

def habilitar(nombre_de_la_tabla, treeview, cajasDeTexto):
     treeview.delete(*treeview.get_children())
     if not nombre_de_la_tabla:
        return
   
     datos = fun.consultar_tabla(nombre_de_la_tabla)
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


def deshabilitar(nombre_de_la_tabla, treeview):
     global permitir_insercion
  
     if ventanaSecundaria:
          fun.mostrar_aviso(ventanaSecundaria, "")

     if not permitir_insercion:
          return
     treeview.delete(*treeview.get_children())

    
     treeview.bind("<Button-1>", lambda e: "break")
     treeview.bind("<Key>", lambda e: "break")
     treeview.selection_remove(treeview.selection())
     entryBuscar.config(state="readonly")
     for entry in ele.cajasDeTexto.get(nombre_de_la_tabla, []):
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