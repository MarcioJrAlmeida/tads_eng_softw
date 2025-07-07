import streamlit as st
import requests
from datetime import datetime
from datetime import date
import csv
import os
from app.components.auth import load_auth_config, create_authenticator
from app.components.utils import realizar_logout, load_css, load_footer, load_js

st.set_page_config(
    page_title="Formulário", 
    page_icon="", 
    layout="centered"
)

# Configuração e autenticação
config = load_auth_config()
authenticator = create_authenticator(config)

# Estado inicial
if "modo_edicao" not in st.session_state:
    st.session_state["modo_edicao"] = False
if "nova_pergunta_texto" not in st.session_state:
    st.session_state["nova_pergunta_texto"] = ""
if "nova_pergunta_tipo" not in st.session_state:
    st.session_state["nova_pergunta_tipo"] = "Fechada"
if "avaliacao_selecionada" not in st.session_state:
    st.session_state["avaliacao_selecionada"] = None
if "mostrar_formulario" not in st.session_state:
    st.session_state["mostrar_formulario"] = False
if "secao_edicao" not in st.session_state:
    st.session_state["secao_edicao"] = ""

if st.session_state.get("authentication_status") is not True:
    st.warning("Você precisa estar logado para acessar esta página.")
    st.switch_page("login.py")

load_css("style.css")
load_js("index.js")

# Sidebar
if st.sidebar.button("Home"):
    st.switch_page("pages/home.py")
if st.sidebar.button("Formulários"):
    st.switch_page("pages/edicao_forms.py")
if st.sidebar.button("Dashboard"):
    st.switch_page("pages/dashboard_diretor.py")
if st.sidebar.button("Logout"):
    realizar_logout()

# Conteúdo principal
st.title("🛠️ Formulários de Avaliação")

API_URL = "http://localhost:5001/api/perguntas"
RESPOSTA_API_URL = "http://localhost:5001/api/respostas"
AVALIACOES_API_URL = "http://localhost:5001/api/avaliacoes"

def carregar_avaliacoes():
    try:
        response = requests.get(AVALIACOES_API_URL)
        if response.status_code == 200:
            return response.json()
        else:
            st.warning("Erro ao carregar avaliações disponíveis.")
            return []
    except Exception as e:
        st.error(f"Erro ao carregar avaliações: {str(e)}")
        return []


def carregar_modelo_avaliacao(id_avaliacao: int):
    try:
        response = requests.get(f"http://localhost:5001/api/modelo_avaliacao/{id_avaliacao}")
        if response.status_code == 200:
            return response.json()
        else:
            return {}
    except Exception as e:
        st.error(f"Erro ao buscar modelo de avaliação: {str(e)}")
        return {}

def selecionar_avaliacao():
    avaliacoes = carregar_avaliacoes()
    if not avaliacoes:
        st.warning("Nenhuma avaliação encontrada.")
        return False

    opcoes = {f"ID {av['id_avaliacao']} - Período {av['periodo']}": av for av in avaliacoes}
    opcoes_labels = ["Selecione a Avaliação..."] + list(opcoes.keys())

    escolha = st.selectbox("🔍 Selecione a avaliação para editar:", opcoes_labels, key="seletor_avaliacao")

    if escolha != "Selecione a Avaliação...":
        st.session_state["avaliacao_selecionada"] = opcoes[escolha]["id_avaliacao"]
        st.session_state["avaliacao_info"] = opcoes[escolha]
        st.rerun()

    return False

def exibir_formulario_avaliacao(perguntas, perfil):
    st.subheader("Formulário de Avaliação Docente")
    respostas = []

    if 'ordem_perguntas' in st.session_state:
        perguntas_ordenadas = [p for id_ in st.session_state['ordem_perguntas'] for p in perguntas if p['id_pergunta'] == id_]
    else:
        perguntas_ordenadas = sorted(perguntas, key=lambda x: x['id_pergunta'])

    qtd_exibir = st.session_state.get('qtd_perguntas_exibir', len(perguntas_ordenadas))
    perguntas_exibidas = perguntas_ordenadas[:qtd_exibir]

    alternativas_fechadas_padrao = [
        "Selecione...",
        "Discordo totalmente",
        "Discordo",
        "Neutro",
        "Concordo",
        "Concordo totalmente"
    ]

    for pergunta in perguntas_exibidas:
        if pergunta['tipo_pergunta'].lower() == "fechada":
            resposta = st.radio(pergunta['texto_pergunta'], alternativas_fechadas_padrao, key=f"resposta_{pergunta['id_pergunta']}")
        else:
            resposta = st.text_area(pergunta['texto_pergunta'], key=f"resposta_{pergunta['id_pergunta']}")

        respostas.append({"id_pergunta": pergunta['id_pergunta'], "resposta": resposta})

    if perfil != "Diretor":
        if st.button("Enviar respostas"):
            for r in respostas:
                if r["resposta"] == "Selecione...":
                    st.warning("Por favor, selecione uma resposta para todas as perguntas fechadas.")
                    return

            payload = {
                "respostas": respostas,
                "data_hr_registro": datetime.now().isoformat()
            }
            response = requests.post(RESPOSTA_API_URL, json=payload)
            if response.status_code == 201:
                st.success("Respostas enviadas com sucesso!")
            else:
                st.error("Erro ao enviar respostas.")
    else:
        st.info("🔒 Como Diretor, você não pode enviar respostas.")
        
