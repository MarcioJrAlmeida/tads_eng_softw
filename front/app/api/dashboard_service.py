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
            df_avaliacao = pd.read_csv(get_csv_path("Avaliacao.csv"), sep=";", dtype=str)[["id_avaliacao", "periodo"]]
            df_contem = pd.read_csv(get_csv_path("Contem.csv"), sep=";", dtype=str)[["id_avaliacao", "id_pergunta"]]
            df_pergunta = pd.read_csv(get_csv_path("Pergunta.csv"), sep=";", dtype=str)[["id_pergunta", "texto_pergunta", "tipo_pergunta"]]
            df_resposta = pd.read_csv(get_csv_path("Resposta.csv"), sep=";", dtype=str)[["id_resposta", "idAvaliacao", "id_pergunta", "conteudo_resposta"]]
            df_possui = pd.read_csv(get_csv_path("Possui.csv"), sep=";", dtype=str)[["id_resposta", "id_disciplina_docente"]]
            df_disciplina_docente = pd.read_csv(get_csv_path("Disciplina_Docente.csv"), sep=";", dtype=str)[["id_disciplina_docente"]]
            df_professor = pd.read_csv(get_csv_path("Professor.csv"), sep=";", dtype=str)[["idDisciplina_Docente", "nome_docente"]]
            df_disciplina = pd.read_csv(get_csv_path("Disciplina.csv"), sep=";", dtype=str)[["idDisciplina_Docente", "idDisciplina_Curso"]]
            df_disciplina_curso = pd.read_csv(get_csv_path("Disciplina_Curso.csv"), sep=";", dtype=str)[["id_disciplina_curso", "idCurso"]]
            df_curso = pd.read_csv(get_csv_path("Curso.csv"), sep=";", dtype=str)[["id_curso", "nome_curso"]]

            # Aplicar os joins
            df = df_resposta.merge(df_avaliacao, left_on="idAvaliacao", right_on="id_avaliacao", how="inner")
            df = df.merge(df_pergunta, on="id_pergunta", how="inner")
            df = df[df["tipo_pergunta"] == "Fechada"]

            df = df.merge(df_contem, on=["id_avaliacao", "id_pergunta"], how="inner")
            df = df.merge(df_possui, on="id_resposta", how="inner")
            df = df.merge(df_disciplina_docente, on="id_disciplina_docente", how="inner")
            df = df.merge(df_professor, left_on="id_disciplina_docente", right_on="idDisciplina_Docente", how="inner")
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

