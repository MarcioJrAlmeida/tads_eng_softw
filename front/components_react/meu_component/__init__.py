import streamlit as st
import streamlit.components.v1 as components

_component_func = components.declare_component(
    "formulario_programacao_web",
    url="http://localhost:5173",  # <- Quando está no modo desenvolvimento
)

def meu_component(key=None):
    value = _component_func(key=key, default="Aguardando clique")
    return value
