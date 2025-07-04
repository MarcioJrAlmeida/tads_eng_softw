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
    palavras = texto_limpo.split()
    
     # (0) Verificação por palavras ofensivas explícitas
    for palavra in palavras:
        if palavra in palavras_ofensivas:
            resultado_sent = sentiment_pipeline(original)[0]
            return [{
                "eh_ofensiva": True,
                "metodo_detectado": "palavra_ofensiva",
                "tipo_suspeita": "ofensa_explicita",
                "score_ofensa_explicita": 1.0,
                "sentimento_previsto": resultado_sent["label"]
            }]

    # (1) Classificador supervisionado de OFENSIVIDADE
    if contexto:
        resultado_ofensivo = prever_ofensividade(contexto, texto)
        if resultado_ofensivo.get("score", 0) >= 0.5:
            return [{
                "eh_ofensiva": resultado_ofensivo["eh_ofensiva"],
                "metodo_detectado": "modelo_treinado_ofensivo",
                "tipo_suspeita": "ofensividade_supervisionada",
                "score_ofensivo": resultado_ofensivo.get("score", 0),
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
            "score_semantica": 1.0,
            "sentimento_previsto": "negativo"
        }]

    # (3) Modelo de toxicidade
    tox = tox_pipeline(original)[0]
    if tox['label'].lower() == "toxic" and tox['score'] >= 0.75:
        resultado_sent = sentiment_pipeline(original)[0]
        return [{
            "eh_ofensiva": True,
            "metodo_detectado": "modelo_transformer",
            "tipo_suspeita": "toxicidade_modelo",
            "score_toxidade": tox['score'],
            "sentimento_previsto": resultado_sent['label']
        }]

    # (4) Modelo supervisionado de ANÁLISE CRÍTICA (sentimento inteligente)
    if contexto:
        resultado_critico = prever_analise_critica(contexto, texto)
        if resultado_critico.get("score_critica", 0) >= 0.5:
            return [{
                "eh_ofensiva": False,
                "metodo_detectado": "modelo_treinado_critico",
                "tipo_suspeita": "avaliacao_critica_inteligente",
                "score_critica": resultado_critico.get("score_critica", 0),
                "sentimento_previsto": resultado_critico.get("classificacao_critica", 0)
            }]

    # (5) Fallback: Modelo de sentimento geral
    resultado_sent = sentiment_pipeline(original)[0]
    label_map = {
    "LABEL_0": "negativo",
    "LABEL_1": "neutro",
    "LABEL_2": "positivo"
    }
    return [{
        "eh_ofensiva": False,
        "metodo_detectado": "sentimento",
        "tipo_suspeita": "avaliacao_geral",
        "score_ml_sentimento": round(resultado_sent['score'], 2),
        "sentimento_previsto": label_map[resultado_sent['label']]
    }]

# Teste direto
if __name__ == "__main__":
    resultado = analisar_texto("Como você avalia o desempenho do professor durante o semestre?", "O professor atuou como um simples acadêmico, toda vez que tinha pergunta que ele não sabia ele era rispido com o alluno que perguntou.")
    print("Resultado estruturado:", resultado)