import sqlite3
import os

def get_db_path():
    # Solicita la ruta al usuario y se asegura de incluir el nombre del archivo .db
    db_path = input("Ingresa la ruta completa de la base de datos (incluyendo .db): ").strip()
    if not db_path.lower().endswith(".db"):
        # Si no se ingresó el nombre se asume 'Participantes.db'
        if db_path.endswith("\\") or db_path.endswith("/"):
            db_path += "Participantes.db"
        else:
            db_path += os.sep + "Participantes.db"
    # Reemplaza backslashes para evitar problemas de escape y obtiene la ruta absoluta
    db_path = db_path.replace("\\", "/")
    db_path = os.path.abspath(db_path)
    return db_path

while True:
    db_path = get_db_path()
    if os.path.exists(db_path):
        print(f"La base de datos existe en: {db_path}")
        break
    else:
        respuesta = input(f"La base de datos no existe en {db_path}. ¿Deseas crearla? (S/N): ").strip().lower()
        if respuesta == "s":
            # Si el usuario acepta se procederá a crearla al conectarse
            break
        else:
            print("Por favor, ingresa una nueva ruta.")

try:
    # Conexión a la base de datos; si el archivo no existe, se creará
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Crear la tabla t_ciudades (estructura según Anexo 3)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS t_ciudades (
            Id_Departamento INTEGER NOT NULL,
            Id_Ciudad INTEGER NOT NULL,
            Nombre_Departamento TEXT,
            Nombre_Ciudad TEXT,
            PRIMARY KEY (Id_Ciudad)
        );
    ''')

    # 2. Crear la tabla t_participantes (incluyendo la columna Ciudad)
    cursor.execute('''
       CREATE TABLE IF NOT EXISTS t_participantes (
       Id INTEGER NOT NULL UNIQUE,
       Nombre VARCHAR(45),
      "Dirección" VARCHAR(45),
      Celular VARCHAR(45),
      Entidad VARCHAR(45),
      Fecha DATE,
      Ciudad VARCHAR(45),
      PRIMARY KEY(Id)
        );
    ''')

    conn.commit()
    print("Base de datos y tablas creadas/actualizadas exitosamente.")

except sqlite3.Error as e:
    print("Error al conectar o manipular la base de datos:", e)

finally:
    if 'conn' in globals() and conn:
        conn.close()
