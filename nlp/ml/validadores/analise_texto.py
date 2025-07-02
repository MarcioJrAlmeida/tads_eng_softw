import unicodedata
from spellchecker import SpellChecker
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from sentence_transformers import SentenceTransformer, util
import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.insert(0, ROOT_DIR)

from nlp.ml.learning.validador_respostas import prever_ofensividade

palavras_ofensivas = [
    # Ofensas gerais
    "merda", "bosta", "porra", "caralho", "cu", "cuzão", "buceta", "pau no cu", "pnc",
    "vai se fuder", "vsf", "vai tomar no cu", "vtnc", "foda-se", "se foder",
    "fodido", "babaca", "idiota", "imbecil", "retardado", "burro", "jumento",
    "otário", "panaca", "mané", "zé ruela", "trouxa", "tapado", "escroto",
    "arrombado", "canalha", "cacete", "desgraça", "inferno", "diabo", "lixo",
    "corno", "corno manso", "corna", "safado", "vagabundo", "sem vergonha", "velho safado",

    # Ofensas sexuais
    "viado", "bicha", "bixona", "boiola", "bichola", "paneleiro", "sapatão",
    "traveco", "travecão", "travesti do caralho", "lambe clitóris", "chupa clitoris",
    "chupa rola", "enfia no cu", "vai chupar um canavial de rola", "boquete",
    "bolagato", "bolcat", "bosseta", "brosca", "brioco", "broxa", "chereca", "chibumba",
    "chibumbo", "bunda", "chupetão", "dar o cu", "tome no cu", "encaixe", "suruba", "dedada",

    # Racismo, preconceito e xenofobia
    "negro de merda", "macaco", "crioulo", "favelado", "pobre de merda",
    "nordestino burro", "paraíba", "baiano preguiçoso", "judeu de merda", "cigano ladrão",

    # Gírias pernambucanas / nordestinas ofensivas
    "fio de rapariga", "fio de uma égua", "arrombadinho", "desmantelado", "fuleira",
    "fuleiragem", "peste", "caba frouxo", "caba safado", "fila de uma peste", "cabra de peia",
    "oxente seu peste", "me arrombe", "doido de pedra", "peste bubônica", "calango doido",
    "cabra safado", "cabra do cão", "diabo loiro", "raparigueiro", "vai pastar", "caba de peia",

    # Ofensas disfarçadas (ironia e duplo sentido)
    "aula de merda", "não ensinou porra nenhuma", "parece que tava bêbado", "ensina igual a minha avó morta",
    "nem meu cachorro entende essa aula", "professor lixo", "explica igual o cu", "pior que calouro perdido",
    "cagou na lousa", "fez um cocô verbal", "parece que tava chapado", "ensina só enrolando", "ensina igual um jumento",
    "mais perdido que cego em tiroteio", "parece um doido", "fala mais que a boca", "fala merda o tempo todo",

    # Ofensas abreviadas
    "fdp", "pnc", "vsf", "vtnc", "pqp", "tmnc", "fds",

    # Composição de insultos com contexto
    "professor burro", "aula lixo", "professor doido", "ensino de bosta", "professor fraco",
    "esse cara é uma piada", "essa mulher é uma anta", "esse aí só sabe gritar", "fala igual uma porta"
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

def remover_acentos(texto):
    return ''.join(c for c in unicodedata.normalize('NFKD', texto) if not unicodedata.combining(c))

def desleet(texto):
    mapa = {'4': 'a', '3': 'e', '1': 'i', '0': 'o', '5': 's', '@': 'a', '$': 's', '!': 'i'}
    for k, v in mapa.items():
        texto = texto.replace(k, v)
    return texto

def contem_ofensa_explicita(texto_limpo):
    for palavra in palavras_ofensivas:
        if palavra in texto_limpo:
            return True, palavra
    return False, None

# === Função principal de análise ===
def analisar_texto(texto, contexto=None):
    original = texto
    texto_limpo = desleet(remover_acentos(original.lower()))

    # (0) Filtro explícito de ofensas (mais direto e eficiente)
    encontrou, termo = contem_ofensa_explicita(texto_limpo)
    if encontrou:
        return [{
            "eh_ofensiva": True,
            "metodo_detectado": "filtro_explicito",
            "tipo_suspeita": f"termo_ofensivo_explicito: {termo}",
            "score": 1.0,
            "sentimento_previsto": None
        }]

    # (1) Classificador supervisionado (modelo treinado)
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
        resultado = sentiment_pipeline(original)[0]
        return [{
            "eh_ofensiva": True,
            "metodo_detectado": "modelo_transformer",
            "tipo_suspeita": "toxicidade_modelo",
            "score": tox['score'],
            "sentimento_previsto": resultado['label']
        }]

    # (4) Sentimento geral
    resultado = sentiment_pipeline(original)[0]
    return [{
        "eh_ofensiva": False,
        "metodo_detectado": "sentimento",
        "tipo_suspeita": "avaliacao_geral",
        "score": round(resultado['score'], 2),
        "sentimento_previsto": resultado['label']
    }]
