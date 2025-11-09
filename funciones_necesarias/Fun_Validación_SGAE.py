import re

patrón_nombre = re.compile(r'^[A-Za-záéíóúÁÉÍÓÚñÑüÜ\s]+$')
patrón_fecha = re.compile(r'^(0?[1-9]|[12][0-9]|3[01])/(0?[1-9]|1[0-2])/\d{4}$')
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
                partes = valor.split("/")
                if len(partes) > 0 and partes[0]:
                    
                    if not partes[0].isdigit() or len(partes[0]) > 2:
                        return False
                    try:
                        dia = int(partes[0])
                        if dia < 1 or dia > 31:
                            return False
                    except ValueError:
                        return False
                
                if len(partes) > 1 and partes[1]:
                    try:
                        mes = int(partes[1])
                        if mes < 1 or mes > 12:
                            return False
                    except ValueError:
                        return False
                if len(partes) > 2 and partes[2]:
                    if not partes[2].isdigit() or len(partes[2]) > 4:
                        return False
                
                if not re.fullmatch(r'[\d/]*', valor):
                    return False
                
                if len(valor) == 10:
                    return bool(patrón_fecha.match(valor))
                return True

            elif tipo == "hora":
                if not re.fullmatch(r'[\d:.,]*', valor):
                    return False
                
                partes = valor.split(":")
                
                valor = valor.replace(".", ":").replace(",", ":")
                
                if len(partes) > 0 and partes[0]:
                    try:
                        hora = int(partes[0])
                        if hora < 0 or hora > 23:
                            return False
                    except ValueError:
                        return False
                
                if len(partes) > 1 and partes[1]:
                    try:
                        minuto = int(partes[1])
                        if minuto < 0 or minuto > 59:
                            return False
                    except ValueError:
                        return False
                
                if len(partes) == 1 and len(valor) in (1, 2):
                    widget.after_idle(lambda: widget.delete(0, "end"))
                    widget.after_idle(lambda: widget.insert(0, f"{int(valor):02d}:00"))
                    return True
                return True

            elif tipo == "nombre":
                return bool(re.fullmatch(patrón_nombre, valor))

            elif tipo == "duración":
                return bool(re.fullmatch(patrón_alfanumérico_con_espacios, valor))

            elif tipo == "nota":
                return bool(re.fullmatch(patrón_nota, valor))

            return True
        vcmd = (ventana.register(validar), "%P")
        widget.config(validate="key", validatecommand=vcmd)
    except Exception as e:
        print(f"ERROR DE VALIDACIÓN: {e}")
        return False