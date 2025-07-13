# nlp/ml/interface/ml_service.py

from flask import Blueprint, jsonify, request
from nlp.config.connection import get_connection_ml
from back.database.connection import get_connection

ml_api = Blueprint('ml_api', __name__)

@ml_api.route('/respostas/abertas', methods=['GET'])
def lista_respostas_abertas():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT  
                a.id_avaliacao,
                p.texto_pergunta,
                r.conteudo_resposta,
                p.id_pergunta,
                r.id_resposta
            FROM Avaliacao AS a
            JOIN Contem AS c ON a.id_avaliacao = c.id_avaliacao
            JOIN Pergunta AS p ON c.id_pergunta = p.id_pergunta
            JOIN Resposta r ON r.idAvaliacao = a.id_avaliacao AND r.id_pergunta = p.id_pergunta
            WHERE p.tipo_pergunta = 'Aberta'
            AND NOT EXISTS (
                SELECT 1
                FROM [ml_ifpe_sado].[dbo].[Frases_Analisadas] fa
                WHERE fa.id_avaliacao = a.id_avaliacao
                  AND fa.id_pergunta = p.id_pergunta
                  AND fa.id_resposta = r.id_resposta
            )
            ;""")
        colunas = [column[0] for column in cursor.description]
        resultados = [dict(zip(colunas, row)) for row in cursor.fetchall()]
        conn.close()
        return jsonify(resultados), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@ml_api.route('/frases_suspeitas/pendentes', methods=['GET'])
def listar_frases_suspeitas():
    try:
        conn = get_connection_ml()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, id_avaliacao, contexto_pergunta, conteudo_resposta
            FROM Frases_Suspeitas
            WHERE analisada_por_ml = 0
        """)
        colunas = [column[0] for column in cursor.description]
        resultados = [dict(zip(colunas, row)) for row in cursor.fetchall()]
        conn.close()
        return jsonify(resultados), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
@ml_api.route('/frases_suspeitas', methods=['POST'])
def inserir_frase_suspeita():
    try:
        dados = request.json
        conn = get_connection_ml()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO Frases_Suspeitas (
                id_avaliacao, contexto_pergunta, conteudo_resposta,
                metodo_detectado, tipo_suspeita, score, analisada_por_ml, eh_ofensiva, sentimento_previsto, 
                id_pergunta, id_resposta
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            dados['id_avaliacao'], dados['contexto_pergunta'], dados['conteudo_resposta'],
            dados['metodo_detectado'], dados['tipo_suspeita'], dados['score'],
            dados['analisada_por_ml'], dados['eh_ofensiva'], dados['sentimento_previsto'],
            dados['id_pergunta'], dados['id_resposta']
        ))

        conn.commit()
        conn.close()
        return jsonify({"mensagem": "Frase suspeita registrada com sucesso"}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@ml_api.route('/salvar_analise', methods=['POST'])
def salvar_analise():
    try:
        dados = request.json
        conn = get_connection_ml()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO Frases_Analisadas (
                id_avaliacao, contexto_pergunta, conteudo_resposta,
                modelo_utilizado, sentimento_classificado,
                ofensiva, motivo_ofensivo, score, 
                id_pergunta, id_resposta
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            dados['id_avaliacao'], dados['contexto_pergunta'], dados['conteudo_resposta'],
            dados['modelo_utilizado'], dados['sentimento_classificado'],
            int(dados['ofensiva']), dados['motivo_ofensivo'], dados['score'],
            dados['id_pergunta'], dados['id_resposta']
        ))

        cursor.execute("UPDATE Frases_Suspeitas SET analisada_por_ml = 1 WHERE id = ?", dados['id'])
        conn.commit()
        conn.close()
        return jsonify({"mensagem": "Análise salva com sucesso"}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@ml_api.route('/treinamento/ofensividade', methods=['GET'])
def obter_treinamento_manual():
    try:
        conn = get_connection_ml()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, contexto_pergunta, conteudo_resposta, classificada_como_ofensiva,
            classificada_como_sentimento, observacao
            FROM Treinamento_Manual
        """)
        colunas = [column[0] for column in cursor.description]
        resultados = [dict(zip(colunas, row)) for row in cursor.fetchall()]
        conn.close()
        return jsonify(resultados), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
@ml_api.route('/treinamento/ofensividade', methods=['POST'])
def inserir_treinamento_manual():
    try:
        dados = request.json
        conn = get_connection_ml()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO Treinamento_Manual (
                contexto_pergunta, conteudo_resposta,
                classificada_como_ofensiva,
                classificada_como_sentimento,
                observacao
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            dados['contexto_pergunta'],
            dados['conteudo_resposta'],
            dados['classificada_como_ofensiva'],
            dados['classificada_como_sentimento'],
            dados.get('observacao', '')
        ))

        conn.commit()
        conn.close()
        return jsonify({"mensagem": "Treinamento inserido com sucesso"}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
@ml_api.route('/treinamento/sentimento', methods=['GET'])
def obter_treinamento_sentimento():
    try:
        conn = get_connection_ml()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, contexto_pergunta, conteudo_resposta,
            classificada_como_sentimento, observacao
            FROM Treinamento_Sentimento
        """)
        colunas = [column[0] for column in cursor.description]
        resultados = [dict(zip(colunas, row)) for row in cursor.fetchall()]
        conn.close()
        return jsonify(resultados), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
@ml_api.route('/treinamento/sentimento', methods=['POST'])
def inserir_treinamento_sentimento():
    try:
        dados = request.json
        conn = get_connection_ml()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO Treinamento_Sentimento (
                contexto_pergunta, conteudo_resposta,
                classificada_como_sentimento,
                observacao
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            dados['contexto_pergunta'],
            dados['conteudo_resposta'],
            dados['classificada_como_sentimento'],
            dados.get('observacao', '')
        ))

        conn.commit()
        conn.close()
        return jsonify({"mensagem": "Treinamento inserido com sucesso"}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500