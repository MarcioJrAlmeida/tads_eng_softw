# nlp/ml/treinador.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score
import joblib
from nlp.ml.preprocessing.preprocessador import carregar_dados_treinamento

# Carrega e prepara os dados
df = carregar_dados_treinamento()

# Define as features e os rótulos (classificação de sentimento)
X = df['texto']
y = df['classificada_como_sentimento']  # esperado: "positivo", "neutro", "negativo"

# Divide em treino e teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Cria pipeline com TF-IDF + Naive Bayes
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(max_features=3000)),
    ('clf', MultinomialNB())
])

# Treina o modelo
pipeline.fit(X_train, y_train)

# Avalia o modelo
y_pred = pipeline.predict(X_test)
print("\nRelatório de Classificação:\n")
print(classification_report(y_test, y_pred))
print("Acurácia:", accuracy_score(y_test, y_pred))

# Salva modelo treinado
joblib.dump(pipeline, 'nlp/ml/database/modelo_sentimento.joblib')
print("\nModelo salvo em: nlp/ml/database/modelo_sentimento.joblib")
