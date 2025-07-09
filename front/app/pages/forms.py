import streamlit as st
import requests
from datetime import datetime
from app.components.utils import load_css, load_footer, load_js

st.set_page_config(
    page_title="Avaliação de Docentes",
    page_icon="👨🏼‍🏫",
    layout="centered"
)

load_css("style.css")
load_js("index.js")

st.title("🎮 Avaliação de Docentes")

API_URL = "http://localhost:5001/api/perguntas"
RESPOSTA_API_URL = "http://localhost:5001/api/resposta"
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


def exibir_formulario_avaliacao(perguntas, perfil):
    st.subheader("📋 Formulário de Avaliação Docente")
    respostas = []

    opcoes = {
        1: "Discordo totalmente",
        2: "Discordo",
        3: "Neutro",
        4: "Concordo",
        5: "Concordo totalmente"
    }

    if 'ordem_perguntas' in st.session_state:
        perguntas_ordenadas = [p for id_ in st.session_state['ordem_perguntas'] for p in perguntas if p['id_pergunta'] == id_]
    else:
        perguntas_ordenadas = sorted(perguntas, key=lambda x: x['id_pergunta'])

    qtd_exibir = st.session_state.get('qtd_perguntas_exibir', len(perguntas_ordenadas))
    perguntas_exibidas = perguntas_ordenadas[:qtd_exibir]

    for pergunta in perguntas_exibidas:
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

        respostas.append({
            "id_pergunta": pergunta['id_pergunta'],
            "resposta": opcoes[resposta] if pergunta['tipo_pergunta'].lower() == "fechada" else resposta
        })

    if perfil != "Diretor":
        if st.button("📨 Enviar respostas"):
            try:
                id_avaliacao = st.session_state.get("avaliacao_selecionada", 1)
                sucesso = True

                for r in respostas:
                    payload = {
                        "conteudo_resposta": r["resposta"],
                        "idAvaliacao": id_avaliacao,
                        "id_pergunta": r["id_pergunta"]
                    }
                    response = requests.post(RESPOSTA_API_URL, json=payload)
                    if response.status_code != 201:
                        sucesso = False
                        st.error(f"Erro ao enviar resposta da pergunta {r['id_pergunta']}")

                if sucesso:
                    # Parabéns e animação
                    st.balloons()
                    st.success("🎉 Parabéns! Respostas enviadas com sucesso!")

            except Exception as e:
                st.error(f"Erro ao enviar: {e}")

    else:
        st.info("🔒 Como Diretor, você não pode enviar respostas.")


def main():
    id_avaliacao = st.session_state.get("avaliacao_selecionada", 1)

    if "perguntas" not in st.session_state:
        st.session_state.perguntas = carregar_perguntas()

    if "modelo_avaliacao" not in st.session_state:
        modelo = carregar_modelo_avaliacao(id_avaliacao)
        st.session_state['ordem_perguntas'] = modelo.get("ordem_perguntas", [p['id_pergunta'] for p in st.session_state.perguntas])
        st.session_state['qtd_perguntas_exibir'] = modelo.get("qtd_perguntas_exibir", len(st.session_state.perguntas))

    # Use o perfil salvo na sessão ou padrão "Aluno"
    perfil_usuario = st.session_state.get("perfil_usuario", "Aluno")

    exibir_formulario_avaliacao(st.session_state.perguntas, perfil_usuario)


if __name__ == "__main__":
    main()

load_footer()
