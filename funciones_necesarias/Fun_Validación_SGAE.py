import re

patrón_nombre = re.compile(r'^[A-Za-záéíóúÁÉÍÓÚñÑüÜ\s]+$')
patrón_númerosDecimales = re.compile(r'^\d+([.,]\d+)?$')
patrón_fecha = re.compile(r'^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$')
patrón_hora = re.compile(r'^([01]\d|2[0-3]):([0-5]\d)$')
patrón_alfanumérico_con_espacios = re.compile(r'^[A-Za-z0-9áéíóúÁÉÍÓÚñÑüÜ\s]+$')
patrón_nota = re.compile(r'^(10([.,]0{1,2})?|[1-9]([.,]\d{1,2})?)$')


def normalizar_valor_nota(datos):
  valor = datos.get("valorNota", "").strip().replace(",", ".")
  if re.fullmatch(patrón_nota, valor):
      return {"valorNota": float(valor)}
  return False


def aplicar_validación(widget, ventana, tipo):
    try:
      def validar(valor):
        
        if valor == "":
            return True

        if tipo == "fecha":
            if not re.fullmatch(r'[\d/]*', valor):
                return False
            
            if len(valor) == 10:
                return bool(re.fullmatch(patrón_fecha, valor))
            return True

        elif tipo == "hora":
            
            if not re.fullmatch(r'[\d:]*', valor):
                return False
            if len(valor) == 5:
                return bool(re.fullmatch(patrón_hora, valor))
            return True

        elif tipo == "nombre":
            return bool(re.fullmatch(r"[A-Za-záéíóúÁÉÍÓÚñÑüÜ\s]*", valor))

        elif tipo == "duración":
            return bool(re.fullmatch(r"[A-Za-z0-9áéíóúÁÉÍÓÚñÑüÜ\s]*", valor))

        elif tipo == "nota":
            return bool(re.fullmatch(r"\d*([.,]\d*)?", valor))

        return True
      vcmd = (ventana.register(validar), "%P")
      widget.config(validate="key", validatecommand=vcmd)
    except Exception as e:
        print(f"ERROR DE VALIDACIÓN: {e}")
        return False