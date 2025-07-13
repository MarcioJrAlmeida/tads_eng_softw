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

# Caminho base dos modelos
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "modelos"))

# Carregamento do modelo ofensivo
modelo_ofensivo = joblib.load(os.path.join(BASE_DIR, "modelo_ofensivo.pkl"))
vectorizer_ofensivo = joblib.load(os.path.join(BASE_DIR, "vectorizer_ofensivo.pkl"))

# Carregamento do modelo analítico (sentimento)
modelo_analitico = joblib.load(os.path.join(BASE_DIR, "modelo_sentimento.pkl"))
vectorizer_analitico = joblib.load(os.path.join(BASE_DIR, "vectorizer_sentimento.pkl"))

def prever_ofensividade(contexto_pergunta, conteudo_resposta, threshold=0.5):
    texto_completo = f"{contexto_pergunta} {conteudo_resposta}"
    texto_limpo = limpar_texto(texto_completo)

    X = vectorizer_ofensivo.transform([texto_limpo])
    probas = modelo_ofensivo.predict_proba(X)[0]

    # Probabilidade da classe "True"
    idx_ofensivo = list(modelo_ofensivo.classes_).index(True)
    score = probas[idx_ofensivo]

    return {
        "eh_ofensiva": score >= threshold,
        "score_ofensiva": round(float(score), 3)
    }


def prever_analise_critica(contexto_pergunta, conteudo_resposta):
    texto_completo = f"{contexto_pergunta} {conteudo_resposta}"
    texto_limpo = limpar_texto(texto_completo)

    X = vectorizer_analitico.transform([texto_limpo])
    previsao = modelo_analitico.predict(X)[0]
    probabilidade = modelo_analitico.predict_proba(X)[0].max()

    return {
        "eh_ofensiva": False,
        "classificacao_critica": previsao,
        "score_critica": round(float(probabilidade), 3)
    }

def prever_ambos(contexto_pergunta, conteudo_resposta):
    ofensivo = prever_ofensividade(contexto_pergunta, conteudo_resposta)
    critico = prever_analise_critica(contexto_pergunta, conteudo_resposta)

    return {
        "eh_ofensiva": ofensivo["eh_ofensiva"],
        "score_ofensiva": ofensivo["score_ofensiva"],
        "classificacao_critica": critico["classificacao_critica"],
        "score_critica": critico["score_critica"]
    }

# Teste isolado
if __name__ == "__main__":
    pergunta = "Qual a sua opinião sobre a metodologia de aula do Professor?"
    resposta = input("Digite a resposta do aluno: ")

    resultado = prever_ambos(pergunta, resposta)
    print("Resultado da predição combinada:")
    for chave, valor in resultado.items():
        print(f"  {chave}: {valor}")
