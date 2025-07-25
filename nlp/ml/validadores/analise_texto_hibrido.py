import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.insert(0, ROOT_DIR)

from nlp.ml.validadores.analise_texto import analisar_texto
from nlp.ml.validadores.analise_texto_llm import analisar_texto_llm

def analisar_texto_hibrido(resposta: str, pergunta: str):
    """
    Primeiro tenta com o modelo local de ML.
    Se a classificação for inconclusiva ou pouco confiável,
    aciona a IA (LLM) para uma interpretação mais precisa.
    """
    # Caso o modelo local classifique como ofensivo com alta confiança, usa ele
    resultado_local = analisar_texto(resposta, pergunta)
    r_local = resultado_local[0]

    # Verifica qual tipo de score está presente
    score = (
        r_local.get("score_critica") or 
        r_local.get("score_ofensivo") or 
        r_local.get("score_ofensa_explicita") or
        r_local.get("score_semantica") or
        r_local.get("score_toxidade") or
        r_local.get("score_ml_sentimento") or
        r_local.get("score")
    )

    # Se ambos tiverem alta confiança, retorna o local
    if score >= 0.75:
        return resultado_local
    
    resultado_ia = analisar_texto_llm(resposta, pergunta)

    # Garante que a resposta da IA seja válida (lista com dicionário)
    if isinstance(resultado_ia, list) and len(resultado_ia) > 0 and isinstance(resultado_ia[0], dict):
        r_ia = resultado_ia[0]

        # Se a IA detectar ofensa com alta confiança
        if r_ia["eh_ofensiva"] and r_ia["score"] >= 0.75:
            return resultado_ia

        # Se houver divergência clara entre local e IA (local diz que não é, IA diz que é)
        if not r_local["eh_ofensiva"] and r_ia["eh_ofensiva"]:
            return resultado_ia

    # Caso contrário, retorna o resultado local
    return resultado_local