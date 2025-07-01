import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.insert(0, ROOT_DIR)

from nlp.ml.validadores.analise_texto import analisar_texto as modelo_ml
from nlp.ml.validadores.analise_texto_llm import analisar_texto_llm

def analisar_texto_hibrido(resposta: str, pergunta: str):
    """
    Executa análise híbrida:
    1. Primeiro tenta com modelo ML local (rápido, econômico)
    2. Se for inconclusivo ou score muito baixo, tenta com LLM
    """

    try:
        resultado_ml = modelo_ml(resposta, pergunta)
        if not resultado_ml:
            print("⚠️ Resultado ML vazio, partindo para LLM")
            return analisar_texto_llm(resposta, pergunta)

        suspeita_ml = resultado_ml[0]

        # Alta confiança no resultado local, não precisa da LLM
        if suspeita_ml['score'] >= 0.7 or suspeita_ml['eh_ofensiva']:
            return resultado_ml
        else:
            print("🤖 Score baixo ou neutro, acionando LLM para reforço interpretativo")
            return analisar_texto_llm(resposta, pergunta)

    except Exception as e:
        print("Erro ao executar análise híbrida:", e)
        return []
