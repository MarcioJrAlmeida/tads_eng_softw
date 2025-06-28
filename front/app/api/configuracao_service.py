from flask import Blueprint, request, jsonify
from datetime import datetime
import json
import pandas as pd
import pyodbc
import os

from back.database.connection import get_connection
from back.config.db_config import MODO_DESENVOLVIMENTO

configuracao_api = Blueprint('configuracao_api', __name__)

def get_csv_path(nome_arquivo):
    base_dir = os.path.dirname(os.path.abspath(__file__))  # pasta atual
    caminho_csv = os.path.join(base_dir, '..', '..', '..', 'banco', 'data', nome_arquivo)
    return os.path.normpath(caminho_csv)

@configuracao_api.route('/configuracao_formulario', methods=['POST'])
def configurar_formulario():
    try:
        dados = request.json
        ordem_perguntas = dados.get("ordem_perguntas", [])
        qtd_perguntas_exibir = dados.get("qtd_perguntas_exibir", 0)
        id_avaliacao = dados.get("id_avaliacao")

        if not id_avaliacao:
            return jsonify({"erro": "id_avaliacao é obrigatório"}), 400

        modelo_json = json.dumps({
            "ordem_perguntas": ordem_perguntas,
            "qtd_perguntas_exibir": qtd_perguntas_exibir
        })

        data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if MODO_DESENVOLVIMENTO == "CSV":
            caminho = get_csv_path("Avaliacao.csv")
            df = pd.read_csv(caminho, sep=';', dtype=str)

            idx = df[df["id_avaliacao"] == str(id_avaliacao)].index
            if idx.empty:
                return jsonify({"erro": "id_avaliacao não encontrado no CSV"}), 404

            df.loc[idx[0], "modelo_avaliacao"] = modelo_json
            df.loc[idx[0], "data_hr_registro"] = data_atual

            df.to_csv(caminho, sep=';', index=False)
            return jsonify({"mensagem": "Configuração salva no CSV com sucesso!"}), 200

        else:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE Avaliacao
                SET modelo_avaliacao = ?, data_hr_registro = ?
                WHERE id_avaliacao = ?
            """, modelo_json, datetime.now(), id_avaliacao)

            conn.commit()
            return jsonify({"mensagem": "Configuração salva com sucesso!"}), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
