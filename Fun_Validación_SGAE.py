from Conexión import conectar_base_de_datos, desconectar_base_de_datos
from datetime import datetime, date as fecha, time as hora
from tkinter import messagebox as mensajeTexto
import re

#Esta función validar_datos valida los datos antes de agregarlo a la listbox para evitar redundancias
def validar_datos(nombre_de_la_tabla, datos):
  try:
    conexión = conectar_base_de_datos()
    cursor = conexión.cursor()
    patrón_nombre = re.compile(r'^[A-Za-záéíóúÁÉÍÓÚñÑüÜ\s]+$')
    patrón_númerosDecimales = re.compile(r'^\d+([.,]\d+)?$')
    #patrón_alfanumérico = re.compile(r'^[A-Za-z0-9áéíóúÁÉÍÓÚñÑüÜ\s]+$')
    patron_alfanumerico_con_espacios = re.compile(r'^[A-Za-z0-9áéíóúÁÉÍÓÚñÑüÜ\s]+$')
    
    tabla_a_validar = {"alumno":    ["Nombre", "FechaDeNacimiento"],
                      "carrera":    ["Nombre", "Duración"],
                      "materia":    ["Nombre", "Horario"],
                      "profesor":   ["Nombre",],
                      "enseñanza":  [],
                      "asistencia": [],
                      "nota":       ["valorNota", "fechaEvaluación", "TipoNota"]
                      }
    
    if nombre_de_la_tabla not in tabla_a_validar:
      mensajeTexto.showerror("Error", "La tabla solicitada no se encuentra")
      return
    
    
    ##Este bloque de validación está bien? ME GUSTARÍA QUE VUELVA A FUNCIONAR COMO ESTABA ANTES
    ##SIN AFECTAR LA CONVERSIÓN DE FECHA Y HORA
    if nombre_de_la_tabla == "nota":
      datos = normalizar_valor_nota(datos)
      if not datos:
        return
    
    validaciones = {
      'alumno': {
              "Nombre": lambda valor : patrón_nombre.match(valor),
      },
      'asistencia': {
              "Estado": lambda valor: valor.isalpha(),
      },
      'carrera': {
              "Nombre": lambda valor :patrón_nombre.match(valor),
              "Duración": lambda valor :patron_alfanumerico_con_espacios.match(valor),
      },
      'materia': {
              "Nombre": lambda valor :patrón_nombre.match(valor),
              "Horario": validar_hora,
      },
      'enseñanza': {
      },
      'profesor': {
              "Nombre": lambda valor :patrón_nombre.match(valor),
      },
      'nota': {
              "tipoNota": lambda valor: patron_alfanumerico_con_espacios.match(valor),
              "valorNota": lambda valor: patrón_númerosDecimales.match(valor),
      }
    }

    for campo, valor in datos.items():
      if campo in validaciones[nombre_de_la_tabla]:
        # Validar vacío solo si es str
        if isinstance(valor, str) and not valor.strip():
            mensajeTexto.showerror("Error", f"El campo '{campo}' está vacío.")
            return False
        validador = validaciones[nombre_de_la_tabla][campo]
        esVálido = validador(valor) if callable(validador)  else bool(validador.match(valor))
        if not esVálido:
          return
      if nombre_de_la_tabla in ["alumno", "profesor", "carrera"]: 
        campo_único = "Nombre"
        cursor.execute(f"SELECT COUNT(*) FROM {nombre_de_la_tabla} WHERE {campo_único} = %s", (datos[campo_único],))
        resultado = cursor.fetchone()
        if resultado[0] > 0:
          cursor.close()
          desconectar_base_de_datos(conexión)
          return False
      return True
  except ValueError as error_de_validación:
    return False
  desconectar_base_de_datos(conexión)
  return True

def normalizar_valor_nota(datos):
  if "valorNota" in datos:
    valor = datos["valorNota"].strip().lower().replace(",", ".")
    try:
      número = float(valor)
      datos["valorNota"] = f"{número:.2f}"
    except ValueError:
      return False
  return datos

## Estas funciones se encargan de validar los datos de fecha, hora y nota. Pero de una forma muy forzada,
## es decir, para que SQL no sepa principalmente la fecha en formato 'YYYY-MM-DD' está así. Buscamos que se haga 'DD/MM/YYYY'
def validar_fecha(widget):
  try:
      datetime.strptime(widget.get(), "%d/%m/%Y")
      widget.config(background="white")
  except ValueError:
      widget.config(background="salmon")
  return False

def validar_hora(valor):
  if isinstance(valor, hora):
    return True
  if isinstance(valor, str):
    try:
      datetime.strptime(valor, '%H:%M').time()
      return True
    except ValueError:
      return False
  return False


def aplicar_validación_fecha(widget, mi_ventana):
  vcmd_key = (mi_ventana.register(validar_fecha_combobox), "%P")
  widget.config(validate="key", validatecommand=vcmd_key)
  widget.bind("<FocusOut>", lambda e: validar_fecha(widget))
  widget.bind("<KeyPress>", bloquear_caracter)

def validar_fecha_combobox(valor):
  return True if re.fullmatch(r"[0-9]{0,2}(/[0-9]{0,2}(/[0-9]{0,4})?)?", valor) else False


def bloquear_caracter(event):
  if not re.match(r"[0-9/]", event.char) and event.keysym not in ("BackSpace", "Delete", "Tab", "Left", "Right"):
      return "break"
