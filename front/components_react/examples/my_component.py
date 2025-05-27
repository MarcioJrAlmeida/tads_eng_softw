import streamlit as st
from meu_component import meu_component

st.set_page_config(page_title="Componente React", layout="centered")

st.title("🚀 Exemplo de Componente React no Streamlit")

resultado = meu_component(key="botao1")

st.write("Valor retornado:", resultado)
