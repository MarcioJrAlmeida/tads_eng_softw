import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from app.components.auth import load_auth_config, create_authenticator
from app.components.utils import realizar_logout, load_css, load_footer, load_js

st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide"
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

if st.sidebar.button("Home"):
    st.switch_page("pages/home.py")
    
if st.sidebar.button("Formularios"):
    st.switch_page("pages/edicao_forms.py")

if st.sidebar.button("Dashboard"):
    st.rerun()  # Recarrega a própria

if st.sidebar.button("Logout"):
    realizar_logout()

st.title("📊 Dashboard de Avaliações")

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <h3 style="text-align: center; color: #FFFFFF;">
        Sistema de Avaliação Docente - IFPE Jaboatão
    </h3>
    """,
    unsafe_allow_html=True
)

# 🔥 Dados simulados
np.random.seed(42)

docentes = ['Prof. A', 'Prof. B', 'Prof. C', 'Prof. D']
cursos = ['ADS', 'Administração']

cadeiras_ads = [
    'Programação Web 1', 'Lógica de Programação', 'Sistemas Operacionais',
    'Inglês 1', 'Fundamentos da Informática', 'Ética Profissional e Cidadania',
    'Redes de Computadores'
]
cadeiras_adm = [
    'Administração Financeira', 'Gestão de Pessoas', 'Marketing Empresarial',
    'Ética Profissional e Cidadania', 'Contabilidade Básica',
    'Logística Empresarial', 'Economia e Mercados'
]

periodos = ['2024.2', '2025.1']

dados = []

for periodo in periodos:
    for curso in cursos:
        cadeiras = cadeiras_ads if curso == 'ADS' else cadeiras_adm
        for cadeira in cadeiras:
            for docente in docentes:
                n_formularios = np.random.randint(5, 20)
                medias = np.round(np.random.uniform(3.5, 5.0, n_formularios), 1)
                for media in medias:
                    dados.append({
                        'Curso': curso,
                        'Cadeira': cadeira,
                        'Docente': docente,
                        'Período': periodo,
                        'Média': media
                    })

df = pd.DataFrame(dados)

# ------------------- 🔍 Filtros Dependentes -------------------

with st.sidebar.expander("🔍 Filtros", expanded=True):
    # --- Filtro Curso ---
    curso_selecionado = st.multiselect(
        "Filtrar por Curso:", options=df['Curso'].unique()
    )

    # --- Filtrar cadeiras baseado no curso selecionado ---
    if curso_selecionado:
        cadeiras_disponiveis = df[df['Curso'].isin(curso_selecionado)]['Cadeira'].unique()
    else:
        cadeiras_disponiveis = df['Cadeira'].unique()

    cadeira_selecionada = st.multiselect(
        "Filtrar por Cadeira:", options=sorted(cadeiras_disponiveis)
    )

    # --- Filtro Docente ---
    docente_selecionado = st.multiselect(
        "Filtrar por Docente:", options=df['Docente'].unique()
    )

    # --- Filtro Período ---
    periodo_selecionado = st.multiselect(
        "Filtrar por Período:", options=df['Período'].unique()
    )

# ------------------- 🔥 Aplicar Filtros -------------------

df_filtrado = df.copy()

if curso_selecionado:
    df_filtrado = df_filtrado[df_filtrado['Curso'].isin(curso_selecionado)]

if cadeira_selecionada:
    df_filtrado = df_filtrado[df_filtrado['Cadeira'].isin(cadeira_selecionada)]

if docente_selecionado:
    df_filtrado = df_filtrado[df_filtrado['Docente'].isin(docente_selecionado)]

if periodo_selecionado:
    df_filtrado = df_filtrado[df_filtrado['Período'].isin(periodo_selecionado)]

# ------------------- 📊 KPIs -------------------

col1, col2 = st.columns(2)

with col1:
    st.metric(
        label="📄 Total de Formulários Preenchidos",
        value=f"{df_filtrado.shape[0]}"
    )

with col2:
    media_global = df_filtrado['Média'].mean()
    st.metric(
        label="⭐ Média Global",
        value=f"{media_global:.2f}" if not np.isnan(media_global) else "0.00"
    )

# ------------------- 📈 Gráfico -------------------

#Gráfico de coluna
if df_filtrado.empty:
    st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados.")
else:
    fig = px.bar(
        df_filtrado.groupby(['Docente', 'Período']).mean(numeric_only=True).reset_index(),
        x='Docente',
        y='Média',
        color='Período',
        barmode='group',
        title="Média de Avaliações por Docente"
    )

    st.plotly_chart(fig, use_container_width=True)

#Gráfico Pizza
respostas = {
    "Concordo totalmente": 40,
    "Concordo": 30,
    "Neutro": 20,
    "Discordo": 5,
    "Discordo totalmente": 5
}

fig = px.pie(
    names=list(respostas.keys()),
    values=list(respostas.values()),
    title="Distribuição das Respostas",
    color_discrete_sequence=px.colors.sequential.Greens
)
st.plotly_chart(fig)

#Gráficos em linhas
import plotly.graph_objects as go

periodos = ["2023.1", "2023.2", "2024.1", "2024.2"]
pontuacoes = [3.2, 3.5, 4.1, 4.5]

fig = go.Figure()
fig.add_trace(go.Scatter(x=periodos, y=pontuacoes, mode='lines+markers', line=dict(color="#007E3D")))
fig.update_layout(title="Média das Avaliações por Período", xaxis_title="Período", yaxis_title="Nota Média")
st.plotly_chart(fig)



# ------------------- 📄 Tabela + Download -------------------

with st.expander("📄 Ver dados em tabela"):
    st.dataframe(df_filtrado)

    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Baixar Tabela em CSV",
        data=csv,
        file_name='avaliacoes_filtradas.csv',
        mime='text/csv'
    )

st.info("Este é um exemplo de visualização. Dados reais estarão conectados ao banco.")

load_footer()
