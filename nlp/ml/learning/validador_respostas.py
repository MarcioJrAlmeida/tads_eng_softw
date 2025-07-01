# nlp/ml/learning/validador_respostas.py

import joblib
import os
import unicodedata
import re

# Função de limpeza de texto
def limpar_texto(texto):
    if not isinstance(texto, str):
        return ""
    texto = texto.lower()
    texto = ''.join(c for c in unicodedata.normalize('NFKD', texto) if not unicodedata.combining(c))
    texto = re.sub(r'[^a-zA-Z0-9\s]', '', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

# Caminho dos modelos
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "modelos"))
modelo_path = os.path.join(BASE_DIR, "modelo_ofensivo.pkl")
vectorizer_path = os.path.join(BASE_DIR, "vectorizer_ofensivo.pkl")

# Carregar modelos
modelo = joblib.load(modelo_path)
vectorizer = joblib.load(vectorizer_path)

def prever_ofensividade(contexto_pergunta, conteudo_resposta):
    texto_completo = f"{contexto_pergunta} {conteudo_resposta}"
    texto_limpo = limpar_texto(texto_completo)

    X = vectorizer.transform([texto_limpo])
    previsao = modelo.predict(X)[0]
    probabilidade = modelo.predict_proba(X)[0].max()

    return {
        "eh_ofensiva": bool(previsao),
        "score": round(float(probabilidade), 3)
    }

# Teste isolado
if __name__ == "__main__":
    pergunta = "Como você avalia o professor?"
    resposta = input("Digite a resposta do aluno: ")

    resultado = prever_ofensividade(pergunta, resposta)
    print("Resultado da predição:", resultado)
