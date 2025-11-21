import dis, marshal

# with open("funciones_necesarias/Fun_adicionales.py", "r", encoding="utf-8") as f:
#     dis.dis(f.read())
    
# O desensamblar el .pyc directamente

with open("__pycache__/Fun_ABM_SGAE.cpython-310.pyc", "rb") as f:
    f.read(16)  # saltar cabecera
    code = marshal.load(f)
    dis.dis(code)