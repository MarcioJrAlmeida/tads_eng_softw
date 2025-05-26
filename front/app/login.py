import streamlit as st
from app.components.utils import autenticar_usuario, load_css, load_html

st.set_page_config(page_title="Login", layout="centered")  # deve ser 1º Streamlit

load_html("header.html")
load_css("style.css")

from app.components.auth import load_auth_config, create_authenticator
from app.components.utils import autenticar_usuario

config = load_auth_config()
authenticator = create_authenticator(config)

autenticar_usuario(authenticator)
st.write("Sessão atual:", st.session_state)