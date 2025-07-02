# nlp/ml/preprocessing/teste_analise_hibrida.py

import sys
import os

# Ajusta caminho para importar os módulos da aplicação
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.insert(0, ROOT_DIR)

from nlp.ml.validadores.analise_texto_hibrido import analisar_texto_hibrido

# Pergunta fixa (mas personalizável)
pergunta = "Como você avalia o desempenho do professor durante o semestre?"

print("🔍 Avaliação de Resposta Aberta")
print(f"❓ Pergunta: {pergunta}")

# Entrada do usuário
resposta = input("✏️  Digite a resposta do aluno: ").strip()

# Análise
resultado = analisar_texto_hibrido(resposta, pergunta=pergunta)

if isinstance(resultado, list) and all(isinstance(r, dict) for r in resultado):
    print("✅ Resultado da Análise Estruturada:")
    for r in resultado:
        print(f"- Método: {r['metodo_detectado']}")
        print(f"  → Ofensiva: {r['eh_ofensiva']}")
        print(f"  → Tipo de Suspeita: {r['tipo_suspeita']}")
        print(f"  → Score: {r['score']}")
        print(f"  → Sentimento: {r['sentimento_previsto']}")
        print("-" * 40)
else:
    print("❌ Resultado inválido:", repr(resultado))