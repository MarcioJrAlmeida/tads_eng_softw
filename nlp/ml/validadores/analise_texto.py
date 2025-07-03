import unicodedata
from spellchecker import SpellChecker
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from sentence_transformers import SentenceTransformer, util
import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.insert(0, ROOT_DIR)

from nlp.ml.learning.validador_respostas import prever_ofensividade, prever_analise_critica

spell = SpellChecker(language='pt')
modelo_frases = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# Sentimento e toxicidade
sentiment_model = "cardiffnlp/twitter-roberta-base-sentiment"
sent_tokenizer = AutoTokenizer.from_pretrained(sentiment_model)
sent_model = AutoModelForSequenceClassification.from_pretrained(sentiment_model)
sentiment_pipeline = pipeline("sentiment-analysis", model=sent_model, tokenizer=sent_tokenizer)

tox_model_id = "unitary/toxic-bert"
tox_tokenizer = AutoTokenizer.from_pretrained(tox_model_id)
tox_model = AutoModelForSequenceClassification.from_pretrained(tox_model_id)
tox_pipeline = pipeline("text-classification", model=tox_model, tokenizer=tox_tokenizer)

frases_negativas_permitidas = [
    "aula ruim", "aula fraca", "não gostei da aula", "péssima aula", "aula confusa",
    "aula desorganizada", "professor desorganizado", "professor precisa melhorar",
    "a didática foi ruim", "não consegui entender", "não explicou bem",
    "não aprendi nada", "fiquei com dúvidas", "professor despreparado",
    "não tirou nossas dúvidas", "não soube responder", "falta domínio do conteúdo",
    "poderia melhorar", "foi ruim", "esperava mais", "aula muito básica",
    "o conteúdo foi mal apresentado", "a explicação foi fraca", "foi cansativo",
    "demonstrou impaciência", "faltou clareza", "repetitivo demais",
    "não se preparou para a aula", "demonstrou insegurança",
    "não seguiu o conteúdo", "faltou planejamento", "leu os slides o tempo todo",
    "poderia interagir mais com a turma"
]

def remover_acentos(texto):
    return ''.join(c for c in unicodedata.normalize('NFKD', texto) if not unicodedata.combining(c))

def desleet(texto):
    mapa = {'4': 'a', '3': 'e', '1': 'i', '0': 'o', '5': 's', '@': 'a', '$': 's', '!': 'i'}
    for k, v in mapa.items():
        texto = texto.replace(k, v)
    return texto

# === Função principal de análise ===
def analisar_texto(texto, contexto=None):
    original = texto
    texto_limpo = desleet(remover_acentos(original.lower()))

    # (1) Classificador supervisionado de OFENSIVIDADE
    if contexto:
        resultado_ofensivo = prever_ofensividade(contexto, texto)
        if resultado_ofensivo.get("score", 0) >= 0.5:
            return [{
                "eh_ofensiva": resultado_ofensivo["eh_ofensiva"],
                "metodo_detectado": "modelo_treinado_ofensivo",
                "tipo_suspeita": "ofensividade_supervisionada",
                "score": resultado_ofensivo.get("score", 0),
                "sentimento_previsto": None
            }]

    # (2) Verificação semântica com frases críticas aceitáveis
    emb_entrada = modelo_frases.encode(original, convert_to_tensor=True)
    emb_validas = modelo_frases.encode(frases_negativas_permitidas, convert_to_tensor=True)
    if util.pytorch_cos_sim(emb_entrada, emb_validas).max().item() >= 0.85:
        return [{
            "eh_ofensiva": False,
            "metodo_detectado": "semantica",
            "tipo_suspeita": "critica_aceitavel",
            "score": 0,
            "sentimento_previsto": "NEGATIVO"
        }]

    # (3) Modelo de toxicidade
    tox = tox_pipeline(original)[0]
    if tox['label'].lower() == "toxic" and tox['score'] >= 0.7:
        resultado_sent = sentiment_pipeline(original)[0]
        return [{
            "eh_ofensiva": True,
            "metodo_detectado": "modelo_transformer",
            "tipo_suspeita": "toxicidade_modelo",
            "score": tox['score'],
            "sentimento_previsto": resultado_sent['label']
        }]

    # (4) Modelo supervisionado de ANÁLISE CRÍTICA (sentimento inteligente)
    if contexto:
        resultado_critico = prever_analise_critica(contexto, texto)
        return [{
            "eh_ofensiva": False,
            "metodo_detectado": "modelo_treinado_critico",
            "tipo_suspeita": "avaliacao_critica_inteligente",
            "score": resultado_critico.get("score", 0),
            "sentimento_previsto": resultado_critico.get("label",0)
        }]

    # (5) Fallback: Modelo de sentimento geral
    resultado_sent = sentiment_pipeline(original)[0]
    return [{
        "eh_ofensiva": False,
        "metodo_detectado": "sentimento",
        "tipo_suspeita": "avaliacao_geral",
        "score": round(resultado_sent['score'], 2),
        "sentimento_previsto": resultado_sent['label']
    }]

# Teste direto
if __name__ == "__main__":
    resultado = analisar_texto("Você gosta do professor?", "Acho ele um idiota.")
    print("Resultado estruturado:", resultado)