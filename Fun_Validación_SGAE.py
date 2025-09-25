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
                      "asistencia": [],
                      "nota":       ["valorNota", "fechaEvaluación", "TipoNota"]
                      }
    
    if nombre_de_la_tabla not in tabla_a_validar:
      mensajeTexto.showerror("Error", "La tabla solicitada no se encuentra")
      return False
    
    
    ##Este bloque de validación está bien? ME GUSTARÍA QUE VUELVA A FUNCIONAR COMO ESTABA ANTES
    ##SIN AFECTAR LA CONVERSIÓN DE FECHA Y HORA
    if nombre_de_la_tabla == "nota":
      datos = normalizar_valor_nota(datos)
      if not datos:
        return
    
    validaciones = {
      'alumno': {
              "Nombre": lambda valor : patrón_nombre.match(valor),
              "FechaDeNacimiento": validar_fecha,
      },
      'asistencia': {
              "Estado": lambda valor: valor.isalpha(),
              "Fecha_Asistencia": validar_fecha,
      },
      'carrera': {
              "Nombre": lambda valor :patrón_nombre.match(valor),
              "Duración": lambda valor :patron_alfanumerico_con_espacios.match(valor),
      },
      'materia': {
              "Nombre": lambda valor :patrón_nombre.match(valor),
              "Horario": validar_hora,
      },
      'profesor': {
              "Nombre": lambda valor :patrón_nombre.match(valor),
      },
      'nota': {
              "tipoNota": lambda valor: patron_alfanumerico_con_espacios.match(valor),
              "valorNota": lambda valor: patrón_númerosDecimales.match(valor),
              "fechaEvaluación": validar_fecha,
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
          mensajeTexto.showerror("Error", f"El campo '{campo}' tiene un valor inválido.")
          cursor.close()
          return
    if nombre_de_la_tabla in ["alumno", "profesor", "carrera"]: 
      campo_único = "Nombre"
      cursor.execute(f"SELECT COUNT(*) FROM {nombre_de_la_tabla} WHERE {campo_único} = %s", (datos[campo_único],))
      resultado = cursor.fetchone()
      if resultado[0] > 0:
        mensajeTexto.showinfo("Aviso", "Ya existe datos repetidos")
        cursor.close()
        return False
      cursor.close()
      desconectar_base_de_datos(conexión)
      return True
  except ValueError as error_de_validación:
    print(f"Error de validación: {error_de_validación}")
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
def validar_fecha(valor):
  if isinstance(valor, fecha):
    return True
  if isinstance(valor, str):
    try:
      datetime.strptime(valor, '%d/%m/%Y').date()
      return True
    except ValueError:
      return False
  return False

def validar_hora(valor):
  if isinstance(valor, hora):
    return True # ya es una hora válida
  if isinstance(valor, str):
    try:
      datetime.strptime(valor, '%H:%M').time()
      return True
    except ValueError:
      return False
  return False