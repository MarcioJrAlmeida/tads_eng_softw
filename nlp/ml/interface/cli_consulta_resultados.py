# back/interface/cli_consulta_resultados.py

import pyodbc
from config.db_config_ml import db_params


def conectar_sql_server():
    conn_str = (
        f"DRIVER={db_params['driver']};"
        f"SERVER={db_params['server']};"
        f"DATABASE={db_params['database']};"
        f"UID={db_params['username']};"
        f"PWD={db_params['password']}"
    )
    return pyodbc.connect(conn_str)


def consultar_resultados():
    conn = conectar_sql_server()
    cursor = conn.cursor()

    query = """
        SELECT TOP 20 id, contexto_pergunta, conteudo_resposta, metodo_detectado,
               tipo_suspeita, eh_ofensiva, sentimento_previsto, data_registro
        FROM Frases_Suspeitas
        ORDER BY data_registro DESC
    """

    cursor.execute(query)
    resultados = cursor.fetchall()

    print("\n📝 Últimas 20 Frases Classificadas:\n")
    for row in resultados:
        print(f"ID: {row.id}")
        print(f"Pergunta: {row.contexto_pergunta}")
        print(f"Resposta: {row.conteudo_resposta}")
        print(f"Método: {row.metodo_detectado} | Tipo: {row.tipo_suspeita}")
        print(f"Ofensiva: {'Sim' if row.eh_ofensiva else 'Não'} | Sentimento: {row.sentimento_previsto}")
        print(f"Data: {row.data_registro.strftime('%Y-%m-%d %H:%M')}\n")

    conn.close()


if __name__ == "__main__":
    consultar_resultados()
