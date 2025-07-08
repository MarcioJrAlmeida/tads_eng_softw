from flask import Blueprint, request, jsonify
from datetime import datetime
import pandas as pd
import os
import json

from back.database.connection import get_connection
from back.config.db_config import MODO_DESENVOLVIMENTO

discente_api = Blueprint("discente_api", __name__)

def get_csv_path(nome_arquivo):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    caminho_csv = os.path.join(base_dir, '..', '..', '..', 'banco', 'data', nome_arquivo)
    return os.path.normpath(caminho_csv)

@discente_api.route('/alunos', methods=['GET'])
def listar_alunos():
    try:
        if MODO_DESENVOLVIMENTO == "CSV":
            df = pd.read_csv(get_csv_path("Aluno.csv"), sep=';', dtype=str)
            return jsonify(df.to_dict(orient='records'))
        else:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT matricula, email FROM Aluno")
            resultados = [
                {"matricula": r.matricula, "email": r.email}
                for r in cursor.fetchall()
            ]
            return jsonify(resultados)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
@discente_api.route('/alunos/turma', methods=['GET'])
def listar_turma():
    try:
        if MODO_DESENVOLVIMENTO == "CSV":
            df = pd.read_csv(get_csv_path("Turma_Aluno.csv"), sep=';', dtype=str)
            return jsonify(df.to_dict(orient='records'))
        else:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id_turma, idAluno FROM Turma_Aluno")
            resultados = [
                {"id_turma": r.id_turma, "idAluno": r.idAluno}
                for r in cursor.fetchall()
            ]
            return jsonify(resultados)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
@discente_api.route('/alunos/turma/curso', methods=['GET'])
def listar_turma_curso():
    try:
        if MODO_DESENVOLVIMENTO == "CSV":
            df = pd.read_csv(get_csv_path("Turma.csv"), sep=';', dtype=str)
            return jsonify(df.to_dict(orient='records'))
        else:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id_turma, idCurso FROM Turma")
            resultados = [
                {"id_turma": r.id_turma, "idCurso": r.idCurso}
                for r in cursor.fetchall()
            ]
            return jsonify(resultados)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500