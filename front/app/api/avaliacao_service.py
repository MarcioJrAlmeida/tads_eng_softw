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
                    "data_hr_registro": row["data_hr_registro"],
                    "status_avaliacao": row["status_avaliacao"],
                    "data_lancamento": row["data_lancamento"]
                })

            return jsonify(avaliacoes)

        else:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id_avaliacao, periodo, data_hr_registro, status_avaliacao, data_lancamento
                FROM Avaliacao
                ORDER BY id_avaliacao
            """)
            rows = cursor.fetchall()

            avaliacoes = [
                {
                    "id_avaliacao": row.id_avaliacao,
                    "periodo": row.periodo,
                    "data_hr_registro": row.data_hr_registro.strftime("%Y-%m-%d %H:%M:%S"),
                    "status_avaliacao": row.status_avaliacao,
                    "data_lancamento": row.data_lancamento
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

        # Validar campos obrigatórios (exceto id, data e diretor)
        if 'periodo' not in dados or 'modelo_avaliacao' not in dados:
            return jsonify({"erro": "Campos 'periodo' e 'modelo_avaliacao' são obrigatórios."}), 400

        periodo = int(dados['periodo'])
        modelo_avaliacao = dados['modelo_avaliacao']
        idDiretor = 1  # fixo por enquanto

        if MODO_DESENVOLVIMENTO == "CSV":
            caminho = get_csv_path("Avaliacao.csv")

            if os.path.exists(caminho):
                df = pd.read_csv(caminho, sep=';', dtype=str)
                max_id = df["id_avaliacao"].astype(int).max() if not df.empty else 0
            else:
                df = pd.DataFrame(columns=["id_avaliacao", "periodo", "data_hr_registro", "idDiretor", "modelo_avaliacao", "status_avaliacao", "data_lancamento"])
                max_id = 0

            novo_id = max_id + 1

            nova_linha = {
                'id_avaliacao': str(novo_id),
                'periodo': str(periodo),
                'data_hr_registro': data_hr,
                'idDiretor': str(idDiretor),
                'modelo_avaliacao': json.dumps(modelo_avaliacao),
                'status_avaliacao': 'Inativo',
                'data_lancamento': 'NULL'
            }

            df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
            df.to_csv(caminho, sep=';', index=False)

            return jsonify({"mensagem": "Avaliação criada com sucesso (CSV)."}), 201

        else:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT ISNULL(MAX(id_avaliacao), 0) FROM Avaliacao")
            max_id = cursor.fetchone()[0]
            novo_id = max_id + 1
            
            data_lancamento = dados.get("data_lancamento")  # pode vir em string ISO
            data_lancamento = datetime.fromisoformat(data_lancamento) if data_lancamento else None

            cursor.execute("""
                INSERT INTO Avaliacao (id_avaliacao, periodo, data_hr_registro, idDiretor, modelo_avaliacao)
                VALUES (?, ?, ?, ?, ?)
            """, (
                novo_id,
                periodo,
                datetime.now(),
                idDiretor,
                json.dumps(modelo_avaliacao)
            ))

            conn.commit()
            return jsonify({
                    "mensagem": "Avaliação criada com sucesso (BD).",
                    "id_avaliacao": novo_id
                }), 201


    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
@avaliacoes_api.route('/avaliacoes/<int:id_avaliacao>/modelo', methods=['PUT'])
def atualizar_modelo_avaliacao(id_avaliacao):
    try:
        dados = request.json
        modelo = dados.get("modelo_avaliacao")
        if not modelo:
            return jsonify({"erro": "modelo_avaliacao é obrigatório"}), 400

        if MODO_DESENVOLVIMENTO == "CSV":
            # Caminho do CSV
            caminho_csv = get_csv_path("Avaliacao.csv")
            df = pd.read_csv(caminho_csv, sep=";", dtype=str)

            # Verifica se o ID existe
            if str(id_avaliacao) not in df["id_avaliacao"].values:
                return jsonify({"erro": "Avaliação não encontrada"}), 404

            # Atualiza a coluna modelo_avaliacao como JSON
            df.loc[df["id_avaliacao"] == str(id_avaliacao), "modelo_avaliacao"] = json.dumps(modelo)

            # Sobrescreve o CSV
            df.to_csv(caminho_csv, sep=";", index=False)

            return jsonify({"mensagem": "Modelo atualizado com sucesso (CSV)"}), 200

        else:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Avaliacao
                SET modelo_avaliacao = ?
                WHERE id_avaliacao = ?
            """, (json.dumps(modelo), id_avaliacao))
            conn.commit()

            return jsonify({"mensagem": "Modelo atualizado com sucesso"}), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500



