import streamlit as st
from app.components.auth import load_auth_config
from pathlib import Path


# === Diretórios base ===
BASE_DIR = Path(__file__).resolve().parent.parent  # app/
ASSETS_DIR = BASE_DIR / "assets"
HTML_DIR = ASSETS_DIR / "html"
CSS_DIR = ASSETS_DIR / "css"
JS_DIR = ASSETS_DIR / "js"

# === Carregar configurações de autenticação ===
config = load_auth_config()

# === Perfis ===
PERFIS = {
    "Diretor": ["diretor"],
    "Coordenador": ["coordenador"]
}


# === Autenticação ===
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


# === Verificar Autenticação ===
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


# === Logout ===
def realizar_logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


# === Logout estilizado ===
def mostrar_logout():
    st.markdown("""
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
    """, unsafe_allow_html=True)

    logout = st.button("Logout", key="logout_button", help="Sair da conta", on_click=realizar_logout)
    return logout


# === Loader CSS ===
def load_css(file_name):
    file_path = CSS_DIR / file_name
    if not file_path.exists():
        st.error(f"Arquivo CSS não encontrado: {file_path}")
    else:
        with open(file_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# === Loader HTML ===
def load_html(file_name):
    file_path = HTML_DIR / file_name
    if not file_path.exists():
        st.error(f"Arquivo HTML não encontrado: {file_path}")
    else:
        with open(file_path, encoding="utf-8") as f:
            st.markdown(f.read(), unsafe_allow_html=True)


# === Loader Footer específico ===
def load_footer(file_name="footer.html"):
    file_path = HTML_DIR / file_name
    if not file_path.exists():
        st.error(f"Arquivo HTML não encontrado: {file_path}")
    else:
        with open(file_path, encoding="utf-8") as f:
            st.components.v1.html(f.read(), height=100)


# === Loader JavaScript ===
def load_js(file_name):
    file_path = JS_DIR / file_name
    if not file_path.exists():
        st.error(f"Arquivo JS não encontrado: {file_path}")
    else:
        with open(file_path, encoding="utf-8") as f:
            js = f.read()
            st.components.v1.html(f"<script>{js}</script>", height=0)
