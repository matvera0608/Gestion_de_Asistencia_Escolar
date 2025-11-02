from Conexión import *
from .Fun_Validación_SGAE import *
from Elementos import consultas
from datetime import datetime as fecha_y_hora
from tkinter import messagebox as mensajeTexto
import tkinter as tk

def consultar_tabla_dinámica(consultas_meta, nombre_de_la_tabla, valorBúsqueda, operador_like):
    meta = consultas_meta.get(nombre_de_la_tabla.lower())
    if not meta:
        raise ValueError(f"No existe metadata para la tabla '{nombre_de_la_tabla}'")

    select_sql = meta["select"].strip()
    buscables = meta.get("buscables", [])
    orden = meta.get("orden")

    if buscables:
        condiciones = " OR ".join(f"{campo} LIKE %s" for campo in buscables)
        sql = f"{select_sql} WHERE {condiciones}"
        if orden:
            sql = f"{sql} ORDER BY {orden}"
        params = tuple(operador_like.format(valorBúsqueda) for _ in buscables)
    else:
       
        sql = select_sql
        if orden:
            sql = f"{sql} ORDER BY {orden}"
        params = ()

    return sql, params

def guardar_snapshot(treeview):
  #Guardamos el contenido de los datos como la selección y la copia de datos de manera temporal#
  copia_de_datos = {
    "filas": [],
    "selección": treeview.selection()
  }
  
  for item in treeview.get_children():
    valor = treeview.item(item, "values")
    tags = treeview.item(item, "tags")
    fila = { "iid": item, "valores": valor, "tags": tags}
    copia_de_datos["filas"].append(fila)
    
  return copia_de_datos

def restaurar_snapshot(treeview, copia_de_datos):
  #Restauramos cuando se deshabilitan los botones#
  
  treeview.delete(*treeview.get_children()) #Esto hace que limpie visualmente
  
  for fila in copia_de_datos["filas"]:
    treeview.insert("", "end", iid=fila["iid"], values=fila["valores"], tags=fila["tags"]) #Mientras recorro los datos voy volviendo a insertar todo
    
  treeview.selection_set(copia_de_datos["selección"]) #Y Este lo restaura todo

def filtrar(tablas_de_datos, nombre_tabla, selecciónEncabezado):
  #En esta función voy a filtrar todos los datos de la treeview.
  if not hasattr(tablas_de_datos, "winfo_exists") or not tablas_de_datos.winfo_exists():
    return 
  
  with conectar_base_de_datos() as conexión:
    cursor = conexión.cursor()
  for item in tablas_de_datos.get_children():
    tablas_de_datos.delete(item)
  
  sql, parametros = consultar_tabla_dinámica(consultas, nombre_tabla, selecciónEncabezado, "%{}%")
  cursor.execute(sql, parametros)
  registros_ocultos = cursor.fetchall()
  cursor.close()
  for índice, fila in enumerate(registros_ocultos):
    if len(fila) > 1:
      valores_visibles = fila[1:]
      id_iid = fila[0]
    else:
      valores_visibles = fila
      id_iid = None

    tag = "par" if índice % 2 == 0 else "impar"
    if id_iid is not None:
      tablas_de_datos.insert("", "end", iid=str(id_iid), values=valores_visibles, tags=(tag,))
    else:
      tablas_de_datos.insert("", "end", values=valores_visibles, tags=(tag,))
  desconectar_base_de_datos(conexión)

def obtener_selección(treeview):
    try:
      return treeview.selection()
    except tk.TclError:
      mensajeTexto.showerror("ERROR", "La tabla ya no está disponible.")
      return None

def obtener_datos_de_Formulario(nombre_de_la_tabla, cajasDeTexto, campos_de_la_base_de_datos):
  campos_db = campos_de_la_base_de_datos[nombre_de_la_tabla]
  lista_de_cajas = cajasDeTexto[nombre_de_la_tabla]
  
  convertir_datos(campos_db, lista_de_cajas)
  
  if nombre_de_la_tabla not in cajasDeTexto or nombre_de_la_tabla not in campos_de_la_base_de_datos:
    mensajeTexto.showerror("Error", f"Configuración no encontrada para la tabla: {nombre_de_la_tabla}")
    return None
  
  datos = {}

  for campo, caja in zip(campos_db, lista_de_cajas):
    texto = caja.get().strip()
    try:
      if texto.count("/") == 2:
        texto = fecha_y_hora.strptime(texto, "%d/%m/%Y").date()
      elif texto.count(":") == 1 and len(texto) <= 5:
        texto = fecha_y_hora.strptime(texto, "%H:%M").time()
    except ValueError:
      return None
    datos[campo] = texto
  
  return datos

