import unicodedata, re
from spellchecker import SpellChecker
from better_profanity import profanity
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from sentence_transformers import SentenceTransformer, util
from rapidfuzz import fuzz
import torch
import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.insert(0, ROOT_DIR)

from nlp.ml.learning.validador_respostas import prever_ofensividade

# === Palavras e frases ===
palavras_ofensivas = [
    "merda", "bosta", "porra", "caralho", "cu", "cuzão", "buceta", "pau no cu", "pnc",
    "vai se fuder", "vsf", "vai tomar no cu", "vtnc", "foda-se", "se foder",
    "fodido", "babaca", "idiota", "imbecil", "retardado", "burro", "jumento",
    "otário", "panaca", "mané", "zé ruela", "trouxa", "tapado", "escroto",
    "arrombado", "canalha", "cacete", "desgraça", "inferno", "diabo", "lixo",
    "viado", "bicha", "bixona", "boiola", "bichola", "gay de merda",
    "paneleiro", "sapatão", "traveco", "travecão", "travesti do caralho",
    "negro de merda", "macaco", "crioulo", "favelado", "pobre de merda",
    "nordestino burro", "paraíba", "judeu de merda", "cigano ladrão",
    "fio de rapariga", "fio de uma égua", "caba safado", "arrombadinho",
    "desmantelado", "fuleira", "fuleiragem", "caba frouxo", "peste",
    "fila de uma peste", "cabra de peia", "oxente seu peste",
    "me arrombe", "seu infeliz", "doido de pedra",
    "lambe clitóris", "chupa clitoris", "da o cu", "chupa cu",
    "chupa rola", "enfia no cu essa merda", "vai chupar um canavial de rola",
    "boquete", "bolagato", "bolcat", "bosseta", "brosca", "bronha", "brioco",
    "broxa", "bunda", "chereca", "chibumba", "chibumbo", "chifruda",
    "zero à esquerda", "velhaco", "verme", "vagabundo", "ignorante",
    "tanso", "tosco", "torpe", "troglodita", "vigarista", "zingão", "zelota",
    "fdp", "pnc", "vsf", "vtnc", "pqp", "tmnc", "fds", "obg", "slk", "amg",
    "vc fod", "vc é fod@", "vc fodeu", "vai sentar"
]

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

spell = SpellChecker(language='pt')
profanity.load_censor_words(palavras_ofensivas)
modelo_frases = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

sentiment_model = "cardiffnlp/twitter-roberta-base-sentiment"
sent_tokenizer = AutoTokenizer.from_pretrained(sentiment_model)
sent_model = AutoModelForSequenceClassification.from_pretrained(sentiment_model)
sentiment_pipeline = pipeline("sentiment-analysis", model=sent_model, tokenizer=sent_tokenizer)

tox_model_id = "unitary/toxic-bert"
tox_tokenizer = AutoTokenizer.from_pretrained(tox_model_id)
tox_model = AutoModelForSequenceClassification.from_pretrained(tox_model_id)
tox_pipeline = pipeline("text-classification", model=tox_model, tokenizer=tox_tokenizer)

def remover_acentos(texto):
    return ''.join(c for c in unicodedata.normalize('NFKD', texto) if not unicodedata.combining(c))

def desleet(texto):
    mapa = {'4': 'a', '3': 'e', '1': 'i', '0': 'o', '5': 's', '@': 'a', '$': 's', '!': 'i'}
    for k, v in mapa.items():
        texto = texto.replace(k, v)
    return texto

def analisar_texto(texto, contexto=None):
    original = texto
    texto_limpo = desleet(remover_acentos(original.lower()))

    # === 1. Classificador Treinado ===
    if contexto:
        resultado_ml = prever_ofensividade(contexto, texto)
        if resultado_ml["score"] >= 0.75:
            return [{
                "eh_ofensiva": resultado_ml["eh_ofensiva"],
                "metodo_detectado": "modelo_treinado_manual",
                "tipo_suspeita": "machine_learning_supervisionado",
                "score": resultado_ml["score"],
                "sentimento_previsto": None
            }]

    if profanity.contains_profanity(texto_limpo):
        return [{
            "eh_ofensiva": True,
            "metodo_detectado": "profanity",
            "tipo_suspeita": "direta",
            "score": 1.0,
            "sentimento_previsto": None
        }]

    palavras = texto_limpo.split()
    for palavra in palavras:
        if palavra not in spell:
            for ofensiva in palavras_ofensivas:
                score = fuzz.partial_ratio(palavra, ofensiva)
                if score >= 75:
                    return [{
                        "eh_ofensiva": True,
                        "metodo_detectado": "palavra_inventada",
                        "tipo_suspeita": "invenção_suspeita",
                        "score": score / 100,
                        "sentimento_previsto": None
                    }]

    for palavra in palavras:
        if palavra not in spell:
            for ofensiva in palavras_ofensivas:
                score = fuzz.partial_ratio(palavra, ofensiva)
                if score >= 75:
                    return [{
                        "eh_ofensiva": True,
                        "metodo_detectado": "rapidfuzz",
                        "tipo_suspeita": "leetspeak/similaridade",
                        "score": score / 100,
                        "sentimento_previsto": None
                    }]

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

    emb_ofensivas = modelo_frases.encode(palavras_ofensivas, convert_to_tensor=True)
    sims = util.pytorch_cos_sim(emb_entrada, emb_ofensivas)[0]
    max_sim = sims.max().item()
    if max_sim >= 0.85:
        idx = sims.argmax().item()
        return [{
            "eh_ofensiva": True,
            "metodo_detectado": "semantica",
            "tipo_suspeita": "semelhanca_frase",
            "score": round(max_sim, 2),
            "sentimento_previsto": None
        }]

    resultado = sentiment_pipeline(original)[0]
    sentimento = resultado['label']
    score_sent = round(resultado['score'], 2)

    label_tox = tox_pipeline(original)[0]['label']
    score_tox = round(tox_pipeline(original)[0]['score'], 2)

    if label_tox.lower() == "toxic" and score_tox >= 0.7:
        return [{
            "eh_ofensiva": True,
            "metodo_detectado": "modelo_transformer",
            "tipo_suspeita": "toxicidade_modelo",
            "score": score_tox,
            "sentimento_previsto": sentimento
        }]

    return [{
        "eh_ofensiva": False,
        "metodo_detectado": "sentimento",
        "tipo_suspeita": "avaliacao_geral",
        "score": score_sent,
        "sentimento_previsto": sentimento
    }]
