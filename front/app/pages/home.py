import streamlit as st
from app.components.auth import load_auth_config, create_authenticator
from app.components.utils import realizar_logout, load_css, load_footer, load_js


st.set_page_config(
    page_title="SADo",
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

if st.sidebar.button("Home"):
    st.rerun()  # Recarrega a própria página inicial
    
# ✅ Mostrar Formularios apenas para Diretor
if perfil == "Diretor":
    if st.sidebar.button("Formularios"):
        st.switch_page("pages/edicao_forms.py")

if st.sidebar.button("Dashboard"):
    st.switch_page("pages/dashboard_diretor.py")

if st.sidebar.button("Logout"):
    realizar_logout()
    
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <h3 style="text-align: center; color: #FFFFFF;">
        Sistema de Avaliação Docente - IFPE Jaboatão dos Guararapes
    </h3>
    """,
    unsafe_allow_html=True
)


# --- Conteúdo da Página Inicial ---
st.title("🏠 Home")
st.markdown("""
Bem-vindo ao sistema de avaliação docente desenvolvido como parte do projeto de Engenharia de Software.
            
Utilize o menu lateral para navegar entre as páginas do sistema.
            
O sistema permite que você avalie os docentes do IFPE Jaboatão, visualize dashboards e edite formulários de avaliação.
            
Para mais informações, consulte a documentação ou entre em contato com a equipe de desenvolvimento.
""")

st.success("Você está na Página Inicial!")

load_footer()