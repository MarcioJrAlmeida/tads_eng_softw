import streamlit as st
from app.components.auth import load_auth_config
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

config = load_auth_config()

PERFIS = {
    "Diretor": ["diretor"]
}

def autenticar_usuario(authenticator):    
    if st.session_state.get("authentication_status") is not True:

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            perfil_selecionado = st.selectbox("Selecione seu perfil", list(PERFIS.keys()))
            st.session_state["perfil_selecionado"] = perfil_selecionado

            name, auth_status, username = authenticator.login("Login", location="main")

            if auth_status:
                user_config = config["credentials"]["usernames"].get(username, {})

                if username not in PERFIS[perfil_selecionado]:
                    st.error("Usuário não pertence ao perfil selecionado.")
                    st.stop()

                st.session_state["username"] = username
                st.session_state["name"] = user_config.get("name", "Usuário")
                st.session_state["role"] = user_config.get("role", "user")
                st.session_state["authentication_status"] = True

                if perfil_selecionado == "Diretor":
                    st.switch_page("pages/home.py")
                st.stop()

            elif auth_status is False:
                st.session_state["authentication_status"] = False
                st.error("Usuário ou senha incorretos.")
                st.stop()
            elif auth_status is None:
                st.session_state["authentication_status"] = None
                st.warning("Por favor, insira suas credenciais.")
                st.stop()

### Verificar se o usuário é autenticado.
def verifica_autenticacao(perfil=None):
    if not st.session_state.get("username"):
        st.error("Acesso negado. Por favor, faça login.")
        st.stop()
    if perfil:
        user_role = st.session_state.get("role", "").strip().lower()
        expected_role = perfil.strip().lower()
        if user_role != expected_role:
            st.error(f"Acesso restrito ao perfil: {perfil}")
            st.stop()


from extra_streamlit_components import CookieManager

def mostrar_logout():
    st.markdown(
        """
        <style>
            .logout-button {
                position: absolute;
                top: 20px;
                right: 25px;
                background-color: transparent;
                border: 1px solid #ddd;
                padding: 6px 12px;
                border-radius: 5px;
                font-size: 14px;
                cursor: pointer;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    logout = st.button("Logout", key="logout_button", help="Sair da conta", on_click=realizar_logout)
    return logout

def realizar_logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
    

def load_css(file_name):
    file_path = os.path.join('app', 'assets', 'css', file_name)
    with open(file_path, encoding="utf-8") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        
def load_html(file_name):
    """Carrega e renderiza um arquivo HTML da pasta assets/html."""
    html_path = Path('app/assets/html') / file_name
    with open(html_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
        st.markdown(html_content, unsafe_allow_html=True)


def load_js(file_name):
    file_path = os.path.join('app', 'assets', 'js', file_name)
    with open(file_path, encoding="utf-8") as f:
        js = f.read()
        st.components.v1.html(f"<script>{js}</script>", height=0)
        
def load_footer(file_name="footer.html"):
    file_path = BASE_DIR / "assets" / "html" / file_name
    if not file_path.exists():
        st.error(f"Arquivo HTML não encontrado: {file_path}")
    else:
        with open(file_path, encoding="utf-8") as f:
            html = f.read()
            st.components.v1.html(html, height=100)