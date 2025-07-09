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
            cursor.execute("SELECT id_disciplina_docente, data_hr_registro FROM Disciplina_Docente")
            resultados = [
                {"id_disciplina_docente": r.id_disciplina_docente, "data_hr_registro": r.data_hr_registro.strftime('%Y-%m-%d %H:%M:%S')}
                for r in cursor.fetchall()
            ]
            return jsonify(resultados)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
