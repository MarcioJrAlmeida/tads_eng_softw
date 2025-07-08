from flask import Blueprint, request, jsonify
from datetime import datetime
import pandas as pd
import os
import json

from back.database.connection import get_connection
from back.config.db_config import MODO_DESENVOLVIMENTO

dashboard_api = Blueprint("dashboard_api", __name__)

def get_csv_path(nome_arquivo):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    caminho_csv = os.path.join(base_dir, '..', '..', '..', 'banco', 'data', nome_arquivo)
    return os.path.normpath(caminho_csv)


@dashboard_api.route('/dashboard/fechadas', methods=['GET'])
def resumo_respostas_fechadas():
    try:
        if MODO_DESENVOLVIMENTO == "CSV":
            # Leitura de todos os arquivos necessários
            df_avaliacao = pd.read_csv(get_csv_path("Avaliacao.csv"), sep=";", dtype=str)
            df_contem = pd.read_csv(get_csv_path("Contem.csv"), sep=";", dtype=str)
            df_pergunta = pd.read_csv(get_csv_path("Pergunta.csv"), sep=";", dtype=str)
            df_resposta = pd.read_csv(get_csv_path("Resposta.csv"), sep=";", dtype=str)
            df_possui = pd.read_csv(get_csv_path("Possui.csv"), sep=";", dtype=str)
            df_disciplina_docente = pd.read_csv(get_csv_path("Disciplina_Docente.csv"), sep=";", dtype=str)
            df_professor = pd.read_csv(get_csv_path("Professor.csv"), sep=";", dtype=str)
            df_disciplina = pd.read_csv(get_csv_path("Disciplina.csv"), sep=";", dtype=str)
            df_disciplina_curso = pd.read_csv(get_csv_path("Disciplina_Curso.csv"), sep=";", dtype=str)
            df_curso = pd.read_csv(get_csv_path("Curso.csv"), sep=";", dtype=str)

            # Aplicar os joins
            df = df_resposta.merge(df_avaliacao, left_on="idAvaliacao", right_on="id_avaliacao", how="inner")
            df = df.merge(df_pergunta, on="id_pergunta", how="inner")
            df = df[df["tipo_pergunta"] == "Fechada"]

            df = df.merge(df_contem, on=["id_avaliacao", "id_pergunta"], how="inner")
            df = df.merge(df_possui, on="id_resposta", how="inner")
            df = df.merge(df_disciplina_docente, on="id_disciplina_docente", how="inner")
            df = df.merge(df_professor, on="idDisciplina_Docente", how="inner")
            df = df.merge(df_disciplina, on="idDisciplina_Docente", how="inner")
            df = df.merge(df_disciplina_curso, left_on="idDisciplina_Curso", right_on="id_disciplina_curso", how="inner")
            df = df.merge(df_curso, left_on="idCurso", right_on="id_curso", how="inner")

            # Seleciona e renomeia colunas
            df_resultado = df.groupby(
                ["periodo", "nome_curso", "nome_docente", "texto_pergunta", "conteudo_resposta"]
            ).size().reset_index(name="qtd_respostas")

            df_resultado = df_resultado.rename(columns={
                "periodo": "Período",
                "nome_curso": "Curso",
                "nome_docente": "Professor",
                "texto_pergunta": "Pergunta",
                "conteudo_resposta": "Resposta"
            }).sort_values(by=["Período", "Curso", "Professor", "Pergunta", "qtd_respostas"], ascending=[True, True, True, True, False])

            return jsonify(df_resultado.to_dict(orient="records"))

        else:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    a.periodo AS Período,
                    c.nome_curso AS Curso,
                    prof.nome_docente AS Professor,
                    p.texto_pergunta AS Pergunta,
                    r.conteudo_resposta AS Resposta,
                    COUNT(*) AS qtd_respostas
                FROM Avaliacao a
                JOIN Contem cp ON cp.id_avaliacao = a.id_avaliacao
                JOIN Pergunta p ON p.id_pergunta = cp.id_pergunta
                JOIN Resposta r ON r.idAvaliacao = a.id_avaliacao AND r.id_pergunta = p.id_pergunta
                JOIN Possui po ON po.id_resposta = r.id_resposta
                JOIN Disciplina_Docente dd ON dd.id_disciplina_docente = po.id_disciplina_docente
                JOIN Professor prof ON prof.idDisciplina_Docente = dd.id_disciplina_docente
                JOIN Disciplina d ON d.idDisciplina_Docente = dd.id_disciplina_docente
                JOIN Disciplina_Curso dc ON dc.id_disciplina_curso = d.idDisciplina_Curso
                JOIN Curso c ON c.id_curso = dc.idCurso
                WHERE p.tipo_pergunta = 'Fechada'
                GROUP BY a.periodo, c.nome_curso, prof.nome_docente, p.texto_pergunta, r.conteudo_resposta
                ORDER BY a.periodo, c.nome_curso, prof.nome_docente, p.texto_pergunta, qtd_respostas DESC;
            """)

            rows = cursor.fetchall()
            colunas = [column[0] for column in cursor.description]
            resultados = [dict(zip(colunas, row)) for row in rows]

            return jsonify(resultados)

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
