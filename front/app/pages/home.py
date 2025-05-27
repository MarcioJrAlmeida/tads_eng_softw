import streamlit as st
import pandas as pd
from app.components.auth import load_auth_config, create_authenticator
from app.components.utils import realizar_logout, load_css, load_footer, load_js


# ---------------------- CONFIGURAÇÕES ----------------------
st.set_page_config(
    page_title="Página Inicial",
    page_icon="🏠",
    layout="wide"
)

# 🔐 Verifica autenticação
config = load_auth_config()
authenticator = create_authenticator(config)

if st.session_state["authentication_status"] is not True:
    st.warning("Você precisa estar logado para acessar esta página.")
    st.switch_page("login.py")

perfil = st.session_state.get('perfil_selecionado')

# Carrega CSS e JS
load_css("style.css")
load_js("index.js")


# ---------------------- MENU LATERAL ----------------------
st.sidebar.markdown("<h2>☰ Menu</h2>", unsafe_allow_html=True)

if st.sidebar.button("🏠 Página Inicial"):
    st.rerun()

if perfil == "Diretor":
    if st.sidebar.button("📝 Edição de Formulários"):
        st.rerun()

if st.sidebar.button("📊 Dashboard"):
    st.switch_page("pages/dashboard_diretor.py")

if st.sidebar.button("🚪 Logout"):
    realizar_logout()

st.sidebar.markdown("---")
st.sidebar.info("Sistema de Avaliação Docente - IFPE Jaboatão")


# ---------------------- CONTEÚDO PRINCIPAL ----------------------
st.markdown("<h1 style='text-align: center;'>🏠 Página Inicial</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>Bem-vindo ao Sistema de Avaliação Docente - IFPE Jaboatão</h4>", unsafe_allow_html=True)


# ---------------------- KPI's (Indicadores) ----------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Formulários Respondidos", value="68", delta="+5 esta semana")
with col2:
    st.metric(label="Formulários Totais", value="85")
with col3:
    st.metric(label="Formulários Pendentes", value="17", delta="-2")

st.markdown("---")


# ---------------------- INFORMAÇÕES BÁSICAS ----------------------
st.subheader("📚 Informações Gerais")
st.markdown("""
- **Período de Avaliação:** 2025.1  
- **Total de Docentes Avaliados:** 25  
- **Participação Atual dos Alunos:** 80%  
- **Responsável pela Avaliação:** Coordenação de Ensino
""")

st.markdown("---")


# ---------------------- NOTÍCIAS DO IFPE ----------------------
st.subheader("📰 Últimas Notícias do IFPE Jaboatão")
col_noticia1, col_noticia2 = st.columns(2)

with col_noticia1:
    st.info("""**Edital aberto para Monitoria 2025.1**  
    Confira as regras e inscreva-se no site oficial do IFPE.""")

    st.info("""**Semana de Extensão começa dia 15/06**  
    Participe das oficinas e palestras gratuitas.""")

with col_noticia2:
    st.info("""**Resultado do ENADE 2024 divulgado**  
    Parabéns aos alunos e docentes pela nota de excelência!""")

    st.info("""**Abertura de inscrições para cursos de extensão**  
    Acesse o portal do IFPE para mais informações.""")

st.markdown("---")


# ---------------------- RODAPÉ ----------------------
load_footer()

