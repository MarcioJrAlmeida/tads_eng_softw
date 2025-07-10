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

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <h3 style="text-align: center; color: #FFFFFF;">
        Sistema de Avaliação Docente - IFPE Jaboatão
    </h3>
    """,
    unsafe_allow_html=True
)

# Conteúdo principal
st.title("🛠️ Formulários de Avaliação")

API_URL = "http://localhost:5001/api/perguntas"
AVALIACOES_API_URL = "http://localhost:5001/api/avaliacoes"

@st.cache_data(ttl=60)
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


@st.cache_data(ttl=60)
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
    st.subheader("📋 Formulário de Avaliação Docente")
    respostas = []

    opcoes = {
        1: "Discordo totalmente",
        2: "Discordo",
        3: "Neutro",
        4: "Concordo",
        5: "Concordo totalmente"
    }

    if 'ordem_perguntas' in st.session_state:
        perguntas_ordenadas = [p for id_ in st.session_state['ordem_perguntas'] for p in perguntas if p['id_pergunta'] == id_]
    else:
        perguntas_ordenadas = sorted(perguntas, key=lambda x: x['id_pergunta'])

    qtd_exibir = st.session_state.get('qtd_perguntas_exibir', len(perguntas_ordenadas))
    perguntas_exibidas = perguntas_ordenadas[:qtd_exibir]

    for pergunta in perguntas_exibidas:
        texto_curto = pergunta['texto_pergunta'][:80] + ("..." if len(pergunta['texto_pergunta']) > 80 else "")
        if pergunta['tipo_pergunta'].lower() == "fechada":
            resposta = st.radio(
                texto_curto,
                opcoes,
                key=f"resposta_{pergunta['id_pergunta']}",
                horizontal=True
            )
        else:
            resposta = st.text_area(pergunta['texto_pergunta'], key=f"resposta_{pergunta['id_pergunta']}")


        respostas.append({
            "id_pergunta": pergunta['id_pergunta'],
            "resposta": opcoes[resposta] if pergunta['tipo_pergunta'].lower() == "fechada" else resposta
        })

    if perfil != "Diretor":
        if st.button("📨 Enviar respostas"):
            for r in respostas:
                if not r["resposta"] or r["resposta"] == "Selecione...":
                    st.warning("⚠️ Por favor, responda todas as perguntas.")
                    return

            payload = {
                "respostas": respostas,
                "data_hr_registro": datetime.now().isoformat()
            }

            st.write("Payload enviado:", payload)  # DEBUG

            try:
                response = requests.post("http://localhost:5001/api/respostas", json=payload)
                if response.status_code == 201:
                    st.success("✅ Respostas enviadas com sucesso!")
                else:
                    st.error(f"Erro ao enviar respostas. Status: {response.status_code}, Msg: {response.text}")
            except Exception as e:
                st.error(f"Erro ao enviar respostas: {e}")
    else:
        st.info("🔒 Como Diretor, você não pode enviar respostas.")
        
@st.cache_data(ttl=60)
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
                    elif response.status_code == 403:
                        st.warning("❌ Esta pergunta não pode ser excluída porque possui respostas associadas.")
                    else:
                        st.error("Erro ao excluir pergunta.")
                except Exception as e:
                    st.error(f"Erro: {str(e)}")
            elif cancelar:
                st.session_state.pop(f"confirmar_excluir_{pergunta['id_pergunta']}", None)

# Adicionar no topo, após as variáveis iniciais:
if "criando_avaliacao" not in st.session_state:
    st.session_state["criando_avaliacao"] = False

# Atualize a função selecao_perguntas com lógica condicional:
def selecao_perguntas():
    perguntas = carregar_perguntas()
    modelo = {}
    perguntas_modelo = []
    id_avaliacao = st.session_state.get("avaliacao_selecionada")

    perguntas_selecionadas = []

    st.markdown("### ✅ Selecione as perguntas do formulário")
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

    if st.session_state.get("criando_avaliacao"):
        st.session_state["perguntas_nova_avaliacao"] = perguntas_selecionadas
        return  # Evita mostrar o botão de salvar modelo neste modo

    # Modo edição: botão de salvar e vincular
    if st.button("📅 Salvar Modelo e Vincular Perguntas"):
        if not perguntas_selecionadas:
            st.warning("⚠️ Selecione ao menos uma pergunta.")
            return

        perguntas_ordenadas = sorted(perguntas_selecionadas, key=lambda x: x["ordem"])
        ids_perguntas = [p["id_pergunta"] for p in perguntas_ordenadas]
        modelo = {
            "ordem_perguntas": ids_perguntas,
            "qtd_perguntas_exibir": len(ids_perguntas)
        }

        response_modelo = requests.put(
            f"http://localhost:5001/api/avaliacoes/{id_avaliacao}",
            json={"modelo_avaliacao": modelo}
        )

        response_contem = requests.post(
            f"http://localhost:5001/api/avaliacoes/{id_avaliacao}/vincular_perguntas",
            json={"id_perguntas": ids_perguntas}
        )

        if response_modelo.status_code == 200 and response_contem.status_code == 200:
            st.success("✅ Modelo salvo e perguntas vinculadas com sucesso!")
            st.rerun()
        else:
            st.error("❌ Erro ao salvar o modelo ou vincular perguntas.")


def criar_nova_avaliacao():
    st.subheader("🆕 Criar Nova Avaliação")

    periodo = st.text_input("📅 Período da Avaliação (ex: 202502)", key="novo_periodo")

    # Menu de edição rápida
    st.markdown("---")
    menu_edicao()

    # Seção de perguntas
    if st.session_state.get("secao_edicao") == "Selecionar Perguntas":
        selecao_perguntas()

    # Validação e criação
    if st.button("✅ Criar Avaliação"):
        if not periodo.strip():
            st.warning("⚠️ O período é obrigatório.")
            return

        perguntas_selecionadas = st.session_state.get("perguntas_nova_avaliacao", [])
        if not perguntas_selecionadas:
            st.warning("⚠️ Selecione pelo menos uma pergunta.")
            return

        # Modelo da avaliação
        perguntas_ordenadas = sorted(perguntas_selecionadas, key=lambda x: x["ordem"])
        ids_perguntas = [p["id_pergunta"] for p in perguntas_ordenadas]

        modelo = {
            "ordem_perguntas": ids_perguntas,
            "qtd_perguntas_exibir": len(ids_perguntas)
        }

        payload = {
            "periodo": int(periodo),
            "idDiretor": 1,
            "modelo_avaliacao": modelo,
            "data_lancamento": datetime.now().isoformat()  # Se der erro aqui, substitua por .isoformat()
        }

        try:
            response = requests.post("http://localhost:5001/api/avaliacoes", json=payload)

            if response.status_code == 201:
                nova_avaliacao = response.json()
                id_avaliacao = nova_avaliacao["id_avaliacao"]
                
                # 🔁 Vincular perguntas à avaliação após criar com sucesso
                ids_perguntas = [p["id_pergunta"] for p in sorted(perguntas_selecionadas, key=lambda x: x["ordem"])]
                
                response_vinculo = requests.post(
                    f"http://localhost:5001/api/avaliacoes/{id_avaliacao}/vincular_perguntas",
                    json={"id_perguntas": ids_perguntas}
                )

                if response_vinculo.status_code == 200:
                    st.success("✅ Avaliação criada e perguntas vinculadas com sucesso!")
                else:
                    st.warning("Avaliação criada, mas não foi possível vincular as perguntas.")
                    st.error(f"Detalhes: {response_vinculo.text}")

                st.session_state["criando_avaliacao"] = False
                st.rerun()

            else:
                st.error(f"Erro ao criar avaliação: {response.text}")

        except Exception as e:
            st.error(f"Erro de conexão: {str(e)}")


def menu_edicao():
    st.markdown("### ⚙️ Menu de Edição Rápida")

    col_voltar, col_botao1, col_botao2, col_botao3 = st.columns([1, 1, 1, 1])

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
            
    with col_botao3:
        if st.button("📌 Seleção Perguntas"):
            st.session_state["secao_edicao"] = "Selecionar Perguntas"
            
def criar_nova_avaliacao():
    st.subheader("🆕 Criar Nova Avaliação")

    periodo = st.text_input("📅 Período da Avaliação (ex: 202502)", key="novo_periodo")

    perguntas = carregar_perguntas()
    perguntas_selecionadas = st.session_state.get("perguntas_nova_avaliacao", [])


    # Novo: Menu de edição rápida durante a criação da avaliação
    st.markdown("---")
    menu_edicao()

    if st.session_state["secao_edicao"] == "Cadastrar Nova Pergunta":
        cadastrar_nova_pergunta()
    elif st.session_state["secao_edicao"] == "Editar Perguntas Existentes":
        editar_perguntas_existentes()
        
    if st.session_state.get("secao_edicao") == "Selecionar Perguntas":
        selecao_perguntas()

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
        
        dt_lancamento = datetime.now().isoformat()
        payload = {
            "periodo": int(periodo),
            "idDiretor": 1,
            "modelo_avaliacao": modelo,
            "data_lancamento": dt_lancamento
        }

        try:
            response = requests.post("http://localhost:5001/api/avaliacoes", json=payload)
            if response.status_code == 201:
                nova_avaliacao = response.json()
                id_avaliacao = nova_avaliacao.get("id_avaliacao")
        
                if not id_avaliacao:
                    st.error("❌ A API não retornou o ID da avaliação.")
                    return
            
                # Vincula as perguntas agora
                ids_perguntas = [p["id_pergunta"] for p in perguntas_selecionadas]
                response_vinculo = requests.post(
                    f"http://localhost:5001/api/avaliacoes/{id_avaliacao}/vincular_perguntas",
                    json={"id_perguntas": ids_perguntas}
                )
            
                if response_vinculo.status_code == 200:
                    st.success("✅ Avaliação criada e perguntas vinculadas com sucesso!")
                else:
                    st.warning("Avaliação criada, mas houve erro ao vincular perguntas.")
                    st.error(f"Detalhes: {response_vinculo.text}")
            
                st.session_state["criando_avaliacao"] = False
                st.rerun()
            
            else:
                st.error(f"Erro ao criar avaliação: {response.text}")
        except Exception as e:
            st.error(f"Erro de conexão: {str(e)}")


def main():
    # ... outras inicializações ...

    if not st.session_state.get("avaliacao_selecionada"):
        col1, col2 = st.columns([4, 1])  # Ajuste dos pesos para melhor espaçamento
        with col1:
            sucesso = selecionar_avaliacao()
        with col2:
            if st.button("🆕 Nova Avaliação", key="botao_nova_avaliacao"):
                st.session_state["criando_avaliacao"] = True

        if st.session_state.get("criando_avaliacao"):
            criar_nova_avaliacao()
            return

    # ... resto do código ...

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
        elif st.session_state["secao_edicao"] == "Selecionar Perguntas":
            selecao_perguntas()
            
        # Verifica se há uma avaliação ativa
    def buscar_avaliacao_ativa():
        try:
            response = requests.get("http://localhost:5001/api/avaliacoes")
            if response.status_code == 200:
                for a in response.json():
                    if a.get("status_avaliacao") == "Ativo":
                        return a
            return None
        except:
            return None

    avaliacao_ativa = buscar_avaliacao_ativa()

    if id_avaliacao:
        if avaliacao_ativa:
            if avaliacao_ativa["id_avaliacao"] == id_avaliacao:
                st.info("✅ Esta avaliação já está ativa.")
                if st.button("🛑 Desativar Avaliação"):
                    response = requests.put(
                        f"http://localhost:5001/api/avaliacoes/{id_avaliacao}/status",
                        json={"status_avaliacao": "Inativo"}
                    )
                    if response.status_code == 200:
                        st.success("Avaliação desativada com sucesso.")
                        st.rerun()
                    else:
                        st.error("Erro ao desativar a avaliação.")
            else:
                st.warning(f"⚠️ Já existe uma avaliação ativa: ID {avaliacao_ativa['id_avaliacao']} - Período {avaliacao_ativa['periodo']}.")
                st.info("Para ativar esta, desative a avaliação atual primeiro.")
        else:
            if st.button("🚀 Lançar Avaliação"):
                response = requests.put(
                    f"http://localhost:5001/api/avaliacoes/{id_avaliacao}/status",
                    json={"status_avaliacao": "Ativo"}
                )
                if response.status_code == 200:
                    st.success("✅ Avaliação lançada com sucesso!")
                    st.rerun()
                else:
                    st.error("Erro ao lançar a avaliação.")


if __name__ == "__main__":
    main()
    load_footer()
