import streamlit as st
import streamlit.components.v1 as components
from app.components.utils import load_css, load_footer

st.set_page_config(page_title="Formulário - Programação Web 1", layout="centered")

load_css("style.css")

st.title("🖥️ Programação Web 1")

# Carrega o React (gerado pelo Vite)
components.html(
    """
    <iframe src="http://localhost:5173" width="100%" height="600" style="border:none;"></iframe>
    """,
    height=700,
)

load_footer()
