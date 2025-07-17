# tads_eng_softw

## 🛠 Projeto de Engenharia de Software

Este repositório faz parte do desenvolvimento de um sistema no contexto da disciplina de Engenharia de Software. Nosso objetivo é organizar e documentar todas as fases do projeto de forma modular, facilitando a colaboração e o versionamento entre os membros da equipe.

---

## 📁 Estrutura Inicial

O repositório está organizado por áreas de responsabilidade, com a seguinte estrutura de diretórios:

- `/front` – Contém todo o código relacionado à interface do usuário (Frontend).
- `/back` – Responsável pela lógica de negócio e API do sistema (Backend).
- `/documents` – Pasta com documentos de apresentação, cronograma e outros arquivos importantes.
- `/banco` – Scripts e modelagem do banco de dados relacional ou não relacional.
- `/nlp/ml/preprocessing` – Scripts de processamento de linguagem natural (NLP) e modelos de machine learning.
- Outras pastas podem ser criadas conforme o crescimento do projeto: `/docs`, `/tests`, `/infra`, etc.

---

## 🧪 Modo de Desenvolvimento CSV

Durante o desenvolvimento, o sistema pode operar em dois modos:

- **Modo Banco de Dados**: Utiliza um banco SQL Server para persistência dos dados.
- **Modo CSV**: Utiliza arquivos `.csv` para simular o banco de dados, permitindo testes e desenvolvimento local sem necessidade de um banco configurado.

Esse modo é útil para testes rápidos e protótipos, sem necessidade de dependências externas. Para ativar esse modo, altere a variável `MODO_DESENVOLVIMENTO = "CSV"` no arquivo de configuração "back/config/db_config.py".

---

## ⚙️ Pré-requisitos

Antes de executar o projeto, certifique-se de ter instalado:

- Python 3.10+
- Pip
- Git
- (Opcional) SQL Server se for utilizar modo banco de dados

Instale todas as bibliotecas com:

```bash
pip install -r requirements.txt
```

---

## 🚀 Execução do Projeto

### Backend + Frontend

Execute o backend e o frontend com os comandos abaixo:

```bash
cd front
python backend_app.py
```

Em outro terminal:

```bash
cd front
python run_app.py
```

Acesse `http://localhost:8501` no navegador para ver a aplicação.

Login: diretor

Password: diretor123

---

## 🤖 Executar módulo de NLP/LLM

Para testar o sistema de análise de sentimento e ofensas, execute:

```bash
cd nlp/ml/preprocessing
python teste_analise_texto.py
```

Esse script utiliza modelos de linguagem (LLM) para classificar textos com base em sentimento e conteúdo ofensivo.

---

## ✅ Objetivos do Projeto

- Aplicar os conceitos teóricos de Engenharia de Software na prática.
- Trabalhar com versionamento, modularização e integração contínua.
- Explorar técnicas modernas de desenvolvimento como análise de sentimento, API REST, interface com Streamlit e persistência em SQL Server ou arquivos CSV.

---

## 📌 Observação

Este projeto está em constante evolução. Colabore com sugestões, issues e pull requests!