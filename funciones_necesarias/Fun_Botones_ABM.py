from .Operaciones_ABM import *
from SGAE_Principal import habilitar, deshabilitar

modo_actual = None

def nuevo_registro(treeview): #Se puso un parámetro de treeview, porque habilitar y deshabilitar si o si usa un argumento
    global modo_actual
    modo_actual = "nuevo"
    habilitar(treeview)
    
def editar_registro(treeview):
    global modo_actual
    modo_actual = "editar"
    habilitar(treeview)
    
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
    deshabilitar(treeview) #Acá deshabilita toda la operación