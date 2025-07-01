import os
import json
import requests
from dotenv import load_dotenv
import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.insert(0, ROOT_DIR)

from nlp.ml.learning.validador_respostas import prever_ofensividade

# Carregar variáveis de ambiente
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")

def analisar_texto_llm(resposta, pergunta):
    # Primeiro, tenta modelo local supervisionado
    resultado_ml = prever_ofensividade(pergunta, resposta)
    if resultado_ml["score"] >= 0.75:
        return [{
            "eh_ofensiva": resultado_ml["eh_ofensiva"],
            "metodo_detectado": "modelo_treinado_manual",
            "tipo_suspeita": "machine_learning_supervisionado",
            "score": resultado_ml["score"],
            "sentimento_previsto": None
        }]
        
    try:
        prompt = f"""
Você é um modelo de linguagem treinado para classificar textos com base no conteúdo e no contexto de perguntas e respostas em um formulário de avaliação.

Analise cuidadosamente o seguinte diálogo:

Contexto da pergunta: "{pergunta}"
Resposta do usuário: "{resposta}"

Com base na análise contextual da pergunta e da resposta, execute as seguintes tarefas:

1. Detecte se há presença de conteúdo ofensivo.
2. Classifique o sentimento da resposta como: **positivo**, **neutro** ou **negativo**.
3. Caso haja ofensa, identifique claramente o **motivo** (ex: linguagem agressiva, desrespeito, ironia ofensiva, etc.).
4. Atribua um **score de suspeita** entre 0 (nenhuma suspeita) e 1 (altamente suspeita).
5. Use o nome do modelo "Mistral-7B-Instruct:free" no campo `metodo_detectado`.

Responda exclusivamente no formato JSON a seguir:
[
  {{
    "metodo_detectado": "Mistral‑7B‑Instruct:free",
    "eh_ofensiva": true,
    "tipo_suspeita": "Linguagem agressiva",
    "score": 0.82,
    "sentimento_previsto": "negativo"
  }}
]
"""

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8501",  # ou site real se houver
            "X-Title": "Sistema SADo",
        }

        payload = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            data=json.dumps(payload)
        )

        if response.status_code == 200:
            resposta_llm = response.json()['choices'][0]['message']['content']
            try:
                resultado = json.loads(resposta_llm)
                return resultado
            except json.JSONDecodeError:
                print("❌ Erro ao decodificar JSON retornado:")
                print(resposta_llm)
                return []
        else:
            print(f"❌ Erro ao chamar o LLM: {response.status_code} - {response.text}")
            return []

    except Exception as e:
        print(f"❌ Exceção na requisição ao LLM: {e}")
        return []

# Teste direto
if __name__ == "__main__":
    resultado = analisar_texto_llm("Você gosta do professor?", "Acho ele um idiota.")
    print("Resultado estruturado:", resultado)
