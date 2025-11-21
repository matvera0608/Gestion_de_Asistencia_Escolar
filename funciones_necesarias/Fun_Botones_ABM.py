from .Operaciones_ABM import *
from control_form import *

modo_actual = None

def nuevo_registro(nombre_de_la_tabla, treeview): #Se puso un parámetro de treeview, porque habilitar y deshabilitar si o si usa un argumento
    global modo_actual
    modo_actual = "nuevo"
    habilitar(nombre_de_la_tabla, treeview, cajasDeTexto)
    
def editar_registro(nombre_de_la_tabla, treeview):
    global modo_actual
    modo_actual = "editar"
    habilitar(nombre_de_la_tabla, treeview, cajasDeTexto)

 
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
    deshabilitar(nombre_de_la_tabla, treeview) #Acá deshabilita toda la operación