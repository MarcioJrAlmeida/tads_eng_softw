from flask import Blueprint, request, jsonify
from datetime import datetime
import pandas as pd
import os

from back.database.connection import get_connection
from back.config.db_config import MODO_DESENVOLVIMENTO

pergunta_api = Blueprint('pergunta_api', __name__)

def get_csv_path(nome_arquivo):
    base_dir = os.path.dirname(os.path.abspath(__file__))  # pasta atual
    caminho_csv = os.path.join(base_dir, '..', '..', '..', 'banco', 'data', nome_arquivo)
    return os.path.normpath(caminho_csv)


@pergunta_api.route('/perguntas', methods=['GET'])
def listar_perguntas():
    try:
        if MODO_DESENVOLVIMENTO == "CSV":
            caminho = get_csv_path("Pergunta.csv")
            df = pd.read_csv(caminho, sep=';')
            perguntas = df.to_dict(orient='records')
            return jsonify(perguntas)
        else:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id_pergunta, texto_pergunta, tipo_pergunta FROM Pergunta")
            perguntas = [
                {
                    "id_pergunta": row.id_pergunta,
                    "texto_pergunta": row.texto_pergunta,
                    "tipo_pergunta": row.tipo_pergunta
                } for row in cursor.fetchall()
            ]
            return jsonify(perguntas)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@pergunta_api.route('/perguntas', methods=['POST'])
def salvar_perguntas():
    try:
        novas_perguntas = request.json
        data_hr = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if MODO_DESENVOLVIMENTO == "CSV":
            caminho = get_csv_path("Pergunta.csv")
            df = pd.read_csv(caminho, sep=';')

            id_atual = df["id_pergunta"].astype(int).max() if not df.empty else 0

            for pergunta in novas_perguntas:
                id_atual += 1
                nova_linha = {
                    "id_pergunta": str(id_atual),
                    "texto_pergunta": pergunta["texto_pergunta"],
                    "tipo_pergunta": pergunta["tipo_pergunta"],
                    "data_hr_registro": data_hr
                }
                df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)

            df.to_csv(caminho, sep=';', index=False)
            return jsonify({"status": "sucesso"}), 201
        else:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT ISNULL(MAX(id_pergunta), 0) FROM Pergunta")
            id_atual = cursor.fetchone()[0]

            for pergunta in novas_perguntas:
                id_atual += 1
                cursor.execute(
                    """
                    INSERT INTO Pergunta (id_pergunta, texto_pergunta, tipo_pergunta, data_hr_registro)
                    VALUES (?, ?, ?, ?)
                    """,
                    id_atual,
                    pergunta['texto_pergunta'],
                    pergunta['tipo_pergunta'],
                    datetime.now()
                )

            conn.commit()
            return jsonify({"status": "sucesso"}), 201

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@pergunta_api.route('/perguntas/<int:id_pergunta>', methods=['PUT'])
def atualizar_pergunta(id_pergunta):
    try:
        dados = request.json

        if MODO_DESENVOLVIMENTO == "CSV":
            caminho = get_csv_path("Pergunta.csv")
            df = pd.read_csv(caminho, sep=';', dtype=str)

            idx = df[df["id_pergunta"] == str(id_pergunta)].index
            if idx.empty:
                return jsonify({"erro": "Pergunta não encontrada"}), 404

            df.loc[idx[0], "texto_pergunta"] = dados["texto_pergunta"]
            df.loc[idx[0], "tipo_pergunta"] = dados["tipo_pergunta"]
            df.to_csv(caminho, sep=';', index=False)
            return jsonify({"status": "pergunta atualizada com sucesso"})
        else:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE Pergunta
                SET texto_pergunta = ?, tipo_pergunta = ?
                WHERE id_pergunta = ?
                """,
                dados['texto_pergunta'],
                dados['tipo_pergunta'],
                id_pergunta
            )

            conn.commit()
            return jsonify({"status": "pergunta atualizada com sucesso"})

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@pergunta_api.route('/perguntas/<int:id_pergunta>', methods=['DELETE'])
def excluir_pergunta(id_pergunta):
    try:
        if MODO_DESENVOLVIMENTO == "CSV":
            caminho = get_csv_path("Pergunta.csv")
            df = pd.read_csv(caminho, sep=';', dtype=str)
            df = df[df["id_pergunta"] != str(id_pergunta)]
            df.to_csv(caminho, sep=';', index=False)
            return jsonify({"mensagem": "Pergunta excluída com sucesso"}), 200
        else:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Pergunta WHERE id_pergunta = ?", id_pergunta)
            conn.commit()
            return jsonify({"mensagem": "Pergunta excluída com sucesso"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
