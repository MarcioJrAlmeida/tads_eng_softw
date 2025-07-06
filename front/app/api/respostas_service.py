from flask import Blueprint, request, jsonify
from datetime import datetime
import json
import pandas as pd
import os

from back.database.connection import get_connection
from back.config.db_config import MODO_DESENVOLVIMENTO

inserir_resposta_api = Blueprint('inserir_resposta_api', __name__)

def get_csv_path(nome_arquivo):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    caminho_csv = os.path.join(base_dir, '..', '..', '..', 'banco', 'data', nome_arquivo)
    return os.path.normpath(caminho_csv)

@inserir_resposta_api.route('/resposta', methods=['POST'])
def inserir_resposta():
    try:
        dados = request.json
        data_hr = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 

        campos_obrigatorios = ['id_resposta', 'conteudo_resposta', 'data_hr_registro', 'idAvaliacao']
        for campo in campos_obrigatorios:
            if campo not in dados:
                return jsonify({"erro": f"Campo '{campo}' é obrigatório."}), 400

        if MODO_DESENVOLVIMENTO == "CSV":
            caminho = get_csv_path("Resposta.csv")

            if os.path.exists(caminho):
                df = pd.read_csv(caminho, sep=';', dtype=str)
            else:
                df = pd.DataFrame(columns=campos_obrigatorios)

            nova_linha = {
                'id_resposta': int(dados['id_resposta']),
                'conteudo_resposta': dados['conteudo_resposta'],
                'data_hr_registro': data_hr,
                'idAvaliacao': int(dados['idAvaliacao'])
            }

            df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
            df.to_csv(caminho, sep=';', index=False)

            return jsonify({"mensagem": "Resposta criada com sucesso (CSV)."}), 201

        else:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO Resposta (id_resposta, conteudo_resposta, data_hr_registro, idAvaliacao)
                VALUES (?, ?, ?, ?)
            """, (
                dados['id_resposta'],
                dados['conteudo_resposta'],
                datetime.now(),
                dados['idAvaliacao']
            ))

            conn.commit()
            return jsonify({"mensagem": "Resposta criada com sucesso (BD)."}), 201

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
