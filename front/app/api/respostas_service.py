from flask import Blueprint, request, jsonify
from datetime import datetime
import pandas as pd
import os
import json

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
        id_disciplina_docente = dados.get("id_disciplina_docente")
        if not id_disciplina_docente:
            return jsonify({"erro": "Campo 'id_disciplina_docente' é obrigatório."}), 400


        # Verificação de campos obrigatórios
        campos_obrigatorios = ['conteudo_resposta', 'idAvaliacao', 'id_pergunta']
        for campo in campos_obrigatorios:
            if campo not in dados:
                return jsonify({"erro": f"Campo '{campo}' é obrigatório."}), 400

        if MODO_DESENVOLVIMENTO == "CSV":
            caminho_resposta = get_csv_path("Resposta.csv")
            caminho_possui = get_csv_path("Possui.csv")

            df_resposta = pd.read_csv(caminho_resposta, sep=';', dtype=str) if os.path.exists(caminho_resposta) else pd.DataFrame(columns=['id_resposta', 'conteudo_resposta', 'data_hr_registro', 'idAvaliacao', 'id_pergunta'])
            df_possui = pd.read_csv(caminho_possui, sep=';', dtype=str) if os.path.exists(caminho_possui) else pd.DataFrame(columns=['id_disciplina_docente', 'id_resposta'])

            id_resposta = df_resposta["id_resposta"].astype(int).max() + 1 if not df_resposta.empty else 1

            nova_resposta = {
                'id_resposta': str(id_resposta),
                'conteudo_resposta': dados['conteudo_resposta'],
                'data_hr_registro': data_hr,
                'idAvaliacao': str(dados['idAvaliacao']),
                'id_pergunta': str(dados['id_pergunta'])
            }
            df_resposta = pd.concat([df_resposta, pd.DataFrame([nova_resposta])], ignore_index=True)
            df_resposta.to_csv(caminho_resposta, sep=';', index=False)

            nova_possui = {
                'id_disciplina_docente': str(id_disciplina_docente),
                'id_resposta': str(id_resposta)
            }
            df_possui = pd.concat([df_possui, pd.DataFrame([nova_possui])], ignore_index=True)
            df_possui.to_csv(caminho_possui, sep=';', index=False)

            return jsonify({"mensagem": "Resposta criada com sucesso (CSV)."}), 201

        else:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT ISNULL(MAX(id_resposta), 0) + 1 FROM Resposta")
            id_resposta = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO Resposta (id_resposta, conteudo_resposta, data_hr_registro, idAvaliacao, id_pergunta)
                VALUES (?, ?, ?, ?, ?)
            """, (
                id_resposta,
                dados['conteudo_resposta'],
                datetime.now(),
                dados['idAvaliacao'],
                dados['id_pergunta']
            ))

            cursor.execute("""
                INSERT INTO Possui (id_disciplina_docente, id_resposta)
                VALUES (?, ?)
            """, (
                id_disciplina_docente,
                id_resposta
            ))

            conn.commit()
            return jsonify({"mensagem": "Resposta criada com sucesso (BD)."}), 201

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
