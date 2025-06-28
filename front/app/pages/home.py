import streamlit as st
from app.components.auth import load_auth_config, create_authenticator
from app.components.utils import realizar_logout, load_css, load_footer, load_js

st.set_page_config(
    page_title="Página Inicial",
    page_icon="🏠",
    layout="centered"
)

# --- Verifica autenticação ---
config = load_auth_config()
authenticator = create_authenticator(config)

if st.session_state["authentication_status"] is not True:
    st.warning("Você precisa estar logado para acessar esta página.")
    st.switch_page("login.py")
    
# 🔥 Captura o perfil do usuário    
perfil = st.session_state.get('perfil_selecionado')

# Carregar CSS, JS
load_css("style.css")
load_js("index.js")

# --- Menu Lateral com Botões ---
st.sidebar.title("≡ Menu")

if st.sidebar.button("🏠 Página Inicial"):
    st.rerun()  # Recarrega a própria página inicial
    
# ✅ Mostrar Edição Formularios apenas para Diretor
if perfil == "Diretor":
    if st.sidebar.button("📝 Edição Formularios"):
        st.switch_page("pages/edicao_forms.py")

if st.sidebar.button("📊 Dashboard"):
    st.switch_page("pages/dashboard_diretor.py")

if st.sidebar.button("🚪 Logout"):
    realizar_logout()
    
st.sidebar.markdown("---")
st.sidebar.info("Sistema de Avaliação Docente - IFPE Jaboatão")

# --- Conteúdo da Página Inicial ---
st.title("🏠 Página Inicial")
st.markdown("""
Bem-vindo ao sistema de avaliação docente desenvolvido como parte do projeto de Engenharia de Software.

Utilize o menu lateral para navegar entre as páginas do sistema.
""")

st.success("Você está na Página Inicial!")

load_footer()