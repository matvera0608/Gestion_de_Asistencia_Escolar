from elementos_necesarios import *
from Conexión import *
from .Fun_adicionales import *
from .Fun_Validación_SGAE import *
from .ETL import *
import tkinter as tk
from tkinter import filedialog as diálogoArchivo

def insertar_datos(nombre_de_la_tabla, cajasDeTexto, campos_db, treeview, ventana):
  datos = obtener_datos_de_Formulario(nombre_de_la_tabla, cajasDeTexto, campos_db)
  if not datos:
    return False
  
  if detectar_repeticiones_de_datos(datos, nombre_de_la_tabla):
    mostrar_aviso(ventana, "HAY REPETICIÓN DE DATOS", colores["rojo_error"], 10)
    return False
  
  if nombre_de_la_tabla == "materia":
    if verificar_horarioSalida_mayor_horarioEntrada(datos):
      mostrar_aviso(ventana, "EL HORARIO DE SALIDA NO PUEDE SER MENOR O IGUAL\n QUE EL HORARIO DE ENTRADA", colores["rojo_error"], 8)
      return False

  datos_traducidos, error = traducir_IDs(nombre_de_la_tabla, datos)
  
  if error:
    mostrar_aviso(ventana, f"❌ {error}", colores["rojo_error"], 10)
    return False
  
  if datos_traducidos is None:
    return False

  try:
    with conectar_base_de_datos() as conexión:
      campos = ', '.join(datos_traducidos.keys())
      valores = ', '.join(['%s'] * len(datos_traducidos))
      consulta = f"INSERT INTO {nombre_de_la_tabla} ({campos}) VALUES ({valores})"
      valores_sql = list(datos_traducidos.values())
      
      cursor = conexión.cursor()
      cursor.execute(consulta, tuple(valores_sql))
      conexión.commit()
      
      refrescar_Treeview(nombre_de_la_tabla, treeview)
    
      campos_oficiales = campos_en_db.get(nombre_de_la_tabla, [])
      
      for i, campo in enumerate(campos_oficiales):
        try:
          entry = cajasDeTexto[nombre_de_la_tabla][i]
        except (KeyError, IndexError):
          continue
        if not entry.winfo_exists():
          continue
        entry.delete(0, tk.END)
      mostrar_aviso(ventana, "✅ SE AGREGÓ LOS DATOS NECESARIOS", colores["verde_éxito"], 10)
      return True
  except Exception as e:
    print(f"HA OCURRIDO UN ERROR AL GUARDAR LOS DATOS: {str(e)}")
    return False

def modificar_datos(nombre_de_la_tabla, cajasDeTexto, campos_db, treeview, ventana):
  if not hasattr(treeview, "winfo_exists") or not treeview.winfo_exists():
    return False
  
  selección = treeview.selection()
  
  if not selección:
    return False
  
  
  try:
    iid = selección[0]
    idSeleccionado = int(iid)
  except ValueError:
    idSeleccionado = iid

  datos = obtener_datos_de_Formulario(nombre_de_la_tabla, cajasDeTexto, campos_db)
  if not datos:
    return False
  
  if nombre_de_la_tabla == "materia":
    if verificar_horarioSalida_mayor_horarioEntrada(datos):
      mostrar_aviso(ventana, "EL HORARIO DE SALIDA NO PUEDE SER MENOR\n QUE EL HORARIO DE ENTRADA", colores["rojo_error"], 8)
      return False
  
  datos_traducidos, error = traducir_IDs(nombre_de_la_tabla, datos)
  
  if error:
    mostrar_aviso(ventana, f"❌ {error}", colores["rojo_error"], 10)
    return False
  
  if datos_traducidos is None or not datos_traducidos:
    return False
  
  valores_sql = list(datos_traducidos.values())
  campos_sql = [f"{cam} = %s" for cam in datos_traducidos.keys()]
  set_sql = ', '.join(campos_sql)
  campoID = conseguir_campo_ID(nombre_de_la_tabla)
  consulta = f"UPDATE {nombre_de_la_tabla} SET {set_sql} WHERE {campoID} = %s"
  
  valores_sql.append(idSeleccionado)
  try:
    with conectar_base_de_datos() as conexión:
      cursor = conexión.cursor()
      cursor.execute(consulta, tuple(valores_sql))
      conexión.commit()
      
      refrescar_Treeview(nombre_de_la_tabla, treeview)
        
      campos_oficiales = campos_en_db.get(nombre_de_la_tabla, [])
    
      for i, campo in enumerate(campos_oficiales):
        try:
          entry = cajasDeTexto[nombre_de_la_tabla][i]
        except (KeyError, IndexError):
          continue
        if not entry.winfo_exists():
          continue
        entry.delete(0, tk.END)
      mostrar_aviso(ventana, "✅ SE MODIFICÓ EXITOSAMENTE LOS DATOS", colores["verde_éxito"], 10)
      return True
  except Exception as e:
    print(f"HA OCURRIDO UN ERROR AL MODIFICAR LOS DATOS: {str(e)}")
    return False
  
