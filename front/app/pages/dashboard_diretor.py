import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts
import requests

from app.components.auth import load_auth_config, create_authenticator
from app.components.utils import realizar_logout, load_css, load_footer, load_js

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

# --- Autenticação ---
config = load_auth_config()
authenticator = create_authenticator(config)
if st.session_state["authentication_status"] is not True:
    st.warning("Você precisa estar logado para acessar esta página.")
    st.switch_page("login.py")

# --- Estilo ---
load_css("style.css")
load_js("index.js")

# --- Sidebar ---
if st.sidebar.button("Home"):
    st.switch_page("pages/home.py")
if st.sidebar.button("Formularios"):
    st.switch_page("pages/edicao_forms.py")
if st.sidebar.button("Dashboard"):
    st.rerun()
if st.sidebar.button("Logout"):
    realizar_logout()

st.title("📊 Dashboard de Avaliações")

# --- Informações institucionais ---
st.sidebar.markdown("---")
st.sidebar.markdown("""
    <h3 style="text-align: center; color: #FFFFFF;">
        Sistema de Avaliação Docente - IFPE Jaboatão
    </h3>
""", unsafe_allow_html=True)

# --- 🔄 Consumir API ---
API_URL = "http://localhost:5001/api/dashboard/fechadas"
try:
    response = requests.get(API_URL)
    if response.status_code == 200:
        dados = response.json()
        if not dados:
            st.warning("⚠️ Nenhum dado disponível para exibir no dashboard.")
            st.stop()
        df = pd.DataFrame(dados)
    else:
        st.error("Erro ao carregar dados do dashboard.")
        st.stop()
except Exception as e:
    st.error(f"Erro de conexão: {str(e)}")
    st.stop()

# --- Filtros ---
with st.sidebar.expander("🔍 Filtros", expanded=True):
    cursos = df["Curso"].unique()
    docentes = df["Professor"].unique()
    periodos = df["Período"].unique()
    perguntas = df["Pergunta"].unique()

    curso_selecionado = st.multiselect("Curso:", sorted(cursos))
    docente_selecionado = st.multiselect("Docente:", sorted(docentes))
    periodo_selecionado = st.multiselect("Período:", sorted(periodos))
    pergunta_selecionada = st.multiselect("Pergunta:", sorted(perguntas))

df_filtrado = df.copy()
if curso_selecionado:
    df_filtrado = df_filtrado[df_filtrado["Curso"].isin(curso_selecionado)]
if docente_selecionado:
    df_filtrado = df_filtrado[df_filtrado["Professor"].isin(docente_selecionado)]
if periodo_selecionado:
    df_filtrado = df_filtrado[df_filtrado["Período"].isin(periodo_selecionado)]
if pergunta_selecionada:
    df_filtrado = df_filtrado[df_filtrado["Pergunta"].isin(pergunta_selecionada)]

# --- KPIs
# KPIs
col1, col2 = st.columns(2)
col1.metric("🧾 Total de Respostas", int(df_filtrado["qtd_respostas"].sum()))
col2.metric("❓ Perguntas Avaliadas", df_filtrado["Pergunta"].nunique())

if df_filtrado.empty:
    st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados.")
else:
    
    # Padronização de cores por tipo de resposta
    cores_personalizadas = {
        "Concordo Totalmente":  "#3498db",   # Verde
        "Concordo": "#2ecc71",              # Verde mais claro
        "Neutro": "#95a5a6",                # Cinza
        "Discordo": "#f1c40f",              # Amarelo
        "Discordo Totalmente": "#e74c3c"    # Vermelho
    }

    st.subheader("📊 Perguntas e Respostas por Professor")

    df_agrupado = df_filtrado.groupby(["Professor", "Pergunta", "Resposta"])["qtd_respostas"].sum().reset_index()

    professores = sorted(df_agrupado["Professor"].unique())
    respostas = sorted(df_agrupado["Resposta"].unique())

    # Montar as séries por tipo de resposta
    series = []
    for resposta in respostas:
        dados = []
        for prof in professores:
            total = df_agrupado[
                (df_agrupado["Professor"] == prof) &
                (df_agrupado["Resposta"] == resposta)
            ]["qtd_respostas"].sum()
            dados.append(int(total))

        cor = cores_personalizadas.get(resposta) 
        series.append({
            "name": resposta,
            "type": "bar",
            "itemStyle": {"color": cor},
            "emphasis": {"focus": "series"},
            "data": dados,
            "barGap": "10%",          
            "barCategoryGap": "40%"
        })

    chart_options = {
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "legend": {"orient": "vertical",
                    "right": 10,
                    "top": "middle"},
        "grid": {
                "left": 80,
                "right": 100,  
                "bottom": 60,
                "containLabel": True
                    },
        "xAxis": {
            "type": "category",
            "data": professores,
            "axisLabel": {"rotate": 0, "interval": 0},
            "name": ""  
        },
        "yAxis": {
            "type": "value",
            "name": ""  
        },
        "series": series
    }

    st_echarts(options=chart_options, height="500px")


    # 📈 Gráfico de linha por Período
    st.subheader("📈 Evolução de Respostas por Período")
    df_linha = df_filtrado.groupby("Período")["qtd_respostas"].sum().reset_index()
    df_linha["qtd_respostas"] = df_linha["qtd_respostas"].astype(int)

    linha_opts = {
        "xAxis": {"type": "category", "data": df_linha["Período"].tolist()},
        "yAxis": {"type": "value"},
        "tooltip": {"trigger": "axis"},
        "series": [{
            "data": df_linha["qtd_respostas"].tolist(),
            "type": "line",
            "smooth": True
        }]
    }
    st_echarts(options=linha_opts, height="400px")

    # 🥧 Pizza de respostas
    st.subheader("🥧 Distribuição Geral de Respostas")
    pizza_data = df_filtrado.groupby("Resposta")["qtd_respostas"].sum().reset_index()
    pizza_data["qtd_respostas"] = pizza_data["qtd_respostas"].astype(int)
    pizza_opts = {
        "tooltip": {"trigger": "item"},
        "legend": {"orient": "vertical",
                    "right": 10,
                    "top": "middle"},
        "grid": {
                "right": 80  
                    },
        "series": [{
            "type": "pie",
            "radius": ["40%", "70%"],
            "avoidLabelOverlap": False,
            "data": [{"value": int(row["qtd_respostas"]), "name": row["Resposta"]} for _, row in pizza_data.iterrows()]
        }]
    }
    st_echarts(options=pizza_opts, height="400px")

    # 🎓 Pizza de cursos
    st.subheader("🎓 Distribuição por Curso")
    curso_data = df_filtrado.groupby("Curso")["qtd_respostas"].sum().reset_index()
    curso_data["qtd_respostas"] = curso_data["qtd_respostas"].astype(int)
    curso_opts = {
        "tooltip": {"trigger": "item"},
        "legend": {"top": "bottom"},
        "series": [{
            "type": "pie",
            "radius": "55%",
            "data": [{"value": int(row["qtd_respostas"]), "name": row["Curso"]} for _, row in curso_data.iterrows()]
        }]
    }
    st_echarts(options=curso_opts, height="400px")

    # Tabela
    with st.expander("📄 Ver dados em tabela"):
        st.dataframe(df_filtrado)
        csv = df_filtrado.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Baixar CSV", csv, file_name="resumo_dashboard.csv", mime="text/csv")

load_footer()
