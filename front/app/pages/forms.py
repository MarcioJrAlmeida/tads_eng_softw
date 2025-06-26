import streamlit as st
import requests
from app.components.auth import load_auth_config, create_authenticator
from app.components.utils import realizar_logout, load_css, load_footer, load_js
from datetime import datetime

st.set_page_config(
    page_title="Avaliação de Docentes",
    page_icon="👨🏼‍🏫",
    layout="centered"
)

# --- Verifica autenticação ---
config = load_auth_config()
authenticator = create_authenticator(config)

if st.session_state["authentication_status"] is not True:
    st.warning("Você precisa estar logado para acessar esta página.")
    st.switch_page("login.py")

# Carregar CSS, JS
load_css("style.css")
load_js("index.js")


# --- Menu Lateral com Botões ---
st.sidebar.title("≡ Menu")

if st.sidebar.button("🏠 Página Inicial"):
    st.switch_page("pages/home.py")

if st.sidebar.button("📝 Edição Formularios"):
    st.rerun()

if st.sidebar.button("📊 Dashboard"):
    st.switch_page("pages/dashboard_diretor.py")

if st.sidebar.button("🚪 Logout"):
    realizar_logout()

st.title("🎮 Avaliação de Docentes")

API_URL = "http://localhost:5001/api/perguntas"
RESPOSTA_API_URL = "http://localhost:5001/api/respostas"

# --------------------------
# Funções de API
# --------------------------
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

def cadastrar_nova_pergunta():
    texto = st.text_input("Texto da nova pergunta")
    tipo = st.selectbox("Tipo de pergunta", ["fechada", "aberta"])
    if st.button("Cadastrar pergunta"):
        payload = [{
            "texto_pergunta": texto,
            "tipo_pergunta": tipo
        }]
        response = requests.post(API_URL, json=payload)
        if response.status_code == 201:
            st.success("Pergunta cadastrada com sucesso!")
        else:
            st.error("Erro ao cadastrar pergunta.")

def editar_perguntas_existentes():
    perguntas = carregar_perguntas()
    for pergunta in perguntas:
        with st.expander(f"Editar: {pergunta['texto_pergunta']}"):
            novo_texto = st.text_input("Novo texto", value=pergunta['texto_pergunta'], key=f"texto_{pergunta['id_pergunta']}")
            novo_tipo = st.selectbox("Novo tipo", ["fechada", "aberta"], index=0 if pergunta['tipo_pergunta'] == "fechada" else 1, key=f"tipo_{pergunta['id_pergunta']}")
            if st.button("Salvar", key=f"salvar_{pergunta['id_pergunta']}"):
                payload = {
                    "texto_pergunta": novo_texto,
                    "tipo_pergunta": novo_tipo
                }
                url = f"{API_URL}/{pergunta['id_pergunta']}"
                response = requests.put(url, json=payload)
                if response.status_code == 200:
                    st.success("Pergunta atualizada!")
                else:
                    st.error("Erro ao atualizar pergunta.")

def exibir_formulario_avaliacao(perguntas):
    st.subheader("Formulário de Avaliação Docente")
    respostas = []
    for pergunta in perguntas:
        if pergunta['tipo_pergunta'] == "fechada":
            resposta = st.radio(pergunta['texto_pergunta'], ["Discordo totalmente", "Discordo", "Neutro", "Concordo", "Concordo totalmente"], key=f"resposta_{pergunta['id_pergunta']}")
        else:
            resposta = st.text_area(pergunta['texto_pergunta'], key=f"resposta_{pergunta['id_pergunta']}")
        respostas.append({
            "id_pergunta": pergunta['id_pergunta'],
            "resposta": resposta
        })

    if st.button("Enviar respostas"):
        payload = {
            "matricula": st.session_state.get("username", "anon"),
            "respostas": respostas,
            "data_hr_registro": datetime.now().isoformat()
        }
        response = requests.post(RESPOSTA_API_URL, json=payload)
        if response.status_code == 201:
            st.success("Respostas enviadas com sucesso!")
        else:
            st.error("Erro ao enviar respostas.")

def main():
    perfil = st.session_state.get("Diretor", "Aluno")

    if perfil == "Diretor":
        st.subheader("Gerenciar Perguntas do Formulário")
        cadastrar_nova_pergunta()
        editar_perguntas_existentes()
    else:
        perguntas = carregar_perguntas()
        exibir_formulario_avaliacao(perguntas)

if __name__ == "__main__":
    main()
