from Conexión import *
import re

patrón_nombre = re.compile(r'^[A-Za-záéíóúÁÉÍÓÚñÑüÜ\s]+$')
patrón_fecha = re.compile(r'^(0?[1-9]|[12][0-9]|3[01])/(0?[1-9]|1[0-2])/\d{4}$')
patrón_hora = re.compile(r'^([01]\d|2[0-3]):([0-5]\d)$')
patrón_alfanumérico_con_espacios = re.compile(r'^[A-Za-z0-9áéíóúÁÉÍÓÚñÑüÜ\s]+$')
patrón_nota = re.compile(r'^(10([.,]0{1,2})?|[1-9]([.,]\d{1,2})?)$')

separadores_comunes = re.compile(r"[–—\-•|→]")
comillas_o_puntos_suspensivos = re.compile(r"[\"'“”‘’…]")
separadores_y_comillas = re.compile(r"[–—\-•|→\"'“”‘’…]")
múltiples_espacios = re.compile(r"\s{2,}")
punto_y_coma = re.compile(r"[.,;]")

def normalizar_expresión(s):
    return s.lower().strip()

def normalizar_encabezado(texto: str) -> str:
    texto = normalizar_expresión(texto)
    texto = texto.replace(" ", "")
    texto = separadores_y_comillas.sub( "", texto)   # separadores y comillas
    texto = múltiples_espacios.sub(" ", texto)             # múltiples espacios
    return texto

def normalizar_valor(valor, campo=None):
    if not isinstance(valor, str):
        return valor  # no tocamos enteros, fechas, etc. 
    # 1. Quitar espacios, tabulaciones y saltos de línea
    original = valor.strip()
    
    if campo and campo.lower() in ["nota", "calificación", "calificaciones", "notas"]:
        return original.replace(",", ".") if "," in original else original

    # 2. Eliminar separadores comunes
    valor = separadores_comunes.sub("", original)  # guiones, bullets, flechas

    # 3. Eliminar comillas, puntos suspensivos, etc.
    valor = comillas_o_puntos_suspensivos.sub("", valor)

    # 4. reeemplazar múltiples espacios por uno solo
    valor = múltiples_espacios.sub(" ", valor)
    
    valor = punto_y_coma.sub("", valor)

    # 5. Si queda vacío, devolver None
    return valor if valor else None

def detectar_repeticiones_de_datos(datos, tabla):
    valorNombre = datos.get("Nombre", "").strip()
    
    if not valorNombre:
        return False
    
    palabras = valorNombre.lower().split()
    
    for i in range(len(palabras) - 1):
        if palabras[i] == palabras[i + 1]:
            return True
        

    nombres_existentes = []
    if tabla in ["alumno", "materia", "profesor", "carrera", "nota"]:
        try:
            with conectar_base_de_datos() as conexión:
                cursor = conexión.cursor()
                cursor.execute(f"SELECT Nombre FROM {tabla}")
                registros = cursor.fetchall()
                nombres_existentes = [fila[0].strip().lower() for fila in registros if fila and fila[0]]
        except Exception as e:
            print(f"Advertencia: No se pudo verificar la unicidad del nombre debido a un error de DB: {e}")
            pass
            
    if valorNombre.lower() in nombres_existentes:
        return True
    
    return False
    
def verificar_horarioSalida_mayor_horarioEntrada(datos):
    
    try:
        horario_entrada = datos.get("HorarioEntrada", "")
        horario_salida = datos.get("HorarioSalida", "")
    
        if not horario_entrada or not horario_salida:
            return False
        
    except ValueError:
        return False
    
    return horario_salida < horario_entrada
   
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
                        if len(partes[0]) == 2 and (dia < 1 or dia > 31):
                            return False
                    except ValueError:
                        return False
                
                if len(partes) > 1 and partes[1]:
                    try:
                        mes = int(partes[1])
                        if len(partes[1]) == 2 and (mes < 1 or mes > 12):
                            return False
                    except ValueError:
                        return 
                    
                if len(partes) > 2 and partes[2]:
                    if not partes[2].isdigit() or len(partes[2]) > 4:
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
                    try:
                        hora = int(valor)
                        if hora < 0 or hora > 23:
                            return False
                    except:
                        return False
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