@dashboard_api.route('/dashboard/abertas', methods=['GET'])
def resumo_respostas_abertas():
    try:
        if MODO_DESENVOLVIMENTO == "CSV":
            # Leitura apenas das colunas utilizadas
            df_avaliacao = pd.read_csv(get_csv_path("Avaliacao.csv"), sep=";", dtype=str)[["id_avaliacao", "periodo"]]
            df_contem = pd.read_csv(get_csv_path("Contem.csv"), sep=";", dtype=str)[["id_avaliacao", "id_pergunta"]]
            df_pergunta = pd.read_csv(get_csv_path("Pergunta.csv"), sep=";", dtype=str)[["id_pergunta", "texto_pergunta", "tipo_pergunta"]]
            df_resposta = pd.read_csv(get_csv_path("Resposta.csv"), sep=";", dtype=str)[["id_resposta", "idAvaliacao", "id_pergunta", "conteudo_resposta"]]
            df_possui = pd.read_csv(get_csv_path("Possui.csv"), sep=";", dtype=str)[["id_resposta", "id_disciplina_docente"]]
            df_disciplina_docente = pd.read_csv(get_csv_path("Disciplina_Docente.csv"), sep=";", dtype=str)[["id_disciplina_docente"]]
            df_professor = pd.read_csv(get_csv_path("Professor.csv"), sep=";", dtype=str)[["idDisciplina_Docente", "nome_docente"]]
            df_disciplina = pd.read_csv(get_csv_path("Disciplina.csv"), sep=";", dtype=str)[["idDisciplina_Docente", "idDisciplina_Curso"]]
            df_disciplina_curso = pd.read_csv(get_csv_path("Disciplina_Curso.csv"), sep=";", dtype=str)[["id_disciplina_curso", "idCurso"]]
            df_curso = pd.read_csv(get_csv_path("Curso.csv"), sep=";", dtype=str)[["id_curso", "nome_curso"]]

            # Joins encadeados
            df = df_resposta.merge(df_avaliacao, left_on="idAvaliacao", right_on="id_avaliacao", how="inner")
            df = df.merge(df_pergunta, on="id_pergunta", how="inner")
            df = df[df["tipo_pergunta"] == "Aberta"]  # <- aqui é "Aberta" pois é /dashboard/abertas

            df = df.merge(df_contem, on=["id_avaliacao", "id_pergunta"], how="inner")
            df = df.merge(df_possui, on="id_resposta", how="inner")
            df = df.merge(df_disciplina_docente, on="id_disciplina_docente", how="inner")
            df = df.merge(df_professor, left_on="id_disciplina_docente", right_on="idDisciplina_Docente", how="inner")
            df = df.merge(df_disciplina, on="idDisciplina_Docente", how="inner")
            df = df.merge(df_disciplina_curso, left_on="idDisciplina_Curso", right_on="id_disciplina_curso", how="inner")
            df = df.merge(df_curso, left_on="idCurso", right_on="id_curso", how="inner")

            # Carga do Frases_Analisadas
            df_frases = pd.read_csv(get_csv_path("Frases_Analisadas.csv"), sep=";", dtype=str)[[
                "id_avaliacao", "id_pergunta", "id_resposta", "modelo_utilizado", "sentimento_classificado", "score"
            ]]

            df = df.merge(
                df_frases,
                on=["id_avaliacao", "id_pergunta", "id_resposta"],
                how="inner"
            )

            # Agrupamento e renomeação
            df["score"] = df["score"].str.replace(",", ".", regex=False).astype(float)  # garantir tipo para média

            df_resultado = df.groupby([
                "periodo", "nome_curso", "nome_docente", "texto_pergunta", "conteudo_resposta",
                "modelo_utilizado", "sentimento_classificado"
            ]).agg(
                qtd_respostas=("id_resposta", "count"),
                media_score=("score", "mean")
            ).reset_index()

            df_resultado = df_resultado.rename(columns={
                "periodo": "Período",
                "nome_curso": "Curso",
                "nome_docente": "Professor",
                "texto_pergunta": "Pergunta",
                "conteudo_resposta": "Resposta",
                "modelo_utilizado": "Modelo",
                "sentimento_classificado": "Sentimento"
            }).sort_values(by=["Professor", "Sentimento"])

            return jsonify(df_resultado.to_dict(orient="records"))
        
        else:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                WITH cte_respostas_analisadas AS (
                    SELECT  
                        a.periodo AS Período,
                        c.nome_curso AS Curso,
                        prof.nome_docente AS Professor,
                        p.texto_pergunta AS Pergunta,
                        r.conteudo_resposta AS Resposta,
                        fa.modelo_utilizado AS Modelo,
                        fa.sentimento_classificado AS Sentimento,
                        fa.score
                    FROM Avaliacao AS a
                    JOIN Contem AS co ON a.id_avaliacao = co.id_avaliacao
                    JOIN Pergunta AS p ON co.id_pergunta = p.id_pergunta
                    JOIN Resposta r ON r.idAvaliacao = a.id_avaliacao AND r.id_pergunta = p.id_pergunta
                    JOIN Possui po ON po.id_resposta = r.id_resposta
                    JOIN Disciplina_Docente dd ON dd.id_disciplina_docente = po.id_disciplina_docente
                    JOIN Professor prof ON prof.idDisciplina_Docente = dd.id_disciplina_docente
                    JOIN Disciplina d ON d.idDisciplina_Docente = dd.id_disciplina_docente
                    JOIN Disciplina_Curso dc ON dc.id_disciplina_curso = d.idDisciplina_Curso
                    JOIN Curso c ON c.id_curso = dc.idCurso
                    JOIN [ml_ifpe_sado].[dbo].[Frases_Analisadas] fa
                        ON fa.id_avaliacao = a.id_avaliacao 
                       AND fa.id_pergunta = p.id_pergunta 
                       AND fa.id_resposta = r.id_resposta
                    WHERE p.tipo_pergunta = 'Aberta'
                )
                -- Consulta principal de exemplo
                SELECT 
                	Período,
                	Curso,
                	Pergunta,
                	Resposta,
                    Professor,
                    Modelo,
                    Sentimento,
                    COUNT(*) AS qtd_respostas,
                    AVG(score) AS media_score
                FROM cte_respostas_analisadas
                GROUP BY 
                Período,
                Curso,
                Pergunta,
                Resposta,
                Professor, 
                Modelo,
                Sentimento
                ORDER BY Professor, Sentimento;
            """)

            rows = cursor.fetchall()
            colunas = [column[0] for column in cursor.description]
            resultados = [dict(zip(colunas, row)) for row in rows]

            return jsonify(resultados)

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
