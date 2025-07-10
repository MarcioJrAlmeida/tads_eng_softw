import streamlit as st
import requests
from datetime import datetime
from app.components.utils import load_css, load_footer, load_js

st.set_page_config(page_title="Avaliação de Docentes", page_icon="👨🏼‍🏫", layout="centered")
load_css("style.css")
load_js("index.js")

st.title("🎮 Avaliação de Docentes")

# URLs da API
PERGUNTAS_API = "http://localhost:5001/api/perguntas"
RESPOSTA_API_URL = "http://localhost:5001/api/resposta"
MODELO_API_URL = "http://localhost:5001/api/modelo_avaliacao"
DOCENTES_API_URL = "http://localhost:5001/api/disciplinas_docente"
RESPOSTAS_DOCENTES_API = "http://localhost:5001/api/docentes_avaliados"
AVALIACOES_API = "http://localhost:5001/api/avaliacoes"

@st.cache_data(show_spinner=False)
def carregar_perguntas():
    try:
        response = requests.get(PERGUNTAS_API)
        return response.json() if response.status_code == 200 else []
    except:
        return []

@st.cache_data(show_spinner=False)
def carregar_modelo_avaliacao(id_avaliacao: int):
    try:
        response = requests.get(f"{MODELO_API_URL}/{id_avaliacao}")
        return response.json() if response.status_code == 200 else {}
    except:
        return {}

@st.cache_data(show_spinner=False)
def carregar_docentes():
    try:
        response = requests.get(DOCENTES_API_URL)
        return response.json() if response.status_code == 200 else []
    except:
        return []

@st.cache_data(show_spinner=False)
def carregar_docentes_disponiveis(id_avaliacao):
    try:
        docentes = carregar_docentes()
        ja_avaliados = buscar_professores_ja_avaliados(id_avaliacao)
        return [
            d for d in docentes if int(d['id_disciplina_docente']) not in [int(x) for x in ja_avaliados]
        ]
    except:
        return []

def buscar_professores_ja_avaliados(id_avaliacao: int):
    try:
        response = requests.get(f"{RESPOSTAS_DOCENTES_API}?id_avaliacao={id_avaliacao}")
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def obter_avaliacao_ativa():
    try:
        response = requests.get(AVALIACOES_API)
        if response.status_code == 200:
            for a in response.json():
                if a.get("status_avaliacao") == "Ativo":
                    return a["id_avaliacao"]
    except:
        return None

@st.fragment
def bloco_pergunta(pergunta, opcoes):
    texto_curto = pergunta['texto_pergunta'][:80] + ("..." if len(pergunta['texto_pergunta']) > 80 else "")
    if pergunta['tipo_pergunta'].lower() == "fechada":
        resposta = st.radio(
            texto_curto,
            opcoes,
            key=f"resposta_{pergunta['id_pergunta']}",
            horizontal=True
        )
    else:
        resposta = st.text_area(pergunta['texto_pergunta'], key=f"resposta_{pergunta['id_pergunta']}")
    return {
        "id_pergunta": pergunta['id_pergunta'],
        "resposta": opcoes[resposta] if pergunta['tipo_pergunta'].lower() == "fechada" else resposta
    }

def exibir_formulario_avaliacao(perguntas, id_disciplina_docente, id_avaliacao):
    st.subheader("📋 Formulário de Avaliação Docente")
    respostas = []

    opcoes = {
        1: "Discordo totalmente",
        2: "Discordo",
        3: "Neutro",
        4: "Concordo",
        5: "Concordo totalmente"
    }

    perguntas_ordenadas = sorted(perguntas, key=lambda x: x['id_pergunta'])
    qtd_exibir = st.session_state.get('qtd_perguntas_exibir', len(perguntas_ordenadas))
    perguntas_exibidas = perguntas_ordenadas[:qtd_exibir]

    for pergunta in perguntas_exibidas:
        resposta = bloco_pergunta(pergunta, opcoes)
        respostas.append(resposta)

    if st.button("📨 Enviar respostas"):
        sucesso = True
        for r in respostas:
            payload = {
                "conteudo_resposta": r["resposta"],
                "idAvaliacao": id_avaliacao,
                "id_pergunta": r["id_pergunta"],
                "id_disciplina_docente": id_disciplina_docente
            }
            response = requests.post(RESPOSTA_API_URL, json=payload)
            if response.status_code != 201:
                sucesso = False
                st.error(f"Erro ao enviar resposta da pergunta {r['id_pergunta']}")

        if sucesso:
            st.balloons()
            st.success("🎉 Respostas enviadas com sucesso!")
            st.rerun()

def main():
    id_avaliacao = obter_avaliacao_ativa()
    if not id_avaliacao:
        st.warning("Nenhuma avaliação foi lançada no momento. Aguarde...")
        return
    
    if "modelo" not in st.session_state:
        st.session_state.modelo = carregar_modelo_avaliacao(id_avaliacao)

    ordem_ids = st.session_state.modelo.get("ordem_perguntas", [])
    qtd_exibir = st.session_state.modelo.get("qtd_perguntas_exibir", len(ordem_ids))    

    todas_perguntas = carregar_perguntas()
    # Só pega perguntas que estão no modelo da avaliação
    perguntas_filtradas = [p for p in todas_perguntas if p["id_pergunta"] in ordem_ids] 

    # Ordena de acordo com o modelo
    perguntas_ordenadas = sorted(perguntas_filtradas, key=lambda p: ordem_ids.index(p["id_pergunta"]))  

    # Atualiza session_state
    st.session_state.perguntas = perguntas_ordenadas
    st.session_state.qtd_perguntas_exibir = qtd_exibir

    docentes_disponiveis = carregar_docentes_disponiveis(id_avaliacao)

    if docentes_disponiveis:
        nomes = {f"{d['nome_docente']} - {d['nome_disciplina']}": d['id_disciplina_docente'] for d in docentes_disponiveis}
        opcao = st.selectbox("👨‍🏫 Selecione o professor a ser avaliado:", list(nomes.keys()))
        if opcao:
            id_disciplina_docente = nomes[opcao]
            exibir_formulario_avaliacao(st.session_state.perguntas, id_disciplina_docente, id_avaliacao)
    else:
        st.success("✅ Você já avaliou todos os professores disponíveis!")

if __name__ == "__main__":
    main()

load_footer()
