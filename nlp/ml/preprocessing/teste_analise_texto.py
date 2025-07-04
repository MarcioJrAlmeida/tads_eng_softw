# nlp/ml/preprocessing/teste_analise_hibrida.py

import sys
import os

# Ajusta caminho para importar os módulos da aplicação
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.insert(0, ROOT_DIR)

from nlp.ml.validadores.analise_texto_hibrido import analisar_texto_hibrido

pergunta = "Como você avalia o desempenho do professor durante o semestre?"

print("🔍 Avaliação de Resposta Aberta")
print(f"❓ Pergunta: {pergunta}")

resposta = input("✏️  Digite a resposta do aluno: ").strip()

resultado = analisar_texto_hibrido(resposta, pergunta)



if isinstance(resultado, list) and all(isinstance(r, dict) for r in resultado):
    print("✅ Resultado da Análise Estruturada:")
    for r in resultado:
        score = (
            r.get("score_critica") or 
            r.get("score_ofensivo") or 
            r.get("score_ofensa_explicita") or
            r.get("score_semantica") or
            r.get("score_toxidade") or
            r.get("score_ml_sentimento") 
        )
        print(f"- Método: {r['metodo_detectado']}")
        print(f"  → Ofensiva: {r['eh_ofensiva']}")
        print(f"  → Tipo de Suspeita: {r['tipo_suspeita']}")
        print(f"  → Score: {score}")
        print(f"  → Sentimento: {r['sentimento_previsto']}")
        print("-" * 40)
else:
    print("❌ Resultado inválido:", repr(resultado))