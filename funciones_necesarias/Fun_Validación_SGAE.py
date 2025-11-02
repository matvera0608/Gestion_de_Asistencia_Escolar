from datetime import datetime
import re

patrón_nombre = re.compile(r'^[A-Za-záéíóúÁÉÍÓÚñÑüÜ\s]+$')
patrón_númerosDecimales = re.compile(r'^\d+([.,]\d+)?$')
#patrón_alfanumérico = re.compile(r'^[A-Za-z0-9áéíóúÁÉÍÓÚñÑüÜ\s]+$')
patron_alfanumerico_con_espacios = re.compile(r'^[A-Za-z0-9áéíóúÁÉÍÓÚñÑüÜ\s]+$')

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
    return True
  except ValueError:
      widget.config(background="salmon")
  return False

def validar_hora(widget):
  try:
      datetime.strptime(widget.get(), "%H:%M")
      widget.config(background="white")
  except ValueError:
      widget.config(background="salmon")
  return False

def aplicar_validación_fecha(widget, mi_ventana):
  vcmd_key = (mi_ventana.register(validar_fecha_combobox), "%P")
  widget.config(validate="key", validatecommand=vcmd_key)
  widget.bind("<FocusOut>", lambda e: validar_fecha(widget))

def aplicar_validación_hora(widget, mi_ventana):
  vcmd_key = (mi_ventana.register(validar_hora_combobox), "%P")
  widget.config(validate="key", validatecommand=vcmd_key)
  widget.bind("<FocusOut>", lambda e: validar_hora(widget))

def validar_fecha_combobox(valor):
  return True if re.fullmatch(r"[0-9]{0,2}(/[0-9]{0,2}(/[0-9]{0,4})?)?", valor) else False

def validar_hora_combobox(valor):
    return True if re.fullmatch(r"[0-9]{0,2}(:[0-9]{0,2})?", valor) else False
  
def validar_nombre_combobox(valor):
  return True if re.fullmatch(patrón_nombre, valor) else False