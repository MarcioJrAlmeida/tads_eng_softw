import streamlit as st
import requests
from app.components.utils import load_css, load_js
from datetime import datetime

st.set_page_config(
    page_title="Avaliação de Docentes",
    page_icon="👨🏼‍🏫",
    layout="centered"
)

load_css("style.css")
load_js("index.js")

st.title("🎮 Avaliação de Docentes")

API_URL = "http://localhost:5001/api/perguntas"
RESPOSTA_API_URL = "http://localhost:5001/api/respostas"
MODELO_API_URL = "http://localhost:5001/api/modelo_avaliacao"


@st.cache_data(show_spinner=False)
def carregar_perguntas():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception:
        return []

@st.cache_data(show_spinner=False)
def carregar_modelo_avaliacao(id_avaliacao: int):
    try:
        response = requests.get(f"{MODELO_API_URL}/{id_avaliacao}")
        if response.status_code == 200:
            return response.json()
        else:
            return {}
    except Exception:
        return {}

def exibir_formulario_avaliacao(perguntas):
    st.subheader("Formulário de Avaliação Docente")
    respostas = []

    qtd_exibir = st.session_state.get('qtd_perguntas_exibir', len(perguntas))
    ordem_ids = st.session_state.get('ordem_perguntas', [p['id_pergunta'] for p in perguntas])
    perguntas_ordenadas = [p for id_ in ordem_ids for p in perguntas if p['id_pergunta'] == id_]
    perguntas_exibidas = perguntas_ordenadas[:qtd_exibir]

    alternativas_fechadas_padrao = [
        "Selecione...",
        "Discordo totalmente",
        "Discordo",
        "Neutro",
        "Concordo",
        "Concordo totalmente"
    ]

    with st.form("formulario_avaliacao"):
        for pergunta in perguntas_exibidas:
            if pergunta['tipo_pergunta'].lower() == "fechada":
                resposta = st.radio(pergunta['texto_pergunta'], alternativas_fechadas_padrao, key=f"resposta_{pergunta['id_pergunta']}")
            else:
                resposta = st.text_area(pergunta['texto_pergunta'], key=f"resposta_{pergunta['id_pergunta']}")

            respostas.append({
                "id_pergunta": pergunta['id_pergunta'],
                "resposta": resposta
            })

        submit = st.form_submit_button("Enviar respostas")
        if submit:
            for r in respostas:
                if r["resposta"] == "Selecione...":
                    st.warning("Por favor, selecione uma resposta para todas as perguntas fechadas.")
                    return

            payload = {
                "respostas": respostas,
                "data_hr_registro": datetime.now().isoformat()
            }
            try:
                response = requests.post(RESPOSTA_API_URL, json=payload)
                if response.status_code == 201:
                    st.success("Respostas enviadas com sucesso!")
                else:
                    st.error("Erro ao enviar respostas.")
            except Exception as e:
                st.error(f"Erro ao enviar: {e}")

def main():
    id_avaliacao = st.session_state.get("avaliacao_selecionada", 1)

    if "perguntas" not in st.session_state:
        st.session_state.perguntas = carregar_perguntas()

    if "modelo_avaliacao" not in st.session_state:
        modelo = carregar_modelo_avaliacao(id_avaliacao)
        st.session_state['ordem_perguntas'] = modelo.get("ordem_perguntas", [p['id_pergunta'] for p in st.session_state.perguntas])
        st.session_state['qtd_perguntas_exibir'] = modelo.get("qtd_perguntas_exibir", len(st.session_state.perguntas))

    exibir_formulario_avaliacao(st.session_state.perguntas)

if __name__ == "__main__":
    main()
