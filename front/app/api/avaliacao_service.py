from flask import Blueprint, request, jsonify
import pyodbc
from datetime import datetime
import json
import pandas as pd
import os

from back.database.connection import get_connection
from back.config.db_config import MODO_DESENVOLVIMENTO

modelo_avaliacao_api = Blueprint('modelo_avaliacao_api', __name__)
avaliacoes_api = Blueprint('avaliacoes_api', __name__)

def get_csv_path(nome_arquivo):
    base_dir = os.path.dirname(os.path.abspath(__file__))  # pasta atual
    caminho_csv = os.path.join(base_dir, '..', '..', '..', 'banco', 'data', nome_arquivo)
    return os.path.normpath(caminho_csv)

@modelo_avaliacao_api.route('/modelo_avaliacao/<int:id_avaliacao>', methods=['GET'])
def obter_modelo_avaliacao(id_avaliacao):
    try:
        if MODO_DESENVOLVIMENTO == "CSV":
            caminho = get_csv_path("Avaliacao.csv")
            df = pd.read_csv(caminho, sep=';', dtype=str)
            df_filtro = df[df['id_avaliacao'] == str(id_avaliacao)]

            if not df_filtro.empty and pd.notnull(df_filtro.iloc[0]["modelo_avaliacao"]):
                return jsonify(json.loads(df_filtro.iloc[0]["modelo_avaliacao"]))
            else:
                return jsonify({"erro": "Modelo não encontrado ou vazio."}), 404

        else:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT modelo_avaliacao
                FROM Avaliacao
                WHERE id_avaliacao = ?
            """, id_avaliacao)

            row = cursor.fetchone()
            if row and row.modelo_avaliacao:
                return jsonify(json.loads(row.modelo_avaliacao))
            else:
                return jsonify({"erro": "Modelo não encontrado ou vazio."}), 404

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@avaliacoes_api.route('/avaliacoes', methods=['GET'])
def listar_avaliacoes():
    try:
        if MODO_DESENVOLVIMENTO == "CSV":
            caminho = get_csv_path("Avaliacao.csv")
            df = pd.read_csv(caminho, sep=';', dtype=str)

            avaliacoes = []
            for _, row in df.iterrows():
                avaliacoes.append({
                    "id_avaliacao": int(row["id_avaliacao"]),
                    "periodo": row["periodo"],
                    "data_hr_registro": row["data_hr_registro"]
                })

            return jsonify(avaliacoes)

        else:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id_avaliacao, periodo, data_hr_registro
                FROM Avaliacao
                ORDER BY id_avaliacao
            """)
            rows = cursor.fetchall()

            avaliacoes = [
                {
                    "id_avaliacao": row.id_avaliacao,
                    "periodo": row.periodo,
                    "data_hr_registro": row.data_hr_registro.strftime("%Y-%m-%d %H:%M:%S")
                }
                for row in rows
            ]

            return jsonify(avaliacoes)

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@avaliacoes_api.route('/avaliacoes', methods=['POST'])
def criar_avaliacao():
    try:
        dados = request.json
        data_hr = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 

        # Validação básica dos campos
        campos_obrigatorios = ['id_avaliacao', 'periodo', 'data_hr_registro', 'idDiretor', 'modelo_avaliacao']
        for campo in campos_obrigatorios:
            if campo not in dados:
                return jsonify({"erro": f"Campo '{campo}' é obrigatório."}), 400

        if MODO_DESENVOLVIMENTO == "CSV":
            caminho = get_csv_path("Avaliacao.csv")
            
            # Verifica se o arquivo já existe para carregar
            if os.path.exists(caminho):
                df = pd.read_csv(caminho, sep=';', dtype=str)
            else:
                df = pd.DataFrame(columns=campos_obrigatorios)

            nova_linha = {
                'id_avaliacao': int(dados['id_avaliacao']),
                'periodo': int(dados['periodo']),
                'data_hr_registro': data_hr,
                'idDiretor': int(dados['idDiretor']),
                'modelo_avaliacao': json.dumps(dados['modelo_avaliacao'])
            }

            df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
            df.to_csv(caminho, sep=';', index=False)

            return jsonify({"mensagem": "Avaliação criada com sucesso (CSV)."}), 201

        else:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO Avaliacao (id_avaliacao, periodo, data_hr_registro, idDiretor, modelo_avaliacao)
                VALUES (?, ?, ?, ?, ?)
            """, (
                dados['id_avaliacao'],
                dados['periodo'],
                datetime.now(),
                dados['idDiretor'],
                json.dumps(dados['modelo_avaliacao'])
            ))

            conn.commit()
            return jsonify({"mensagem": "Avaliação criada com sucesso (BD)."}), 201

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