def carregar_perguntas():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            return response.json()
        else:
            st.error("Erro ao carregar perguntas.")
            return []
    except Exception as e:
        st.error(f"Erro: {str(e)}")
        return []

def cadastrar_nova_pergunta():
    texto_input = st.text_input("Texto da nova pergunta", key="nova_pergunta_texto")
    tipo_input = st.selectbox("Tipo de pergunta", ["Fechada", "Aberta"], key="nova_pergunta_tipo")

    if st.button("Cadastrar pergunta"):
        payload = [{
            "texto_pergunta": texto_input,
            "tipo_pergunta": tipo_input
        }]
        response = requests.post(API_URL, json=payload)
        if response.status_code == 201:
            st.success("Pergunta cadastrada com sucesso!")
            st.rerun()
        else:
            st.error("Erro ao cadastrar pergunta.")

def editar_perguntas_existentes():
    perguntas = carregar_perguntas()
    for pergunta in perguntas:
        col1, col2 = st.columns([5, 1])
        with col1:
            with st.expander(f"✏️ Editar: {pergunta['texto_pergunta']}"):
                novo_texto = st.text_input("Novo texto", value=pergunta['texto_pergunta'], key=f"texto_{pergunta['id_pergunta']}")
                novo_tipo = st.selectbox(
                    "Novo tipo", 
                    ["Fechada", "Aberta"], 
                    index=0 if pergunta['tipo_pergunta'] == "Fechada" else 1, 
                    key=f"tipo_{pergunta['id_pergunta']}"
                )
                if st.button("💾 Salvar", key=f"salvar_{pergunta['id_pergunta']}"):
                    payload = {
                        "texto_pergunta": novo_texto,
                        "tipo_pergunta": novo_tipo
                    }
                    url = f"{API_URL}/{pergunta['id_pergunta']}"
                    response = requests.put(url, json=payload)
                    if response.status_code == 200:
                        st.success("Pergunta atualizada!")
                    else:
                        st.error("Erro ao atualizar pergunta.")
        with col2:
            excluir = st.button("🗑️ Excluir", key=f"excluir_{pergunta['id_pergunta']}")
            if excluir:
                st.session_state[f"confirmar_excluir_{pergunta['id_pergunta']}"] = True

        if st.session_state.get(f"confirmar_excluir_{pergunta['id_pergunta']}", False):
            st.warning(f"⚠️ Deseja excluir permanentemente a pergunta: {pergunta['texto_pergunta']}?")
            confirmar = st.button("✅ Confirmar Exclusão", key=f"confirmar_botao_{pergunta['id_pergunta']}")
            cancelar = st.button("❌ Cancelar", key=f"cancelar_botao_{pergunta['id_pergunta']}")
            if confirmar:
                try:
                    url = f"{API_URL}/{pergunta['id_pergunta']}"
                    response = requests.delete(url)
                    if response.status_code == 200:
                        st.success("Pergunta excluída com sucesso!")
                        st.session_state.pop(f"confirmar_excluir_{pergunta['id_pergunta']}", None)
                        st.rerun()
                    else:
                        st.error("Erro ao excluir pergunta.")
                except Exception as e:
                    st.error(f"Erro: {str(e)}")
            elif cancelar:
                st.session_state.pop(f"confirmar_excluir_{pergunta['id_pergunta']}", None)

            
def menu_edicao():
    st.markdown("### ⚙️ Menu de Edição Rápida")

    col_voltar, col_botao1, col_botao2 = st.columns([1, 1, 1])

    with col_voltar:
        if st.button("🔙 Voltar"):
            st.session_state["modo_edicao"] = False
            st.rerun()

    with col_botao1:
        if st.button("🆕 Nova Pergunta"):
            st.session_state["secao_edicao"] = "Cadastrar Nova Pergunta"

    with col_botao2:
        if st.button("✏️ Editar Perguntas"):
            st.session_state["secao_edicao"] = "Editar Perguntas Existentes"
            
