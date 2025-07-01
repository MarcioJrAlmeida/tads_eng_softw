# nlp/ml/learning/treinar_ofensivo.py

import requests
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import unicodedata
import re
import os

API_URL = "http://localhost:5001/ml/treinamento/manual"

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
    df = df[df['classificada_como_ofensiva'].notnull()]
    df['texto'] = (df['contexto_pergunta'].fillna('') + ' ' + df['conteudo_resposta'].fillna('')).apply(limpar_texto)
    return df[['texto', 'classificada_como_ofensiva']]

def treinar_modelo_ofensivo():
    df = carregar_dados_treinamento()
    if df.empty:
        print("❌ Nenhum dado disponível para treinamento.")
        return

    X = df['texto']
    y = df['classificada_como_ofensiva']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    vectorizer = TfidfVectorizer(max_features=3000)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    modelo = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo.fit(X_train_vec, y_train)

    y_pred = modelo.predict(X_test_vec)
    print(classification_report(y_test, y_pred))

    # Caminho correto baseado na estrutura tads_eng_softw/nlp/ml/modelos
    modelos_dir = os.path.join(os.path.dirname(__file__), "..", "modelos")
    os.makedirs(modelos_dir, exist_ok=True)

    joblib.dump(modelo, os.path.join(modelos_dir, "modelo_ofensivo.pkl"))
    joblib.dump(vectorizer, os.path.join(modelos_dir, "vectorizer_ofensivo.pkl"))
    print("✅ Modelo ofensivo treinado e salvo com sucesso!")

if __name__ == "__main__":
    treinar_modelo_ofensivo()
