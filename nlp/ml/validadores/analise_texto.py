import unicodedata
from spellchecker import SpellChecker
import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.insert(0, ROOT_DIR)

from nlp.ml.learning.validador_respostas import prever_ofensividade, prever_analise_critica, prever_ambos

spell = SpellChecker(language='pt')

# Lazy loading dos modelos
modelo_frases = None
sentiment_pipeline = None
tox_pipeline = None

def carregar_modelo_frases():
    global modelo_frases
    if modelo_frases is None:
        from sentence_transformers import SentenceTransformer
        modelo_frases = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

def carregar_sentiment_pipeline():
    global sentiment_pipeline
    if sentiment_pipeline is None:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
        sentiment_model = "cardiffnlp/twitter-roberta-base-sentiment"
        sent_tokenizer = AutoTokenizer.from_pretrained(sentiment_model)
        sent_model = AutoModelForSequenceClassification.from_pretrained(sentiment_model)
        sentiment_pipeline = pipeline("sentiment-analysis", model=sent_model, tokenizer=sent_tokenizer)

def carregar_tox_pipeline():
    global tox_pipeline
    if tox_pipeline is None:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
        tox_model_id = "unitary/toxic-bert"
        tox_tokenizer = AutoTokenizer.from_pretrained(tox_model_id)
        tox_model = AutoModelForSequenceClassification.from_pretrained(tox_model_id)
        tox_pipeline = pipeline("text-classification", model=tox_model, tokenizer=tox_tokenizer)

palavras_ofensivas = [
    "merda", "bosta", "porra", "caralho", "cu", "cuzão", "buceta", "pau no cu", "pnc",
    "vai se fuder", "vsf", "vai tomar no cu", "vtnc", "foda-se", "se foder",
    "fodido", "babaca", "idiota", "imbecil", "retardado", "burro", "jumento",
    "otário", "panaca", "mané", "zé ruela", "trouxa", "tapado", "escroto",
    "arrombado", "canalha", "cacete", "desgraça", "inferno", "diabo", "lixo",
    "corno", "corno manso", "corna", "safado", "vagabundo", "sem vergonha", "velho safado",
    "viado", "bicha", "bixona", "boiola", "bichola", "paneleiro", "sapatão",
    "traveco", "travecão", "travesti do caralho", "lambe clitóis", "chupa clitoris",
    "chupa rola", "enfia no cu", "vai chupar um canavial de rola", "boquete",
    "bolagato", "bolcat", "bosseta", "brosca", "brioco", "broxa", "chereca", "chibumba",
    "chibumbo", "bunda", "chupetão", "dar o cu", "tome no cu", "encaixe", "suruba", "dedada",
    "negro de merda", "macaco", "crioulo", "favelado", "pobre de merda",
    "nordestino burro", "paraíba", "baiano preguiçoso", "judeu de merda", "cigano ladrão",
    "fio de rapariga", "fio de uma égua", "arrombadinho", "desmantelado", "fuleira",
    "fuleiragem", "peste", "caba frouxo", "caba safado", "fila de uma peste", "cabra de peia",
    "oxente seu peste", "me arrombe", "doido de pedra", "peste bubônica", "calango doido",
    "cabra safado", "cabra do cão", "diabo loiro", "raparigueiro", "vai pastar", "caba de peia",
    "aula de merda", "não ensinou porra nenhuma", "parece que tava bêbado", "ensina igual a minha avó morta",
    "nem meu cachorro entende essa aula", "professor lixo", "explica igual o cu", "pior que calouro perdido",
    "cagou na lousa", "fez um cocô verbal", "parece que tava chapado", "ensina só enrolando", "ensina igual um jumento",
    "mais perdido que cego em tiroteio", "parece um doido", "fala mais que a boca", "fala merda o tempo todo",
    "fdp", "pnc", "vsf", "vtnc", "pqp", "tmnc", "fds",
    "professor burro", "aula lixo", "professor doido", "ensino de bosta", "professor fraco",
    "esse cara é uma piada", "essa mulher é uma anta", "esse aí só sabe gritar", "fala igual uma porta"
]

