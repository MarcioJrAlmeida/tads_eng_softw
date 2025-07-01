# nlp/ml/preprocessador.py

import pandas as pd
import unicodedata
import re
import requests

def limpar_texto(texto):
    if not isinstance(texto, str):
        return ""
    texto = texto.lower()
    texto = ''.join(
        c for c in unicodedata.normalize('NFKD', texto)
        if not unicodedata.combining(c)
    )
    texto = re.sub(r'[^a-zA-Z0-9\s]', '', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

def carregar_dados_treinamento():
    try:
        url = "http://localhost:5001/api/ml/treinamento_manual"
        response = requests.get(url)

        if response.status_code != 200:
            print(f"❌ Erro ao acessar a API de treinamento: {response.status_code}")
            return pd.DataFrame()

        dados = response.json()

        # Converter em DataFrame
        df = pd.DataFrame(dados)

        if df.empty:
            print("⚠️ Nenhum dado encontrado na API de treinamento.")
            return df

        # Limpeza de texto
        df['pergunta'] = df['contexto_pergunta'].apply(limpar_texto)
        df['resposta'] = df['conteudo_resposta'].apply(limpar_texto)
        df['texto'] = df['pergunta'] + " " + df['resposta']

        return df[['id', 'texto', 'classificada_como_ofensiva', 'classificada_como_sentimento']]

    except Exception as e:
        print(f"❌ Erro ao carregar dados de treinamento via API: {e}")
        return pd.DataFrame()
