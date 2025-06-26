# back/database/connection.py
import pyodbc
from back.config.db_config import db_params

def get_connection():
    try:
        conn_str = (
            f"DRIVER={{{db_params['driver']}}};"
            f"SERVER={db_params['server']};"
            f"DATABASE={db_params['database']};"
            f"UID={db_params['username']};"
            f"PWD={db_params['password']}"
        )
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        print("Erro na conexão com o banco:", e)
        return None