@avaliacoes_api.route('/avaliacoes/<int:id_avaliacao>/status', methods=['PUT'])
def atualizar_status_avaliacao(id_avaliacao):
    try:
        novo_status = request.json.get("status_avaliacao")
        dt_lancamento = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if novo_status not in ["Ativo", "Inativo"]:
            return jsonify({"erro": "Status inválido. Use 'Ativo' ou 'Inativo'."}), 400

        if MODO_DESENVOLVIMENTO == "CSV":
            caminho_csv = get_csv_path("Avaliacao.csv")
            df = pd.read_csv(caminho_csv, sep=";", dtype=str)

            df["id_avaliacao"] = df["id_avaliacao"].astype(str)
            if str(id_avaliacao) not in df["id_avaliacao"].values:
                return jsonify({"erro": "Avaliação não encontrada."}), 404

            # Define todas como Inativo
            df["status_avaliacao"] = "Inativo"

            # Atualiza o status e a data da avaliação específica
            df.loc[df["id_avaliacao"] == str(id_avaliacao), "status_avaliacao"] = novo_status
            df.loc[df["id_avaliacao"] == str(id_avaliacao), "data_lancamento"] = dt_lancamento

            # Salva o CSV atualizado
            df.to_csv(caminho_csv, sep=";", index=False)

            return jsonify({"mensagem": f"Avaliação {id_avaliacao} atualizada para {novo_status} (CSV)."}), 200

        else:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                dt_lancamento = datetime.now()

                # Define todas como Inativo
                cursor.execute("UPDATE Avaliacao SET status_avaliacao = 'Inativo'")

                # Atualiza a específica
                cursor.execute("""
                    UPDATE Avaliacao 
                    SET status_avaliacao = ?, data_lancamento = ? 
                    WHERE id_avaliacao = ?
                """, (novo_status, dt_lancamento, id_avaliacao))

                conn.commit()

                return jsonify({"mensagem": f"Avaliação {id_avaliacao} atualizada para {novo_status}."}), 200
        
            except Exception as e:
                import traceback
                traceback.print_exc()
                return jsonify({"erro": str(e)}), 500

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@avaliacoes_api.route('/avaliacoes/<int:id_avaliacao>/vincular_perguntas', methods=['PUT'])
def vincular_perguntas(id_avaliacao):
    try:
        dados = request.json
        lista_perguntas = dados.get("id_perguntas", [])

        if not lista_perguntas:
            return jsonify({"erro": "Lista de perguntas vazia"}), 400

        if MODO_DESENVOLVIMENTO == "CSV":
            caminho_csv = get_csv_path("Contem.csv")
            df_contem = pd.read_csv(caminho_csv, sep=";", dtype=str)

            # Obter perguntas já vinculadas à avaliação
            perguntas_existentes = df_contem[df_contem["id_avaliacao"] == str(id_avaliacao)]["id_pergunta"].tolist()

            # Determinar perguntas a inserir e remover
            perguntas_a_inserir = list(set(lista_perguntas) - set(perguntas_existentes))
            perguntas_a_remover = list(set(perguntas_existentes) - set(lista_perguntas))

            # Remover perguntas desmarcadas
            df_contem = df_contem[~(
                (df_contem["id_avaliacao"] == str(id_avaliacao)) &
                (df_contem["id_pergunta"].isin(perguntas_a_remover))
            )]

            # Inserir novas perguntas
            novos_registros = pd.DataFrame([{
                "id_avaliacao": str(id_avaliacao),
                "id_pergunta": str(idp)
            } for idp in perguntas_a_inserir])

            df_contem = pd.concat([df_contem, novos_registros], ignore_index=True)

            # Salvar arquivo atualizado
            df_contem.to_csv(caminho_csv, sep=";", index=False)

            return jsonify({
                "mensagem": f"Perguntas atualizadas para a avaliação {id_avaliacao}. (CSV)",
                "inseridas": perguntas_a_inserir,
                "removidas": perguntas_a_remover
            }), 200

        else:
            conn = get_connection()
            cursor = conn.cursor()

            # Obter perguntas já existentes
            cursor.execute("SELECT id_pergunta FROM Contem WHERE id_avaliacao = ?", (id_avaliacao,))
            perguntas_existentes = [row.id_pergunta for row in cursor.fetchall()]

            # Determinar perguntas a inserir e remover
            perguntas_a_inserir = list(set(lista_perguntas) - set(perguntas_existentes))
            perguntas_a_remover = list(set(perguntas_existentes) - set(lista_perguntas))

            # Remover perguntas desmarcadas
            for id_pergunta in perguntas_a_remover:
                cursor.execute("""
                    DELETE FROM Contem 
                    WHERE id_avaliacao = ? AND id_pergunta = ?
                """, (id_avaliacao, id_pergunta))

            # Inserir novas perguntas
            for id_pergunta in perguntas_a_inserir:
                cursor.execute("""
                    INSERT INTO Contem (id_avaliacao, id_pergunta) 
                    VALUES (?, ?)
                """, (id_avaliacao, id_pergunta))

            conn.commit()

            return jsonify({
                "mensagem": f"Perguntas atualizadas para a avaliação {id_avaliacao}.",
                "inseridas": perguntas_a_inserir,
                "removidas": perguntas_a_remover
            }), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@avaliacoes_api.route('/avaliacoes/<int:id_avaliacao>/criar_vinculo_perguntas', methods=['POST'])
