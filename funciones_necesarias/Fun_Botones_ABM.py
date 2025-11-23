from .Operaciones_ABM import *
import control_form as cf

modo_actual = None


def nuevo_registro(nombre_de_la_tabla, treeview): #Se puso un parámetro de treeview, porque habilitar y deshabilitar si o si usa un argumento
    """Prepara la interfaz para agregar un nuevo registro."""
    global modo_actual
    modo_actual = "nuevo"
    
    cf.habilitar(nombre_de_la_tabla, treeview, cajasDeTexto)
    if not treeview.winfo_exists():
        print("Advertencia: el Treeview no está disponible.")
        return
    cf.restaurar_botonera()
    cf.btnAgregar.config(state="disabled")
 
def editar_registro(nombre_de_la_tabla, treeview):
    global modo_actual
    modo_actual = "editar"
    
    cf.habilitar(nombre_de_la_tabla, treeview, cajasDeTexto)
    if not treeview.winfo_exists():
        print("Advertencia: el Treeview no está disponible.")
        return
    cf.restaurar_botonera()
    cf.btnModificar.config(state="disabled")
 
def guardar_registros(nombre_de_la_tabla, cajasDeTexto, campos_db, treeview, ventana):
    global modo_actual
    if modo_actual == "nuevo":
        insertar_datos(nombre_de_la_tabla, cajasDeTexto, campos_db, treeview, ventana)
    elif modo_actual == "editar":
        modificar_datos(nombre_de_la_tabla, cajasDeTexto, campos_db, treeview, ventana)
    else:
        mostrar_aviso(ventana, "No hay operación activa", colores["rojo_error"], 10)
        return
    modo_actual = None
    cf.restaurar_botonera()