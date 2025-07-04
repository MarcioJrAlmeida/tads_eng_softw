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
    if resultado_ml.get("score",0) >= 0.5:
        return [{
            "eh_ofensiva": resultado_ml.get("eh_ofensiva",0),
            "metodo_detectado": "modelo_treinado_manual",
            "tipo_suspeita": "machine_learning_supervisionado",
            "score": resultado_ml.get("score",0),
            "sentimento_previsto": None
        }]
        
    try:
        prompt = f"""
        Você é um modelo de linguagem treinado para analisar respostas de formulários de avaliação. Sua tarefa é interpretar o conteúdo da resposta em relação ao contexto da pergunta e retornar uma análise objetiva.

        ### Dados:
        - Contexto da pergunta: "{pergunta}"
        - Resposta do usuário: "{resposta}"

        ### Objetivos da análise:
        1. Avaliar se a resposta contém **conteúdo ofensivo**. (true/false)
        2. Determinar o **sentimento geral** da resposta: "positivo", "neutro", "negativo" ou irônico.
        3. Se houver ofensa, especifique o **tipo de suspeita** ou o motivo (ex: "linguagem agressiva", "ironia ofensiva", "desrespeito").
        4. Atribuir um **score de suspeita** entre 0 e 1, onde:
           - 0.0 = nenhuma suspeita
           - 1.0 = extremamente ofensiva ou suspeita
        5. Registrar o nome do modelo como `"GPT 3.5 Turbo"` no campo `metodo_detectado`.

        ### Formato de resposta:
        Responda SOMENTE com um JSON válido. Os valores devem ser baseados na sua análise, não copie os exemplos. Exemplo de estrutura (não copie os valores):

        [
          {{
            "metodo_detectado": "GPT 3.5 Turbo",
            "eh_ofensiva": false,
            "tipo_suspeita": null,
            "score": 0.15,
            "sentimento_previsto": "neutro"
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
            "model": "openai/gpt-3.5-turbo-0613",
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