def criar_nova_avaliacao():
    st.subheader("🆕 Criar Nova Avaliação")

    periodo = st.text_input("📅 Período da Avaliação (ex: 202502)", key="novo_periodo")

    perguntas = carregar_perguntas()
    perguntas_selecionadas = []

    st.markdown("### ✅ Selecione as perguntas para a nova avaliação")

    for pergunta in perguntas:
        col1, col2, col3 = st.columns([0.6, 0.2, 0.2])
        with col1:
            texto_curto = pergunta['texto_pergunta'][:80] + ("..." if len(pergunta['texto_pergunta']) > 80 else "")
            label = f"{texto_curto} ({pergunta['tipo_pergunta'].capitalize()})"
            selecionada = st.checkbox(label, key=f"check_criar_{pergunta['id_pergunta']}")
        with col2:
            ordem = st.number_input(
                "Ordem", 
                min_value=1, 
                max_value=100, 
                step=1, 
                key=f"ordem_criar_{pergunta['id_pergunta']}"
            ) if selecionada else None

        if selecionada:
            perguntas_selecionadas.append({
                "id_pergunta": pergunta["id_pergunta"],
                "ordem": ordem
            })

    if st.button("✅ Criar Avaliação"):
        if not periodo.strip():
            st.warning("⚠️ O período é obrigatório.")
            return

        if not perguntas_selecionadas:
            st.warning("⚠️ Selecione pelo menos uma pergunta.")
            return

        modelo = {
            "ordem_perguntas": [p["id_pergunta"] for p in sorted(perguntas_selecionadas, key=lambda x: x["ordem"])],
            "qtd_perguntas_exibir": len(perguntas_selecionadas)
        }

        payload = {
            "periodo": int(periodo),
            "idDiretor": 1,
            "modelo_avaliacao": modelo
        }

        try:
            response = requests.post("http://localhost:5001/api/avaliacoes", json=payload)
            if response.status_code == 201:
                st.success("✅ Avaliação criada com sucesso!")
                st.session_state["criando_avaliacao"] = False
                st.rerun()
            else:
                st.error(f"Erro ao criar avaliação: {response.text}")
        except Exception as e:
            st.error(f"Erro de conexão: {str(e)}")



def main():
    if "modo_edicao" not in st.session_state:
        st.session_state["modo_edicao"] = False
    if "secao_edicao" not in st.session_state:
        st.session_state["secao_edicao"] = ""
    if "criando_avaliacao" not in st.session_state:
        st.session_state["criando_avaliacao"] = False

    if not st.session_state.get("avaliacao_selecionada"):
        col1, col2 = st.columns([3, 1])
        with col1:
            sucesso = selecionar_avaliacao()
        with col2:
            if st.button("🆕 Nova Avaliação"):
                st.session_state["criando_avaliacao"] = True
                st.rerun()

        if st.session_state.get("criando_avaliacao"):
            criar_nova_avaliacao()
            return

    else:
        col1, col2 = st.columns([6, 1])
        with col1:
            st.markdown(f"### ✏️ Avaliação Selecionada: {st.session_state['avaliacao_selecionada']}")
            av_info = st.session_state.get("avaliacao_info", {})
            if av_info:
                st.markdown(f"""
                > 📝 **ID**: {av_info.get('id_avaliacao')}  
                > 📅 **Período**: {av_info.get('periodo')}  
                > 🕒 **Data de Registro**: {av_info.get('data_hr_registro')}
                """)

            if not st.session_state["modo_edicao"]:
                if st.button("✏️ Entrar em Modo de Edição", key="botao_entrar_edicao"):
                    st.session_state["modo_edicao"] = True
                    st.rerun()
            else:
                if st.button("❌ Sair do Modo de Edição", key="botao_sair_edicao"):
                    st.session_state["modo_edicao"] = False
                    st.rerun()

            if st.session_state["modo_edicao"]:
                st.checkbox("👁️ Mostrar formulário de perguntas", key="mostrar_formulario")

        with col2:
            if st.button("🔁 Trocar"):
                st.session_state["avaliacao_selecionada"] = None
                st.session_state["avaliacao_info"] = None
                st.rerun()

    perguntas = carregar_perguntas()
    id_avaliacao = st.session_state.get("avaliacao_selecionada", 1)
    modelo = carregar_modelo_avaliacao(id_avaliacao)

    if modelo:
        st.session_state['ordem_perguntas'] = modelo.get("ordem_perguntas", [])
        st.session_state['qtd_perguntas_exibir'] = modelo.get("qtd_perguntas_exibir", len(perguntas))
    else:
        st.session_state['ordem_perguntas'] = [p['id_pergunta'] for p in perguntas]
        st.session_state['qtd_perguntas_exibir'] = len(perguntas)

    if st.session_state["mostrar_formulario"]:
        exibir_formulario_avaliacao(perguntas, perfil="Diretor")

    if st.session_state["modo_edicao"]:
        st.markdown("---")
        menu_edicao()

        if st.session_state["secao_edicao"] == "Cadastrar Nova Pergunta":
            cadastrar_nova_pergunta()
        elif st.session_state["secao_edicao"] == "Editar Perguntas Existentes":
            editar_perguntas_existentes()
    

if __name__ == "__main__":
    main()
    load_footer()