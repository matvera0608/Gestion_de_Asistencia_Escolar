import dis

# # Desensamblar un archivo fuente
# dis.dis(open("funciones_necesarias/Fun_adicionales.py", "r").read())

# O desensamblar el .pyc directamente
import marshal
with open("__pycache__/Fun_adicionales.cpython-310.pyc", "rb") as f:
    f.read(16)  # saltar cabecera
    code = marshal.load(f)
    dis.dis(code)