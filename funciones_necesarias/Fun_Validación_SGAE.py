import re

patrón_nombre = re.compile(r'^[A-Za-záéíóúÁÉÍÓÚñÑüÜ\s]+$')
patrón_númerosDecimales = re.compile(r'^\d+([.,]\d+)?$')
patrón_fecha = re.compile(r'^\d{0,2}(/?\d{0,2}){0,1}(/?\d{0,4}){0,1}$')
patrón_hora = re.compile(r'^\d{0,2}(:\d{0,2}){0,1}$')
patrón_alfanumérico_con_espacios = re.compile(r'^[A-Za-z0-9áéíóúÁÉÍÓÚñÑüÜ\s]+$')
patrón_nota = re.compile(r'^(10([.,]0{1,2})?|[1-9]([.,]\d{1,2})?)$')


def normalizar_valor_nota(datos):
  valor = datos.get("valorNota", "").strip().replace(",", ".")
  if re.fullmatch(patrón_nota, valor):
      return {"valorNota": float(valor)}
  return False


def aplicar_validación(widget, ventana, tipo):
  try:
    
    validaciones = {
      "fecha": lambda validar: re.fullmatch(patrón_fecha, validar),
      "hora": lambda validar: re.fullmatch(patrón_hora, validar),
      "nombre": lambda validar: re.fullmatch(patrón_nombre, validar),
      "duración": lambda validar: re.fullmatch(patrón_alfanumérico_con_espacios, validar),
      "nota": lambda validar: normalizar_valor_nota({"valorNota": validar})
    }

    vcmd = (ventana.register(lambda valor: valor == "" or bool(validaciones[tipo](valor))), "%P")
    widget.config(validate="key", validatecommand=vcmd)
  except:
    print("ERROR DE VALIDACIÓN")
    return False