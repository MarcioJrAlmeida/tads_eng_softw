import streamlit as st
import json

st.set_page_config(page_title="Avaliação de Docentes", layout="centered")

st.title("🎮 Avaliação de Docentes")

# Sessão para armazenar estado de login
if "diretor_logado" not in st.session_state:
    st.session_state.diretor_logado = False

# Área de login do diretor
with st.expander("🔐 Área do diretor (Editar Perguntas)"):
    senha = st.text_input("Senha do diretor:", type="password")
    if st.button("Entrar"):
        if senha == "admin123":  # Troque por senha segura
            st.session_state.diretor_logado = True
            st.success("Acesso concedido!")
        else:
            st.error("Senha incorreta.")

# Perguntas e pesos padrão
perguntas_fechadas_default = [
    ("O professor demonstra domínio profundo sobre os temas abordados?", 10),
    ("As aulas seguem um plano coerente com os objetivos da disciplina?", 7),
    ("O professor relaciona o conteúdo com situações práticas ou atuais?", 8),
    ("Utiliza métodos variados para facilitar o aprendizado?", 7),
    ("O conteúdo é apresentado de forma clara e organizada?", 8),
    ("As explicações ajudam a esclarecer dúvidas e conceitos difíceis?", 7),
    ("Comunica-se com clareza (oral e escrita)?", 7),
    ("Estimula a participação e o diálogo durante as aulas?", 8),
    ("Responde às dúvidas com atenção e paciência?", 6),
    ("Os critérios de avaliação são claros desde o início da disciplina?", 6),
    ("As correções são feitas dentro de prazos razoáveis?", 6),
    ("Oferece feedback construtivo que contribui para o aprendizado?", 6),
    ("Trata todos os alunos com respeito e imparcialidade?", 6),
    ("Mantém comportamento ético e profissional?", 6),
    ("Está disponível para apoiar os alunos fora do horário de aula?", 6),
]
perguntas_abertas_default = [
    "O que poderia ser melhorado na prática do docente?"
]

# Permite ao diretor editar perguntas
if st.session_state.diretor_logado:
    st.markdown("## ✏️ Editar Perguntas de Avaliação")
    perguntas_editadas = []
    for i, (texto, peso) in enumerate(perguntas_fechadas_default):
        nova_pergunta = st.text_input(f"Pergunta fechada {i+1}", value=texto, key=f"edit_pergunta_{i}")
        novo_peso = st.number_input(f"Peso da pergunta {i+1}", value=peso, min_value=1, max_value=20, key=f"edit_peso_{i}")
        perguntas_editadas.append((nova_pergunta, novo_peso))

    perguntas_abertas_editadas = []
    for i, pergunta in enumerate(perguntas_abertas_default):
        nova = st.text_input(f"Pergunta aberta {i+1}", value=pergunta, key=f"edit_aberta_{i}")
        perguntas_abertas_editadas.append(nova)

    if st.button("Salvar Perguntas"):
        st.session_state.perguntas_fechadas_salvas = perguntas_editadas
        st.session_state.perguntas_abertas_salvas = perguntas_abertas_editadas
        st.success("Perguntas atualizadas com sucesso!")

# Usa perguntas atualizadas se existirem
perguntas_fechadas = st.session_state.get("perguntas_fechadas_salvas", perguntas_fechadas_default)
perguntas_abertas = st.session_state.get("perguntas_abertas_salvas", perguntas_abertas_default)

# Informações iniciais
professor = st.selectbox("Professor avaliado:", ["--Selecione--","Brunno", "Viviane", "Diego", "Geraldo", "Juarez", "Josino", "Emanuel"])

opcoes = ["", "Nunca", "Às vezes", "Frequentemente", "Sempre"]
pontuacoes = {"Nunca": 0.0, "Às vezes": 0.5, "Frequentemente": 0.75, "Sempre": 1.0}

# Coleta de respostas fechadas
st.markdown("## ✍️ Responda às perguntas fechadas:")
respostas = []
for i, (pergunta, _) in enumerate(perguntas_fechadas):
    resposta = st.selectbox(pergunta, opcoes, key=f"q{i}")
    respostas.append(resposta)

# Coleta de respostas abertas
st.markdown("## 📝 Perguntas Abertas")
respostas_abertas = []
for i, pergunta in enumerate(perguntas_abertas):
    resposta_aberta = st.text_area(pergunta, key=f"aberta_{i}")
    respostas_abertas.append(resposta_aberta)

# Botão para enviar avaliação
enviar = st.button("📤 Enviar Avaliação")

if enviar:
    # Valida se todas perguntas fechadas foram respondidas
    if all(resp in pontuacoes and resp != "" for resp in respostas):
        pontuacao_total = 0
        for i, resposta in enumerate(respostas):
            peso = perguntas_fechadas[i][1]
            pontuacao_total += peso * pontuacoes[resposta]

        st.markdown("---")
        st.success(f"🎯 Pontuação final: {int(pontuacao_total)} pontos")

        if pontuacao_total >= 95:
            st.balloons()
            st.markdown("🏆 **Badge desbloqueada: Mestre Inspirador!**")
        elif pontuacao_total >= 75:
            st.markdown("🎖️ **Badge: Professor Excelente**")
        elif pontuacao_total >= 50:
            st.markdown("📘 **Badge: Em Desenvolvimento**")
        else:
            st.markdown("🔍 **Badge: Avaliação Necessária**")
    else:
        st.error("❗ Por favor, responda todas as perguntas fechadas antes de enviar.")
else:
    st.info("➡️ Após responder todas as perguntas, clique em 'Enviar Avaliação' para ver o resultado.")
