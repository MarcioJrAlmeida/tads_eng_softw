import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from back.database.connection import get_connection
from back.database.queries import BUSCAR_ALUNOS

def listar_alunos():
    conn = get_connection()
    if not conn:
        print("Conexão falhou.")
        return

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT matricula, email, data_hr_registro FROM Aluno")

        print("\n📋 Lista de Alunos:")
        for row in cursor.fetchall():
            print(f"Matricula: {row.matricula} | E-mail: {row.email} | Dt_hr_Registro: {row.data_hr_registro}")

        conn.close()

    except Exception as e:
        print("Erro ao executar SELECT:", e)

if __name__ == "__main__":
    listar_alunos()