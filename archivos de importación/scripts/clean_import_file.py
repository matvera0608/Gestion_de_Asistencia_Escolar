"""
Script para limpiar archivos de importación con columnas mezcladas.
Uso: python scripts\clean_import_file.py <ruta_entrada> <ruta_salida>

Heurísticas:
- Busca patrones de hora HH:MM en cada línea.
- Si encuentra 2 horas seguidas (incluso pegadas: 15301700), las separa como entrada/salida.
- El nombre de la materia es lo que quede antes de la primera hora encontrada (o antes del primer tab).
- La carrera se toma como el texto después de la última hora; si no, el último campo separado por tab.
- Guarda como TSV con columnas: Nombre,HorarioEntrada,HorarioSalida,Carrera
"""
import re
import sys
from pathlib import Path

TIME_RE = re.compile(r"(\d{1,2}:?\d{2})")
# también cubrir casos sin ':' como '1530' o '15301700'
COMBINED_TIME_RE = re.compile(r"(\d{1,2}:?\d{2})(\d{1,2}:?\d{2})")


def normalize_time(t):
    # Acepta '1530' o '15:30' y devuelve '15:30'
    t = t.strip()
    if ':' in t:
        h, m = t.split(':')
    else:
        # asumir últimos 2 dígitos minutos
        if len(t) <= 2:
            return t
        h = t[:-2]
        m = t[-2:]
    try:
        h_i = int(h)
        m_i = int(m)
        return f"{h_i:02d}:{m_i:02d}"
    except Exception:
        return t


def parse_line(line):
    # eliminar saltos finales
    original = line.rstrip('\n')
    # primer intento: separar por tabs
    parts = [p.strip() for p in original.split('\t') if p.strip() != '']
    if len(parts) >= 4:
        # ya está bien separado
        nombre = parts[0]
        entrada = normalize_time(parts[1])
        salida = normalize_time(parts[2])
        carrera = ' '.join(parts[3:])
        return nombre, entrada, salida, carrera

    # si no, buscar horas en la línea
    # tratar casos donde dos horas están pegadas como 15301700 o 15:3017:00
    # primero reemplazar ocurrencias como 15301700 -> 15:30 17:00
    # buscar pares de horas pegadas
    m_comb = COMBINED_TIME_RE.search(original.replace(':',''))
    if m_comb:
        # reconstruir usando grupos de 4 o 2+2
        # simplificamos: buscamos todas las ocurrencias de 4 dígitos seguidos o tiempos con ':'
        times = re.findall(r"\d{1,2}:?\d{2}", original)
    else:
        times = re.findall(r"\d{1,2}:?\d{2}", original)

    times = [normalize_time(t) for t in times]

    if len(times) >= 2:
        entrada, salida = times[0], times[1]
        # nombre: todo lo anterior a la primera ocurrencia de la primera hora
        first_time_match = re.search(re.escape(times[0]).replace(':',':?' ), original)
        if first_time_match:
            idx = first_time_match.start()
            nombre = original[:idx].strip()
        else:
            # fallback: tomar primer campo antes de primer dígito
            nombre = re.split(r"\d", original, 1)[0].strip()
        # carrera: lo que quede después de la última hora
        last_time = times[1]
        # buscar la última aparición cruda (sin normalizar) en original
        last_match = None
        for m in re.finditer(r"\d{1,2}:?\d{2}", original):
            last_match = m
        if last_match:
            carrera = original[last_match.end():].strip()
        else:
            carrera = ''
        # si carrera está vacía y había tabs, usar último part
        if not carrera and parts:
            carrera = parts[-1]
        return nombre, entrada, salida, carrera

    # si solo hay 1 time o ninguna, intentar separar por tabs o espacios
    if parts:
        if len(parts) == 1:
            # intentar extraer nombre y carrera separando por múltiples espacios al final
            # buscar últimas palabras que parezcan una carrera (palabras con mayúsculas internas)
            tokens = original.split()
            if len(tokens) >= 2:
                nombre = ' '.join(tokens[:-1])
                carrera = tokens[-1]
            else:
                nombre = original
                carrera = ''
            return nombre, '', '', carrera
        elif len(parts) == 2:
            nombre = parts[0]
            carrera = parts[1]
            return nombre, '', '', carrera
        elif len(parts) == 3:
            nombre, entrada, carrera = parts
            return nombre, normalize_time(entrada), '', carrera

    # fallback final
    return original, '', '', ''


def clean_file(ruta_entrada, ruta_salida):
    ruta_entrada = Path(ruta_entrada)
    ruta_salida = Path(ruta_salida)
    if not ruta_entrada.exists():
        print(f"Archivo no encontrado: {ruta_entrada}")
        return
    lines = ruta_entrada.read_text(encoding='utf-8').splitlines()
    header = "Nombre\tHorarioEntrada\tHorarioSalida\tCarrera\n"
    out_lines = [header]
    for i, line in enumerate(lines):
        if i == 0 and ("Nombre" in line and "Horario" in line):
            # saltar header original
            continue
        if not line.strip():
            continue
        nombre, entrada, salida, carrera = parse_line(line)
        out_lines.append(f"{nombre}\t{entrada}\t{salida}\t{carrera}\n")

    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    ruta_salida.write_text(''.join(out_lines), encoding='utf-8')
    print(f"Limpieza completa → {ruta_salida} ({len(out_lines)-1} registros)")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Uso: python clean_import_file.py <ruta_entrada> <ruta_salida>")
        sys.exit(1)
    clean_file(sys.argv[1], sys.argv[2])