frases_negativas_permitidas = [
    "aula ruim", "aula fraca", "não gostei da aula", "péssima aula", "aula confusa",
    "aula desorganizada", "desorganizado", "precisa melhorar", "a didática foi ruim", "não explicou bem",
    "não aprendi nada", "fiquei com dúvidas", "despreparado", "leu os slides o tempo todo",
    "poderia melhorar", "foi ruim", "esperava mais", "aula básica","foi cansativo",
    "demonstrou impaciência", "faltou clareza", "repetitivo demais",
    "não se preparou para a aula", "demonstrou insegurança", "faltou planejamento"
]

def remover_acentos(texto):
    return ''.join(c for c in unicodedata.normalize('NFKD', texto) if not unicodedata.combining(c))

def desleet(texto):
    mapa = {'4': 'a', '3': 'e', '1': 'i', '0': 'o', '5': 's', '@': 'a', '$': 's', '!': 'i'}
    for k, v in mapa.items():
        texto = texto.replace(k, v)
    return texto

def analisar_texto(texto, contexto=None):
    carregar_modelo_frases()
    carregar_sentiment_pipeline()
    carregar_tox_pipeline()
    from sentence_transformers import util

    original = texto
    texto_limpo = desleet(remover_acentos(original.lower()))
    palavras = texto_limpo.split()
    resultados = []

    for palavra in palavras:
        if palavra in palavras_ofensivas:
            resultado_sent = sentiment_pipeline(original)[0]
            return [{
                "eh_ofensiva": True,
                "metodo_detectado": "palavra_ofensiva",
                "tipo_suspeita": "ofensa_explicita",
                "score": 1.0,
                "sentimento_previsto": resultado_sent["label"]
            }]

    if contexto:
        r1 = prever_ofensividade(contexto, texto)
        r1.update({"metodo_detectado": "modelo_treinado_ofensivo", "tipo_suspeita": "ofensividade_supervisionada", "sentimento_classificado": 'negativo'})
        resultados.append((r1, r1.get("score_ofensiva", 0), 0.6))

        r2 = prever_analise_critica(contexto, texto)
        r2.update({
            "metodo_detectado": "modelo_treinado_critico",
            "tipo_suspeita": "avaliacao_critica_inteligente",
            "sentimento_previsto": r2.get("classificacao_critica"),
            "score": r2.get("score_critica")
        })
        resultados.append((r2, r2["score"], 0.8))

        r3 = prever_ambos(contexto, texto)
        r3.update({
            "metodo_detectado": "modelo_treinado_ambiguo",
            "tipo_suspeita": "avaliacao_critica_inteligente",
            "sentimento_previsto": r3.get("classificacao_critica"),
            "score": r3.get("score_critica")
        })
        resultados.append((r3, r3["score"], 0.7))

    emb_entrada = modelo_frases.encode(palavras, convert_to_tensor=True)
    emb_validas = modelo_frases.encode(frases_negativas_permitidas, convert_to_tensor=True)
    sim = util.pytorch_cos_sim(emb_entrada, emb_validas)
    max_sim = sim.max().item()
    if max_sim >= 0.85:
        return [{
            "eh_ofensiva": False,
            "metodo_detectado": "semantica",
            "tipo_suspeita": "critica_aceitavel",
            "score": round(max_sim, 2),
            "sentimento_previsto": "negativo"
        }]

    tox = tox_pipeline(original)[0]
    if tox['label'].lower() == "toxic" and tox['score'] >= 0.75:
        resultado_sent = sentiment_pipeline(original)[0]
        return [{
            "eh_ofensiva": True,
            "metodo_detectado": "modelo_transformer",
            "tipo_suspeita": "toxicidade_modelo",
            "score": tox['score'],
            "sentimento_previsto": resultado_sent['label']
        }]

    resultado_sent = sentiment_pipeline(original)[0]
    label_map = {
        "LABEL_0": "negativo",
        "LABEL_1": "neutro",
        "LABEL_2": "positivo"
    }
    resultados.append(({
        "eh_ofensiva": False,
        "metodo_detectado": "sentimento",
        "tipo_suspeita": "avaliacao_geral",
        "score": resultado_sent['score'],
        "sentimento_previsto": label_map[resultado_sent['label']]
    }, resultado_sent['score'], 0.3))

    melhor = max(resultados, key=lambda x: x[1]*x[2])[0]
    return [melhor]
