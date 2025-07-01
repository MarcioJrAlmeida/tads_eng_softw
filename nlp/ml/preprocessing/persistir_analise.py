import sys
import os
import requests

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.insert(0, ROOT_DIR)

from nlp.ml.validadores.analise_texto_hibrido import analisar_texto_hibrido

BASE_URL = "http://localhost:5001/ml"

def buscar_suspeitas_nao_analisadas():
    try:
        response = requests.get(f"{BASE_URL}/frases_suspeitas/pendentes")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("Erro ao buscar frases suspeitas:", e)
        return []

def salvar_analise(frase, resultado):
    try:
        for r in resultado:
            payload = {
                "id": frase['id'],
                "id_avaliacao": frase['id_avaliacao'],
                "contexto_pergunta": frase['contexto_pergunta'],
                "conteudo_resposta": frase['conteudo_resposta'],
                "modelo_utilizado": r['metodo_detectado'],
                "sentimento_classificado": r['sentimento_previsto'],
                "ofensiva": int(r['eh_ofensiva']),
                "motivo_ofensivo": r['tipo_suspeita'],
                "score": r['score']
            }
            res = requests.post(f"{BASE_URL}/salvar_analise", json=payload)
            res.raise_for_status()

        requests.patch(f"{BASE_URL}/frases_suspeitas/{frase['id']}", json={"analisada_por_ml": 1})
    except Exception as e:
        print(f"❌ Erro ao salvar análise da frase ID {frase['id']}: {e}")

def processar_frases_suspeitas():
    frases = buscar_suspeitas_nao_analisadas()
    if not frases:
        print("Nenhuma frase suspeita pendente.")
        return

    for frase in frases:
        resultado = analisar_texto_hibrido(frase['conteudo_resposta'], frase['contexto_pergunta'])
        salvar_analise(frase, resultado)
        print(f"✅ Resultado salvo para ID {frase['id']}")

if __name__ == "__main__":
    processar_frases_suspeitas()
