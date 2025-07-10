from flask import Blueprint, request, jsonify
from datetime import datetime
import pandas as pd
import os
import json

from back.database.connection import get_connection
from back.config.db_config import MODO_DESENVOLVIMENTO

disciplina_api = Blueprint("disciplina_api", __name__)

def get_csv_path(nome_arquivo):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    caminho_csv = os.path.join(base_dir, '..', '..', '..', 'banco', 'data', nome_arquivo)
    return os.path.normpath(caminho_csv)

@disciplina_api.route('/curso', methods=['GET'])
def listar_cursos():
    try:
        if MODO_DESENVOLVIMENTO == "CSV":
            df = pd.read_csv(get_csv_path("Curso.csv"), sep=';', dtype=str)
            return jsonify(df.to_dict(orient='records'))
        else:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id_curso, nome_curso, idTurma FROM Curso")
            resultados = [
                {"id_curso": r.id_curso, "nome_curso": r.nome_curso, "idTurma": r.idTurma}
                for r in cursor.fetchall()
            ]
            return jsonify(resultados)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@disciplina_api.route('/disciplinas', methods=['GET'])
def listar_disciplinas():
    try:
        if MODO_DESENVOLVIMENTO == "CSV":
            df = pd.read_csv(get_csv_path("Disciplina.csv"), sep=';', dtype=str)
            return jsonify(df.to_dict(orient='records'))
        else:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id_disciplina, nome_disciplina, idDisciplina_Docente FROM Disciplina")
            resultados = [
                {"id_disciplina": r.id_disciplina, "nome_disciplina": r.nome_disciplina, "idDisciplina_Docente": r.idDisciplina_Docente}
                for r in cursor.fetchall()
            ]
            return jsonify(resultados)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@disciplina_api.route('/docentes', methods=['GET'])
def listar_docentes():
    try:
        if MODO_DESENVOLVIMENTO == "CSV":
            df = pd.read_csv(get_csv_path("Professor.csv"), sep=';', dtype=str)
            return jsonify(df.to_dict(orient='records'))
        else:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id_professor, nome_docente, idDisciplina_Docente FROM Professor")
            resultados = [
                {"id_professor": r.id_professor, "nome_docente": r.nome_docente, "idDisciplina_Docente": r.idDisciplina_Docente}
                for r in cursor.fetchall()
            ]
            return jsonify(resultados)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@disciplina_api.route('/disciplinas_docente', methods=['GET'])
def listar_disciplinas_docente():
    try:
        if MODO_DESENVOLVIMENTO == "CSV":
            df = pd.read_csv(get_csv_path("Disciplina_Docente.csv"), sep=';', dtype=str)
            return jsonify(df.to_dict(orient='records'))
        else:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                           SELECT dd.[id_disciplina_docente]
                               ,prof.nome_docente
                         	  ,d.nome_disciplina
                           FROM Disciplina_Docente as dd
                           LEFT JOIN Professor as prof
                           ON dd.id_disciplina_docente = prof.idDisciplina_Docente
                           LEFT JOIN Disciplina as d
                           ON d.idDisciplina_Docente = prof.idDisciplina_Docente
                           """)
            resultados = [
                {"id_disciplina_docente": r.id_disciplina_docente, "nome_docente": r.nome_docente, "nome_disciplina": r.nome_disciplina}
                for r in cursor.fetchall()
            ]
            return jsonify(resultados)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@disciplina_api.route('/docentes_avaliados', methods=['GET'])
def docentes_avaliados():
    try:
        id_avaliacao = request.args.get('id_avaliacao', type=str)

        if not id_avaliacao or id_avaliacao.strip() == "":
            return jsonify({"erro": "Parâmetro 'id_avaliacao' não fornecido ou vazio."}), 400

        # Modo CSV
        if MODO_DESENVOLVIMENTO == "CSV":
            resposta_df = pd.read_csv(get_csv_path("Resposta.csv"), sep=";", dtype=str)
            possui_df = pd.read_csv(get_csv_path("Possui.csv"), sep=";", dtype=str)

            # Garantir consistência de tipo
            resposta_df["idAvaliacao"] = resposta_df["idAvaliacao"].astype(str)
            possui_df["id_resposta"] = possui_df["id_resposta"].astype(str)

            # Filtrar as respostas da avaliação
            resposta_filtrada = resposta_df[resposta_df["idAvaliacao"] == id_avaliacao]

            # Juntar com a tabela Possui
            merge_df = pd.merge(possui_df, resposta_filtrada, on="id_resposta", how="inner")

            ids = merge_df["id_disciplina_docente"].dropna().unique().tolist()
            ids = [int(x) for x in ids if str(x).isdigit()]

            return jsonify(ids), 200

        # Modo Banco de Dados
        else:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT p.id_disciplina_docente
                FROM Possui AS p
                INNER JOIN Resposta AS r ON p.id_resposta = r.id_resposta
                WHERE r.idAvaliacao = ?
            """, (id_avaliacao,))
            dados = cursor.fetchall()

            ids = [int(row[0]) for row in dados if row[0] is not None]
            return jsonify(ids), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