def conseguir_campo_ID(nombre_de_la_tabla):
  IDs_mapeados = {
              'alumno': "ID_Alumno",
              'asistencia': "ID",
              'carrera': "ID_Carrera",
              'materia': "ID_Materia",
              'enseñanza': "ID",
              'profesor': "ID_Profesor",
              'nota': "ID"
        }
  return IDs_mapeados.get(nombre_de_la_tabla.strip().lower())

def convertir_datos(campos_db, lista_de_cajas):
  for campo, caja in zip(campos_db, lista_de_cajas):
    valor = caja.get()
    
    if isinstance(valor, str) and "fecha" in campo.lower():
        try:
            fecha_obj = fecha_y_hora.strptime(valor, "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            continue
        valor = fecha_obj
    elif isinstance(valor, str) and "hora" in campo.lower():
        try:
            hora_obj = fecha_y_hora.strptime(valor, "%H:%M:%S").strftime("%H:%M")
        except ValueError:
            continue
        valor = hora_obj
    caja.delete(0, tk.END)  # Limpia el entry
    caja.insert(0, str(valor))  # Inserta el valor convertido

#En esta función se crea un label que muestra la hora actual y se actualiza cada segundo
#pero si el label ya existe, sólo se actualiza su texto.
# # def actualizar_la_hora(contenedor):
# #   color_padre = contenedor.cget('bg')
# #   if hasattr(contenedor, 'label_Hora'):
# #     contenedor.label_Hora.config(text=fecha_y_hora.now().strftime("%H:%M:%S"))
# #   else:
# #     contenedor.label_Hora = tk.Label(contenedor, font=("Arial", 10, "bold"), bg=color_padre, fg="blue")
# #     contenedor.label_Hora.grid(row=20, column=0, sticky="ne", padx=0, pady=0)
# #     contenedor.label_Hora.config(text=fecha_y_hora.now().strftime("%H:%M:%S"))
# #   contenedor.after(1000, lambda: actualizar_la_hora(contenedor))

def construir_query(nombre_de_la_tabla, filtros):
  consulta_base = ""
  filtro = ""

  if filtros:
      condiciones = [f'{campo} = %s' for campo in filtros.keys()]
      filtro = " WHERE " + " AND ".join(condiciones)

  match nombre_de_la_tabla.lower():
      case "alumno":
          consulta_base = """SELECT a.ID_Alumno, a.Nombre, DATE_FORMAT(a.FechaDeNacimiento, '%d/%m/%Y') AS FechaNacimiento, c.Nombre AS Carrera
                              FROM alumno AS a
                              JOIN carrera AS c ON a.IDCarrera = c.ID_Carrera
                              ORDER BY a.Nombre;
                          """
      case "asistencia":
          consulta_base = """SELECT asis.ID, asis.Estado, DATE_FORMAT(asis.Fecha_Asistencia, '%d/%m/%Y') AS Fecha, al.Nombre AS Alumno, p.Nombre AS Profesor
                              FROM asistencia AS asis
                              JOIN alumno AS al ON asis.IDAlumno = al.ID_Alumno
                              JOIN profesor AS p ON asis.IDProfesor = p.ID_Profesor
                              ORDER BY asis.Fecha_Asistencia"""
      case "carrera":
          consulta_base = """SELECT c.ID_Carrera, c.Nombre, c.Duración
                              FROM carrera AS c
                              ORDER BY c.Nombre"""
      case "materia":
          consulta_base = """SELECT m.ID_Materia, m.Nombre, TIME_FORMAT(m.HorarioEntrada,'%H:%i') AS HorarioEntrada, TIME_FORMAT(m.HorarioSalida,'%H:%i') AS HorarioSalida, c.Nombre AS Carrera
                              FROM materia AS m
                              JOIN carrera AS c ON m.IDCarrera = c.ID_Carrera
                              ORDER BY m.Nombre"""
      case "enseñanza":
          consulta_base = """SELECT e.ID, m.Nombre AS Materia, p.Nombre AS Profesor
                              FROM enseñanza AS e
                              JOIN profesor AS p ON e.IDProfesor = p.ID_Profesor
                              JOIN materia AS m ON e.IDMateria = m.ID_Materia
                              ORDER BY m.Nombre, p.Nombre"""
      case "profesor":
          consulta_base = """SELECT pro.ID_Profesor, pro.Nombre
                              FROM profesor AS pro
                              ORDER BY pro.Nombre"""
      case "nota":
          consulta_base = """SELECT n.ID, al.Nombre AS Alumno, m.Nombre AS Materia, p.Nombre AS Profesor,
                              REPLACE(CAST(n.valorNota AS CHAR(10)), '.', ',') AS Nota, 
                              n.tipoNota, DATE_FORMAT(n.fecha, '%d/%m/%Y') AS FechaEv
                              FROM nota AS n
                              JOIN alumno AS al ON n.IDAlumno = al.ID_Alumno
                              JOIN materia AS m ON n.IDMateria = m.ID_Materia
                              JOIN profesor AS p ON n.IDProfesor = p.ID_Profesor
                              ORDER BY al.Nombre, m.Nombre"""
      case _:
          consulta_base = f"SELECT * FROM {nombre_de_la_tabla}"

  return consulta_base + filtro

def consultar_tabla(nombre_de_la_tabla):
  try:
    conexión = conectar_base_de_datos()
    if conexión:
      cursor = conexión.cursor()
      query = construir_query(nombre_de_la_tabla, {})
      cursor.execute(query)
      res = cursor.fetchall()
      cursor.close()
      desconectar_base_de_datos(conexión)
      return res
  except Exception as Exc:
    mensajeTexto.showerror("ERROR", f"Algo no está correcto o no tiene nada de datos: {Exc}")

def traducir_IDs(nombre_de_la_tabla, datos):
  campos_a_traducir = {
      "alumno": {"IDCarrera": ("ID_Carrera","carrera", "Nombre")},
      "materia": {"IDCarrera": ("ID_Carrera","carrera", "Nombre")},
      "asistencia": {"IDAlumno": ("ID_Alumno","alumno", "Nombre"), "IDProfesor": ("ID_Profesor","profesor", "Nombre")},
      "enseñanza": {"IDProfesor": ("ID_Profesor","profesor", "Nombre"), "IDMateria": ("ID_Materia", "materia", "Nombre")},
      "nota": {"IDAlumno": ("ID_Alumno","alumno", "Nombre"), "IDMateria": ("ID_Materia","materia", "Nombre"), "IDProfesor": ("ID_Profesor","profesor", "Nombre")}
  }
  if not datos:
    return None
  # Crear un nuevo diccionario para almacenar los datos traducidos
  datos_traducidos = datos.copy()
  relación = campos_a_traducir.get(nombre_de_la_tabla.lower())
  if not relación:
    return datos
  try:
      with conectar_base_de_datos() as conexión:
        cursor = conexión.cursor()
        for campo_fkID, (campo_idPK, tabla_ref, campo_ref) in relación.items():
          if campo_fkID in datos:
            nombre_a_buscar = datos[campo_fkID]
            consulta = f"SELECT {campo_idPK} FROM {tabla_ref} WHERE {campo_ref} = %s"
            cursor.execute(consulta, (nombre_a_buscar,))
            resultado = cursor.fetchone()
            
            if resultado:
                datos_traducidos[campo_fkID] = resultado[0]
            else:
                mensajeTexto.showerror("ERROR DE DATOS", f"❌ El '{nombre_a_buscar}' no existe en la base de datos.")
                return None
      return datos_traducidos
      
  except Exception as e:
      mensajeTexto.showerror("ERROR DE CONEXIÓN", f"❌ Error al conectar a la base de datos: {e}")
      return None
    
    
campos_con_claves = {
  "carrera": ("ID_Carrera","Nombre"),
  "alumno": ("ID_Alumno","Nombre"),
  "profesor": ("ID_Profesor", "Nombre"),
  "materia": ("ID_Materia","Nombre")
  }

campos_foráneos = {"alumno": ("IDCarrera", "carrera"),
                   "asistencia": [("IDAlumno", "alumno"), ("IDProfesor","profesor")],
                   "materia": ("IDCarrera", "carrera"),
                   "enseñanza": [("IDMateria", "materia"), ("IDProfesor","profesor")], 
                   "nota": [("IDMateria", "materia"), ("IDAlumno", "alumno"), ("IDProfesor","profesor")]
                   }

#--- FUNCIONES DEL ABM (ALTA, BAJA Y MODIFICACIÓN) ---
def cargar_datos_en_Combobox(tablas_de_datos, combos):
  try:
    with conectar_base_de_datos() as conexión:
      if not conexión:
        return
      cursor = conexión.cursor()
      relación = campos_foráneos.get(tablas_de_datos)
      if not relación:
        return
        
      if not isinstance(combos, (list, tuple)):
        combos = [combos]
      
      if isinstance(relación, tuple):
        relación = [relación]
      
      for comboWid in combos:
        nombre_combo = getattr(comboWid, "widget_interno", "").lower()
        if not nombre_combo.startswith("cbbox"):
          continue
        nombre_combo = nombre_combo.replace("cbbox_", "")
        for campo_foráneo, tabla_ajena in relación:
          if nombre_combo == tabla_ajena:
            id_campo, campoVisible = campos_con_claves[tabla_ajena]
            consulta = f"SELECT {id_campo}, {campoVisible} FROM {tabla_ajena}"
            cursor.execute(consulta)
            registros = cursor.fetchall()
            valores = [fila[1] for fila in registros]
            comboWid["values"] = valores
            comboWid.id_Nombre = {fila[1]: fila[0] for fila in registros}
  except error_sql as sql_error:
    mensajeTexto.showerror("ERROR", f"HA OCURRIDO UN ERROR AL CARGAR DATOS EN COMBOBOX: {str(sql_error)}")
    return

def mostrar_registro(nombre_de_la_tabla, tablas_de_datos, cajasDeTexto):
  if not hasattr(tablas_de_datos, "winfo_exists") or not tablas_de_datos.winfo_exists():
    return

  selección = tablas_de_datos.selection()
  if not selección:
    return
  
  iid = selección[0]
  try:
    idSeleccionado = int(iid)
  except ValueError:
    idSeleccionado = iid
  
  cursor = None
  conexión = conectar_base_de_datos()
  if conexión:
    try:
      cursor = conexión.cursor()
      # Diccionario de claves primarias según la tabla
      PKs = {
        "alumno": "ID_Alumno",
        "asistencia": "ID",
        "carrera": "ID_Carrera",
        "materia": "ID_Materia",
        "profesor": "ID_Profesor",
        "enseñanza": "ID",
        "nota": "ID",
      }
      
      clave = PKs.get(nombre_de_la_tabla)
      if not clave:
        mensajeTexto.showerror("ERROR", "No se pudo determinar la superclave para esta tabla.")
        return
      campos_visibles = {
      "alumno": ["Nombre", "FechaDeNacimiento", "IDCarrera"], #Los que empiezan con ID sin guión bajo son claves ajenas o FKs.
      "asistencia":["Estado", "Fecha_Asistencia", "IDAlumno", "IDProfesor"],
      "carrera": ["Nombre", "Duración"],
      "materia": ["Nombre", "HorarioEntrada", "HorarioSalida", "IDCarrera"],
      "enseñanza": ["IDMateria", "IDProfesor"],
      "profesor": ["Nombre"],
      "nota": ["IDAlumno", "IDMateria", "IDProfesor", "valorNota", "tipoNota", "fecha"]
      }

      columnas = ', '.join(campos_visibles[nombre_de_la_tabla.lower()])
      consulta = f"SELECT {columnas} FROM {nombre_de_la_tabla.lower()} WHERE {clave} = %s"
      cursor.execute(consulta, (idSeleccionado,))
      fila_seleccionada = cursor.fetchone()
      
      if not fila_seleccionada:
        return
      
      datos_convertidos = []

      for campo, valor in zip(campos_visibles[nombre_de_la_tabla.lower()], fila_seleccionada):
        if campo == "IDProfesor":
            cursor.execute("SELECT Nombre FROM profesor WHERE ID_Profesor = %s", (valor,))
            res = cursor.fetchone()
            datos_convertidos.append(res[0] if res else "Desconocido")
        elif campo == "IDMateria":
            cursor.execute("SELECT Nombre FROM materia WHERE ID_Materia = %s", (valor,))
            res = cursor.fetchone()
            datos_convertidos.append(res[0] if res else "Desconocido")
        elif campo == "IDAlumno":
            cursor.execute("SELECT Nombre FROM alumno WHERE ID_Alumno = %s", (valor,))
            res = cursor.fetchone()
            datos_convertidos.append(res[0] if res else "Desconocido")
        elif campo == "IDCarrera":
            cursor.execute("SELECT Nombre FROM carrera WHERE ID_Carrera = %s", (valor,))
            res = cursor.fetchone()
            datos_convertidos.append(res[0] if res else "Desconocido")
        else:
            datos_convertidos.append(valor)
            continue
          
      cajas = cajasDeTexto[nombre_de_la_tabla]
      for campo, valor, caja in zip(campos_visibles[nombre_de_la_tabla], datos_convertidos, cajas):
        caja.config(state="normal")
        caja.set(str(valor))
        caja.config(state="readonly" if getattr(caja, "widget_interno", "").startswith("cbBox_") else "normal")
          
      convertir_datos(campos_visibles[nombre_de_la_tabla], cajas)
      
    except error_sql as error:
      mensajeTexto.showerror("ERROR", f"ERROR INESPERADO AL SELECCIONAR: {str(error)}")
    finally:
      cursor.close()
      desconectar_base_de_datos(conexión)