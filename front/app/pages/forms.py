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

def carregar_perguntas():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            return response.json()
        else:
            st.error("Erro ao carregar perguntas.")
            return []
    except Exception as e:
        st.error(f"Erro: {str(e)}")
        return []

def carregar_modelo_avaliacao(id_avaliacao: int):
    try:
        response = requests.get(f"http://localhost:5001/api/modelo_avaliacao/{id_avaliacao}")
        if response.status_code == 200:
            return response.json()
        else:
            return {}
    except Exception as e:
        st.error(f"Erro ao buscar modelo de avaliação: {str(e)}")
        return {}

def exibir_formulario_avaliacao(perguntas):
    st.subheader("Formulário de Avaliação Docente")
    respostas = []

    if 'ordem_perguntas' in st.session_state:
        perguntas_ordenadas = [p for id_ in st.session_state['ordem_perguntas'] for p in perguntas if p['id_pergunta'] == id_]
    else:
        perguntas_ordenadas = sorted(perguntas, key=lambda x: x['id_pergunta'])

    qtd_exibir = st.session_state.get('qtd_perguntas_exibir', len(perguntas_ordenadas))
    perguntas_exibidas = perguntas_ordenadas[:qtd_exibir]

    alternativas_fechadas_padrao = [
        "Selecione...",
        "Discordo totalmente",
        "Discordo",
        "Neutro",
        "Concordo",
        "Concordo totalmente"
    ]

    for pergunta in perguntas_exibidas:
        if pergunta['tipo_pergunta'].lower() == "fechada":
            resposta = st.radio(pergunta['texto_pergunta'], alternativas_fechadas_padrao, key=f"resposta_{pergunta['id_pergunta']}")
        else:
            resposta = st.text_area(pergunta['texto_pergunta'], key=f"resposta_{pergunta['id_pergunta']}")

        respostas.append({"id_pergunta": pergunta['id_pergunta'], "resposta": resposta})

    if st.button("Enviar respostas"):
        for r in respostas:
            if r["resposta"] == "Selecione...":
                st.warning("Por favor, selecione uma resposta para todas as perguntas fechadas.")
                return

        payload = {
            "respostas": respostas,
            "data_hr_registro": datetime.now().isoformat()
        }
        response = requests.post(RESPOSTA_API_URL, json=payload)
        if response.status_code == 201:
            st.success("Respostas enviadas com sucesso!")
        else:
            st.error("Erro ao enviar respostas.")

def main():

    perguntas = carregar_perguntas()
    id_avaliacao = st.session_state.get("avaliacao_selecionada", 1)
    modelo = carregar_modelo_avaliacao(id_avaliacao)

    if modelo:
        st.session_state['ordem_perguntas'] = modelo.get("ordem_perguntas", [])
        st.session_state['qtd_perguntas_exibir'] = modelo.get("qtd_perguntas_exibir", len(perguntas))
    else:
        st.session_state['ordem_perguntas'] = [p['id_pergunta'] for p in perguntas]
        st.session_state['qtd_perguntas_exibir'] = len(perguntas)

    exibir_formulario_avaliacao(perguntas)

if __name__ == "__main__":
    main()