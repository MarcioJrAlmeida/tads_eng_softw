import sys
import os
import requests
import pandas as pd

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.insert(0, ROOT_DIR)

from nlp.ml.validadores.analise_texto_hibrido import analisar_texto_hibrido

API_SADO_ML_URL = "http://localhost:5001/ml"

def buscar_respostas_abertas():
    url = f"{API_SADO_ML_URL}/respostas/abertas"
    response = requests.get(url)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        print("Erro ao buscar respostas abertas:", response.text)
        return pd.DataFrame()

def inserir_frase_suspeita(row, resultado):
    url = f"{API_SADO_ML_URL}/frases_suspeitas"
    for r in resultado:
        score = (
            r.get("score_critica") or 
            r.get("score_ofensivo") or 
            r.get("score_ofensa_explicita") or
            r.get("score_semantica") or
            r.get("score_toxidade") or
            r.get("score_ml_sentimento") or
            r.get("score")
        )
        
        payload = {
            "id_avaliacao": row['id_avaliacao'],
            "id_pergunta": row['id_pergunta'],
            "id_resposta": row['id_resposta'],
            "contexto_pergunta": row['texto_pergunta'],
            "conteudo_resposta": row['conteudo_resposta'],
            "metodo_detectado": r.get('metodo_detectado'),
            "tipo_suspeita": r.get('tipo_suspeita'),
            "score": score,
            "analisada_por_ml": 1,
            "eh_ofensiva": True,
            "sentimento_previsto": r.get('sentimento_previsto')
        }
        response = requests.post(url, json=payload)
        if response.status_code == 201:
            print("✅ Frase ofensiva inserida em Frases_Suspeitas")
        else:
            print("❌ Erro ao inserir em Frases_Suspeitas:", response.text)

def inserir_frase_analisada(row, resultado):
    url = f"{API_SADO_ML_URL}/salvar_analise"
    for r in resultado:
        score = (
            r.get("score_critica") or 
            r.get("score_ofensivo") or 
            r.get("score_ofensa_explicita") or
            r.get("score_semantica") or
            r.get("score_toxidade") or
            r.get("score_ml_sentimento") or
            r.get("score")
        )
        
        payload = {
            "id": row.get('id', 0),
            "id_avaliacao": row['id_avaliacao'],
            "id_pergunta": row['id_pergunta'],
            "id_resposta": row['id_resposta'],
            "contexto_pergunta": row['texto_pergunta'],
            "conteudo_resposta": row['conteudo_resposta'],
            "modelo_utilizado": r.get('metodo_detectado'),
            "sentimento_classificado": r.get('sentimento_previsto'),
            "ofensiva": int(r.get('eh_ofensiva', 0)),
            "motivo_ofensivo": r.get('tipo_suspeita'),
            "score": score
        }
        response = requests.post(url, json=payload)
        if response.status_code == 201:
            print("✅ Frase registrada em Frases_Analisadas")
        else:
            print("❌ Erro ao inserir em Frases_Analisadas:", response.text)


def processar_respostas():
    df = buscar_respostas_abertas()
    if df.empty:
        print("Nenhuma resposta aberta encontrada.")
        return

    for _, row in df.iterrows():
        resultado = analisar_texto_hibrido(row['conteudo_resposta'], row['texto_pergunta'])
        if resultado and resultado[0]['eh_ofensiva']:
            inserir_frase_suspeita(row, resultado)
            print(f"🚨 Ofensiva detectada: ID {row['id_resposta']}")
        else:
            inserir_frase_analisada(row, resultado)
            print(f"✅ Sem ofensa: ID {row['id_resposta']}")

if __name__ == "__main__":
    processar_respostas()