def vincular_pergunta_a_avaliacao_nova(id_avaliacao):
    try:
        dados = request.json
        lista_perguntas = dados.get("id_perguntas", [])

        if not lista_perguntas or not isinstance(lista_perguntas, list):
            return jsonify({"erro": "Lista de perguntas vazia ou inválida."}), 400

        # Normaliza os IDs
        lista_perguntas = [int(p) for p in lista_perguntas]

        if MODO_DESENVOLVIMENTO == "CSV":
            caminho_csv = get_csv_path("Contem.csv")
            df_contem = pd.read_csv(caminho_csv, sep=";", dtype=str)

            perguntas_existentes = df_contem[df_contem["id_avaliacao"] == str(id_avaliacao)]["id_pergunta"].astype(int).tolist()

            perguntas_a_inserir = list(set(lista_perguntas) - set(perguntas_existentes))
            perguntas_a_remover = list(set(perguntas_existentes) - set(lista_perguntas))

            # Remove as que foram desmarcadas
            df_contem = df_contem[~(
                (df_contem["id_avaliacao"] == str(id_avaliacao)) &
                (df_contem["id_pergunta"].astype(int).isin(perguntas_a_remover))
            )]

            # Adiciona as novas
            novos_registros = pd.DataFrame([{
                "id_avaliacao": str(id_avaliacao),
                "id_pergunta": str(idp)
            } for idp in perguntas_a_inserir])

            df_contem = pd.concat([df_contem, novos_registros], ignore_index=True)
            df_contem.to_csv(caminho_csv, sep=";", index=False)

            return jsonify({
                "mensagem": f"Perguntas atualizadas para a avaliação {id_avaliacao}. (CSV)",
                "inseridas": perguntas_a_inserir,
                "removidas": perguntas_a_remover
            }), 200

        else:
            conn = get_connection()
            cursor = conn.cursor()

            # (Opcional) Verifica se a avaliação existe antes
            cursor.execute("SELECT 1 FROM Avaliacao WHERE id_avaliacao = ?", (id_avaliacao,))
            if cursor.fetchone() is None:
                return jsonify({"erro": f"Avaliação com id {id_avaliacao} não encontrada."}), 404

            # Busca as perguntas já vinculadas
            cursor.execute("SELECT id_pergunta FROM Contem WHERE id_avaliacao = ?", (id_avaliacao,))
            perguntas_existentes = [int(row.id_pergunta) for row in cursor.fetchall()]

            perguntas_a_inserir = list(set(lista_perguntas) - set(perguntas_existentes))
            perguntas_a_remover = list(set(perguntas_existentes) - set(lista_perguntas))

            # Remoção
            for id_pergunta in perguntas_a_remover:
                cursor.execute("""
                    DELETE FROM Contem 
                    WHERE id_avaliacao = ? AND id_pergunta = ?
                """, (id_avaliacao, id_pergunta))

            # Inserção
            for id_pergunta in perguntas_a_inserir:
                cursor.execute("""
                    INSERT INTO Contem (id_avaliacao, id_pergunta) 
                    VALUES (?, ?)
                """, (id_avaliacao, id_pergunta))

            conn.commit()

            return jsonify({
                "mensagem": f"Perguntas atualizadas para a avaliação {id_avaliacao}.",
                "inseridas": perguntas_a_inserir,
                "removidas": perguntas_a_remover
            }), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
