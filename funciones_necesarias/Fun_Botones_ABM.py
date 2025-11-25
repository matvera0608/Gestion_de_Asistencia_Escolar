from .Operaciones_ABM import *
from .Fun_adicionales import *
import control_form as cf

def preparar_modo(modo, nombre_de_la_tabla, treeview, boton_a_deshabilitar):
    global modo_actual
    modo_actual = modo
    
    cf.habilitar(nombre_de_la_tabla, treeview, cajasDeTexto)
    if not treeview.winfo_exists():
        print(f"Advertencia: el Treeview no está disponible en modo '{modo}'.")
        return
        
    cf.restaurar_botonera("normal")
    # Deshabilita el botón pasado como argumento (ej. cf.btnAgregar o cf.btnModificar)
    boton_a_deshabilitar.config(state="disabled")
    
def nuevo_registro(nombre_de_la_tabla, treeview): #Se puso un parámetro de treeview, porque habilitar y deshabilitar si o si usa un argumento
    """Prepara la interfaz para agregar un nuevo registro."""
    preparar_modo("nuevo", nombre_de_la_tabla, treeview, cf.btnAgregar)
    refrescar_Treeview(nombre_de_la_tabla, treeview, consultas)
 
def editar_registro(nombre_de_la_tabla, treeview):
    """Prepara la interfaz para modificar un registro existente."""
    preparar_modo("editar", nombre_de_la_tabla, treeview, cf.btnModificar)
    refrescar_Treeview(nombre_de_la_tabla, treeview, consultas)
    
def guardar_registros(nombre_de_la_tabla, cajasDeTexto, campos_db, treeview, ventana):
    global modo_actual
    if modo_actual == "nuevo":
        insertar_datos(nombre_de_la_tabla, cajasDeTexto, campos_db, treeview, ventana)
    elif modo_actual == "editar":
        modificar_datos(nombre_de_la_tabla, cajasDeTexto, campos_db, treeview, ventana)
    else:
        mostrar_aviso(ventana, "No hay operación activa", colores["rojo_error"], 10)
        return
    cf.btnGuardar.config(state="disabled")
    
def limpiar_TODO(nombre_de_la_tabla, treeview):
    cf.restaurar_botonera("disabled")
    cf.btnAgregar.config(state="normal")
    cf.deshabilitar(nombre_de_la_tabla, treeview, cajasDeTexto)