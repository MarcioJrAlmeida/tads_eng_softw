# nlp/ml/learning/treinar_analise.py

import requests
import pandas as pd
import joblib
import os
import unicodedata
import re
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

API_URL = "http://localhost:5001/ml/treinamento/sentimento"

def limpar_texto(texto):
    if not isinstance(texto, str):
        return ""
    texto = texto.lower()
    texto = ''.join(c for c in unicodedata.normalize('NFKD', texto) if not unicodedata.combining(c))
    texto = re.sub(r'[^a-zA-Z0-9\s]', '', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

def carregar_dados_treinamento():
    response = requests.get(API_URL)
    if response.status_code != 200:
        print("❌ Erro ao buscar dados de treinamento:", response.text)
        return pd.DataFrame()

    df = pd.DataFrame(response.json())
    df = df[df['classificada_como_sentimento'].notnull()]
    df['texto'] = (df['contexto_pergunta'].fillna('') + ' ' + df['conteudo_resposta'].fillna('')).apply(limpar_texto)
    df = df.rename(columns={"classificada_como_sentimento": "label"})

    return df[['texto', 'label']]

def treinar_modelo_sentimento():
    df = carregar_dados_treinamento()
    if df.empty:
        print("❌ Nenhum dado disponível para treinamento.")
        return

    X = df['texto']
    y = df['label']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    vectorizer = TfidfVectorizer(max_features=3000)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    modelo = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo.fit(X_train_vec, y_train)

    y_pred = modelo.predict(X_test_vec)
    print("\n🎯 Relatório de Classificação (Sentimento):\n")
    print(classification_report(y_test, y_pred))

    modelos_dir = os.path.join(os.path.dirname(__file__), "..", "modelos")
    os.makedirs(modelos_dir, exist_ok=True)

    joblib.dump(modelo, os.path.join(modelos_dir, "modelo_sentimento.pkl"))
    joblib.dump(vectorizer, os.path.join(modelos_dir, "vectorizer_sentimento.pkl"))

    print("✅ Modelo de sentimento treinado e salvo com sucesso!")

if __name__ == "__main__":
    treinar_modelo_sentimento()