def eliminar_datos(nombre_de_la_tabla, cajasDeTexto, treeview, ventana):
  if not hasattr(treeview, "winfo_exists") or not treeview.winfo_exists():
    return
  
  selección = treeview.selection()
  
  if not selección:
    return
  try:
    iid = selección[0]
    ID_Seleccionado = int(iid)
  except ValueError:
    ID_Seleccionado = iid
    
  try:
    siguiente_iid = treeview.next(iid)
    
    with conectar_base_de_datos() as conexión:
      cursor = conexión.cursor()
      CampoID = conseguir_campo_ID(nombre_de_la_tabla)
      if not CampoID:
        return
      query = f"DELETE FROM {nombre_de_la_tabla} WHERE {CampoID} = %s"
      cursor.execute(query, (ID_Seleccionado,))
      conexión.commit()

      refrescar_Treeview(nombre_de_la_tabla, treeview)
      
      if siguiente_iid:
        treeview.selection_set(siguiente_iid)
      
      for entry in cajasDeTexto[nombre_de_la_tabla]:
        if entry.winfo_exists():
          entry.delete(0, tk.END)
      mostrar_aviso(ventana, "✅ SE ELIMINÓ UNA COLUMNA", colores["verde_éxito"], 10)
  except Exception as e:
    print(f"HA OCURRIDO UN ERROR AL ELIMINAR LOS DATOS: {str(e)}")
    return False

def importar_datos(nombre_de_la_tabla, treeview):
  try:
    if not hasattr(treeview, "winfo_exists") or not treeview.winfo_exists():
      print("La tabla visual no existe o fue cerrada.")
      return
    
    ruta, datos = seleccionar_archivo_siguiendo_extension(nombre_de_la_tabla)
    if datos is None:
      return
    datos = validar_archivo(ruta, nombre_de_la_tabla, alias, campos_en_db, datos)
    if datos is None:
      return
    
    datos = normalizar_datos(datos)
    if datos is None: #LOS Nones SIRVEN PARA BLOQUEAR EL PASO DE LA IMPORTACIÓN. LA NORMALIZACIÓN DE FECHA Y HORA ESTÁ GUARDADO EN UNA FUNCIÓN PARA EVITAR AGRANDAR EL CÓDIGO
      return
    
    valores_a_importar = subir_DataFrame(nombre_de_la_tabla, datos)
    
    refrescar_Treeview(nombre_de_la_tabla, treeview)
    
    datos_en_cache[nombre_de_la_tabla] = datos.copy()
    print(f"{len(valores_a_importar)} registros importados correctamente en {nombre_de_la_tabla}")
    
  except error_sql as e_sql:
    print(f"OCURRIÓ UNA EXCEPCIÓN: {str(e_sql)}")
  
def exportar_en_PDF(nombre_de_la_tabla, treeview, ventana):
  try:
    if not hasattr(treeview, "winfo_exists") or not treeview.winfo_exists():
      return
    
    datos_a_exportar = treeview.get_children()
    datos = []
   
    encabezado = treeview["columns"]
    
    enc_legible = [alias.get(col, col) for col in encabezado]
    
    datos.append(enc_legible)

    for i in datos_a_exportar:
      valores = treeview.item(i, "values")
      datos.append(valores)

    ruta_archivo_pdf = diálogoArchivo.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("Archivo PDF", "*.pdf")],
        initialfile=f"Reporte_{nombre_de_la_tabla}",
        title="Exportar informe en PDF"
      )
    
    if not ruta_archivo_pdf:
      return   
    
    crear_PDF(ruta_archivo_pdf, datos, nombre_de_la_tabla)
    
    mostrar_aviso(ventana, "✅ SE HA EXPORTADO COMO PDF EXITOSAMENTE", colores["verde_éxito"], 10)  
  except Exception as e:
      print("OCURRIÓ UN ERROR", f"Error al exportar en PDF: {str(e)}")
  finally:
    pass