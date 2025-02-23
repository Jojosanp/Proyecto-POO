# db_handler.py
import sqlite3

class DatabaseHandler:
    def __init__(self, db_path):
        self.db_path = db_path

    def connect(self):
        """Establece y retorna una conexión a la base de datos."""
        return sqlite3.connect(self.db_path)

    def execute_query(self, query, params=()):
        """Ejecuta una consulta con parámetros opcionales y retorna el cursor."""
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return cursor
        except sqlite3.Error as e:
            print("Error en la consulta:", e)
            return None

    def fetch_all(self, query, params=()):
        """Ejecuta una consulta y retorna todos los resultados."""
        cursor = self.execute_query(query, params)
        return cursor.fetchall() if cursor else None
