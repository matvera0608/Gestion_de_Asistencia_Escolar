from .Operaciones_ABM import *
import control_form as cf

modo_actual = None


def nuevo_registro(nombre_de_la_tabla, treeview): #Se puso un parámetro de treeview, porque habilitar y deshabilitar si o si usa un argumento
    global modo_actual
    modo_actual = "nuevo"
    
    cf.restaurar_botonera()
    cf.habilitar(nombre_de_la_tabla, treeview, cajasDeTexto)
    cf.btnAgregar.config(state="disabled")
    cf.btnGuardar.config(state="normal")
    cf.btnCancelar.config(state="normal")
    cf.btnModificar.config(state="normal")
    cf.btnEliminar.config(state="normal")
 
def editar_registro(nombre_de_la_tabla, treeview):
    global modo_actual
    modo_actual = "editar"
    
    cf.restaurar_botonera()
    cf.habilitar(nombre_de_la_tabla, treeview, cajasDeTexto)
    cf.btnModificar.config(state="disabled")
    cf.btnGuardar.config(state="normal")
    cf.btnCancelar.config(state="normal")
    cf.btnAgregar.config(state="normal")
    cf.btnEliminar.config(state="normal")
    
 
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
    cf.deshabilitar(nombre_de_la_tabla, treeview) #Acá deshabilita toda la operación