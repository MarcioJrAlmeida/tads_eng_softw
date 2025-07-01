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
        payload = {
            "id_avaliacao": row['id_avaliacao'],
            "contexto_pergunta": row['texto_pergunta'],
            "conteudo_resposta": row['conteudo_resposta'],
            "metodo_detectado": r['metodo_detectado'],
            "tipo_suspeita": r['tipo_suspeita'],
            "score": r['score'],
            "analisada_por_ml": 1,
            "eh_ofensiva": True,
            "sentimento_previsto": r['sentimento_previsto']
        }
        response = requests.post(url, json=payload)
        if response.status_code == 201:
            print("✅ Frase ofensiva inserida em Frases_Suspeitas")
        else:
            print("❌ Erro ao inserir em Frases_Suspeitas:", response.text)

def inserir_frase_analisada(row, resultado):
    url = f"{API_SADO_ML_URL}/salvar_analise"
    for r in resultado:
        payload = {
            "id": row.get('id', 0),
            "id_avaliacao": row['id_avaliacao'],
            "contexto_pergunta": row['texto_pergunta'],
            "conteudo_resposta": row['conteudo_resposta'],
            "modelo_utilizado": r['metodo_detectado'],
            "sentimento_classificado": r['sentimento_previsto'],
            "ofensiva": int(r['eh_ofensiva']),
            "motivo_ofensivo": r['tipo_suspeita'],
            "score": r['score']
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
