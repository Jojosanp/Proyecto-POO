import csv
import sqlite3

# Rutas absolutas a la base de datos y al CSV
db_path = r"C:/Users/jorge/OneDrive/Documentos/Proyecto Poo/Participantes.db"
csv_path = r"C:/Users/jorge/OneDrive/Documentos/Proyecto Poo/Departamentos_y_municipios_de_Colombia_20250222.csv"

# Conectar a la base de datos
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# (Opcional) Vaciar la tabla t_ciudades si deseas reiniciar la carga
cursor.execute("DELETE FROM t_ciudades;")
conn.commit()

with open(csv_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    data = []
    # Usamos un set para almacenar combinaciones únicas (departamento, municipio)
    registros_unicos = set()
    
    for row in reader:
        try:
            # Eliminar el punto para obtener el código completo
            id_dep = int(row['CÓDIGO DANE DEL DEPARTAMENTO'].replace(".", ""))
            id_muni = int(row['CÓDIGO DANE DEL MUNICIPIO'].replace(".", ""))
            departamento = row['DEPARTAMENTO'].strip()
            municipio = row['MUNICIPIO'].strip()
        except KeyError as e:
            print("Error: No se encontró la columna esperada en el CSV.", e)
            data = []  # Para evitar insertar datos incompletos
            break
        except ValueError as e:
            print("Error al convertir un valor numérico:", e)
            continue

        # Crear una tupla para identificar de forma única el registro
        clave = (departamento, municipio)
        if clave not in registros_unicos:
            registros_unicos.add(clave)
            data.append((id_dep, id_muni, departamento, municipio))
        else:
            # Si ya existe, se omite este registro
            continue

if data:
    cursor.executemany("""
        INSERT OR IGNORE INTO t_ciudades (Id_Departamento, Id_Ciudad, Nombre_Departamento, Nombre_Ciudad)
        VALUES (?, ?, ?, ?);
    """, data)
    conn.commit()
    print(f"Se han insertado (o ignorado duplicados) {len(data)} registros en t_ciudades.")
else:
    print("No se encontraron datos en el CSV.")

print("Estructura de t_ciudades:")
cursor.execute("PRAGMA table_info(t_ciudades);")
for columna in cursor.fetchall():
    print(columna)

print("\nContenido de t_ciudades:")
cursor.execute("SELECT * FROM t_ciudades;")
for fila in cursor.fetchall():
    print(fila)

conn.close()
