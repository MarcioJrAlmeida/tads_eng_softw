from flask import Blueprint, request, jsonify
import pyodbc
from datetime import datetime

from back.database.connection import get_connection

pergunta_api = Blueprint('pergunta_api', __name__)

@pergunta_api.route('/perguntas', methods=['GET'])
def listar_perguntas():
    try:
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
