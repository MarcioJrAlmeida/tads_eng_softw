from app.components.auth import load_auth_config, create_authenticator
from app.components.utils import realizar_logout, load_css, load_footer, load_js
from streamlit_echarts import st_echarts
import streamlit as st
import pandas as pd
import requests
import sys, os
from collections import Counter

# Config inicial
st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
load_css("style.css")
load_js("index.js")

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.insert(0, ROOT_DIR)
from nlp.ml.preprocessing.classificacao_respostas import processar_respostas, buscar_respostas_abertas

API_URL = "http://localhost:5001/api/dashboard/fechadas"
API_URL_ABERTAS = "http://localhost:5001/api/dashboard/abertas"

# Autenticação
def autenticar_usuario():
    config = load_auth_config()
    authenticator = create_authenticator(config)
    if st.session_state["authentication_status"] is not True:
        st.warning("Você precisa estar logado para acessar esta página.")
        st.switch_page("login.py")

# Sidebar
def montar_sidebar():
    if st.sidebar.button("Home"):
        st.switch_page("pages/home.py")
    if st.sidebar.button("Formularios"):
        st.switch_page("pages/edicao_forms.py")
    if st.sidebar.button("Dashboard"):
        st.rerun()
    if st.sidebar.button("Logout"):
        realizar_logout()
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
        <h3 style="text-align: center; color: #FFFFFF;">
            Sistema de Avaliação Docente - IFPE Jaboatão
        </h3>
    """, unsafe_allow_html=True)

# Verifica e processa respostas abertas
def verificar_respostas_abertas():
    respostas_abertas = buscar_respostas_abertas()
    if not respostas_abertas.empty:
        st.info("🔎 Existem respostas abertas ainda não analisadas por Machine Learning.")
    else:
        st.success("✅ Todas as respostas já foram analisadas por Machine Learning.")

    if st.button("🔄 Atualizar"):
        with st.spinner("Processando respostas e atualizando dados..."):
            processar_respostas()
            st.rerun()

# Função para consumir API de respostas fechadas
def carregar_dados_fechados():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            dados = response.json()
            if not dados:
                st.warning("⚠️ Nenhum dado disponível para exibir no dashboard.")
                st.stop()
            return pd.DataFrame(dados)
        else:
            st.error("Erro ao carregar dados do dashboard.")
            st.stop()
    except Exception as e:
        st.error(f"Erro de conexão: {str(e)}")
        st.stop()

# Filtros
def aplicar_filtros(df):
    with st.sidebar.expander("🔍 Filtros", expanded=True):
        curso = st.multiselect("Curso:", sorted(df["Curso"].unique()))
        docente = st.multiselect("Docente:", sorted(df["Professor"].unique()))
        periodo = st.multiselect("Período:", sorted(df["Período"].unique()))
        pergunta = st.multiselect("Pergunta:", sorted(df["Pergunta"].unique()))

    df_filtrado = df.copy()
    if curso:
        df_filtrado = df_filtrado[df_filtrado["Curso"].isin(curso)]
    if docente:
        df_filtrado = df_filtrado[df_filtrado["Professor"].isin(docente)]
    if periodo:
        df_filtrado = df_filtrado[df_filtrado["Período"].isin(periodo)]
    if pergunta:
        df_filtrado = df_filtrado[df_filtrado["Pergunta"].isin(pergunta)]

    filtros_ativos = []
    if curso:
        filtros_ativos.append(f"**Curso:** {', '.join(curso)}")
    if docente:
        filtros_ativos.append(f"**Docente:** {', '.join(docente)}")
    if periodo:
        filtros_ativos.append(f"**Período:** {', '.join(map(str, periodo))}")
    if pergunta:
        filtros_ativos.append(f"**Pergunta:** {', '.join(pergunta)}")
    if filtros_ativos:
        st.markdown("🎯 **Filtros Ativos:**  \n" + " | ".join(filtros_ativos))

    return df_filtrado

# KPIs
def mostrar_kpis(df):
    col1, col2 = st.columns(2)
    col1.metric("🧾 Total de Respostas", int(df["qtd_respostas"].sum()))
    col2.metric("❓ Perguntas Avaliadas", df["Pergunta"].nunique())

# Gráficos de Respostas Fechadas
def grafico_barras_professor(df):
    st.subheader("📊 Perguntas e Respostas por Professor")
    df_group = df.groupby(["Professor", "Pergunta", "Resposta"])["qtd_respostas"].sum().reset_index()
    professores = sorted(df_group["Professor"].unique())
    respostas = sorted(df_group["Resposta"].unique())
    cores = {
        "Concordo totalmente":  "#416cbd",
        "Concordo": "#3ddf3d",
        "Neutro": "#cccaca",
        "Discordo": "#ffbf00",
        "Discordo totalmente": "#d62728"
    }

    series = []
    for resposta in respostas:
        dados = []
        for prof in professores:
            total = df_group[(df_group["Professor"] == prof) & (df_group["Resposta"] == resposta)]["qtd_respostas"].sum()
            dados.append(int(total))
        series.append({
            "name": resposta,
            "type": "bar",
            "itemStyle": {"color": cores.get(resposta)},
            "data": dados
        })

    st_echarts({
        "tooltip": {"trigger": "axis"},
        "xAxis": {"type": "category", "data": professores, "axisLabel": {"rotate": 15}},
        "yAxis": {"type": "value"},
        "series": series
    }, height="500px")

# Gráfico de Linha por Período
def grafico_linha_periodo(df):
    st.subheader("📈 Evolução de Respostas por Período")
    df_linha = df.groupby("Período")["qtd_respostas"].sum().reset_index()
    st_echarts({
        "xAxis": {"type": "category", "data": df_linha["Período"].tolist()},
        "yAxis": {"type": "value"},
        "tooltip": {"trigger": "axis"},
        "series": [{
            "data": df_linha["qtd_respostas"].tolist(),
            "type": "line",
            "smooth": True
        }]
    }, height="400px")

# Pizza de respostas
def grafico_pizza_respostas(df):
    st.subheader("🥧 Distribuição Geral de Respostas")
    cores = {
        "Concordo totalmente":  "#416cbd",
        "Concordo": "#3ddf3d",
        "Neutro": "#cccaca",
        "Discordo": "#ffbf00",
        "Discordo totalmente": "#d62728"
    }
    dados = df.groupby("Resposta")["qtd_respostas"].sum().reset_index()
    series = [{
        "value": int(row["qtd_respostas"]),
        "name": row["Resposta"],
        "itemStyle": {"color": cores.get(row["Resposta"], "#cccccc")}
    } for _, row in dados.iterrows()]

    st_echarts({
        "tooltip": {"trigger": "item", "formatter": "{b}: {c} ({d}%)"},
        "series": [{
            "type": "pie",
            "radius": ["40%", "70%"],
            "data": series
        }]
    }, height="400px")

# Pizza por curso
def grafico_pizza_curso(df):
    st.subheader("🎓 Distribuição por Curso")
    dados = df.groupby("Curso")["qtd_respostas"].sum().reset_index()
    series = [{
        "value": int(row["qtd_respostas"]),
        "name": row["Curso"]
    } for _, row in dados.iterrows()]

    st_echarts({
        "tooltip": {"trigger": "item", "formatter": "{b}: {c} ({d}%)"},
        "legend": {"top": "bottom"},
        "series": [{
            "type": "pie",
            "radius": "55%",
            "data": series
        }]
    }, height="400px")

# Exportar tabela
def exportar_tabela(df, nome_arquivo):
    with st.expander("📄 Ver dados em tabela"):
        st.dataframe(df)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Baixar CSV", csv, file_name=nome_arquivo, mime="text/csv")
        
def grafico_nuvem_palavras_abertas(df_abertas):
    if df_abertas.empty or "Resposta" not in df_abertas.columns:
        st.info("Nenhuma resposta aberta disponível para nuvem de palavras.")
        return

    textos = df_abertas["Resposta"].dropna().astype(str).tolist()
    expressoes_compostas = {
        "muito bom", "não gostei", "ótimo professor", "aulas dinâmicas",
        "explica bem", "fala rápido", "sem paciência"
    }

    textos_processados = []
    for texto in textos:
        texto_lower = texto.lower()
        for expr in expressoes_compostas:
            if expr in texto_lower:
                texto_lower = texto_lower.replace(expr, expr.replace(" ", "_"))
        textos_processados.append(texto_lower)

    palavras = " ".join(textos_processados).split()
    stopwords = {
        "que", "não", "sim", "bom", "muito", "legal", "ok", "tudo", "bem", "acho",
        "tipo", "uma", "está", "como", "vai", "tem", "com", "pra", "mais", "pouco",
        "para", "de", "da", "do", "nos", "nas", "por", "ser"
    }
    contagem = Counter([p for p in palavras if len(p) > 3 and p not in stopwords])
    palavras_filtradas = [{"name": palavra.replace("_", " "), "value": qtd}
                          for palavra, qtd in contagem.items() if qtd > 1]

    if palavras_filtradas:
        st.subheader("☁️ Nuvem de Palavras - Respostas Abertas")
        st_echarts({
            "tooltip": {},
            "series": [{
                "type": "wordCloud",
                "gridSize": 8,
                "sizeRange": [14, 60],
                "rotationRange": [-90, 90],
                "shape": "circle",
                "width": "100%",
                "height": "100%",
                "drawOutOfBound": True,
                "textStyle": {
                    "normal": {
                        "color": {"type": "random"}
                    }
                },
                "data": palavras_filtradas
            }]
        }, height="500px")
    else:
        st.info("Nenhuma palavra relevante para exibir na nuvem.")


def grafico_sentimento_respostas_abertas(df_abertas):
    if df_abertas.empty or "Sentimento" not in df_abertas.columns:
        return None

    st.subheader("📊 Sentimento das Respostas Abertas por Professor")
    df_sentimento = df_abertas.copy()

    df_group = df_sentimento.groupby(["Professor", "Sentimento"])["qtd_respostas"].sum().reset_index()
    professores = sorted(df_group["Professor"].unique())
    sentimentos = ["positivo", "negativo", "neutro", "irônico"]

    cores_sentimento = {
        "positivo": "#4CAF50",
        "negativo": "#F44336",
        "neutro": "#9E9E9E",
        "irônico": "#FFEB3B"
    }

    series = []
    for sentimento in sentimentos:
        dados = []
        for prof in professores:
            total = df_group[
                (df_group["Professor"] == prof) &
                (df_group["Sentimento"] == sentimento)
            ]["qtd_respostas"].sum()
            dados.append(int(total) if not pd.isna(total) else 0)

        series.append({
            "name": sentimento.capitalize(),
            "type": "bar",
            "itemStyle": {"color": cores_sentimento.get(sentimento)},
            "emphasis": {"focus": "series"},
            "data": dados
        })

    st_echarts({
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "legend": {"orient": "vertical", "right": 10, "top": "middle"},
        "grid": {"left": 80, "right": 100, "bottom": 60, "containLabel": True},
        "xAxis": {"type": "category", "data": professores, "axisLabel": {"rotate": 15}},
        "yAxis": {"type": "value"},
        "series": series
    }, height="500px")

    return df_group


def exportar_tabela_sentimento(df_sentimento):
    with st.expander("📄 Ver dados Sentimento em tabela"):
        st.dataframe(df_sentimento)
        csv = df_sentimento.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Baixar CSV", csv, file_name="resumo_dashboard_resp_abertas.csv", mime="text/csv")


# Função principal
def main():
    autenticar_usuario()
    montar_sidebar()
    st.title("📊 Dashboard de Avaliações")
    verificar_respostas_abertas()

    df = carregar_dados_fechados()
    df_filtrado = aplicar_filtros(df)

    if df_filtrado.empty:
        st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados.")
        return

    mostrar_kpis(df_filtrado)
    grafico_barras_professor(df_filtrado)
    grafico_linha_periodo(df_filtrado)
    grafico_pizza_respostas(df_filtrado)
    grafico_pizza_curso(df_filtrado)
    exportar_tabela(df_filtrado, "resumo_dashboard_resp_fechadas.csv")
    
    # --- Respostas Abertas ---
    try:
        response = requests.get(API_URL_ABERTAS)
        if response.status_code == 200:
            df_abertas = pd.DataFrame(response.json())
            grafico_nuvem_palavras_abertas(df_abertas)
            grafico_sentimento_respostas_abertas(df_abertas)
            if df_abertas is not None:
                exportar_tabela_sentimento(df_abertas)
    except Exception as e:
        st.error(f"Erro ao carregar respostas abertas: {str(e)}")
    
    load_footer()

# Executa a main
if __name__ == "__main__" or st._is_running_with_streamlit:
    main()
