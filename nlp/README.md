## 🧠 Análise de Sentimento com Hugging Face Transformers
# 💬 Sistema de Análise de Conteúdo Aberto - SADo

Este projeto tem como objetivo analisar automaticamente respostas textuais abertas de formulários, detectando **ofensas**, **críticas construtivas**, **elogios**, **neutralidade** e **ironia**. Utilizamos **Machine Learning**, **modelos LLM**, e **estrutura modular em Python**, com armazenamento no **SQL Server**.

---

## 📂 Estrutura do Projeto
nlp/
├── config/
│ ├── connection.py # Conexão com banco SQL Server
│ └── db_config_ml.py # Configurações do banco para ML
│
├── ml/
│ ├── database/
│ │ └── datasets/ # Bases externas e CSVs para treino
│ ├── interface/ # CLI para consultar resultados
│ ├── learning/ # Treinamento dos modelos
│ ├── modelos/ # Modelos salvos (.pkl)
│ ├── preprocessing/ # Pré-processamento e testes
│ └── validadores/ # Funções de análise (ML e LLM)
│
└── README.md

---

## 🧠 Modelos Treinados

### 🔸 Modelo de Ofensividade
- **Objetivo**: Detectar linguagem ofensiva/toxidade.
- **Técnica**: Vetorização + `RandomForestClassifier`
- **Dataset**: 161.623 exemplos reais classificados manualmente.
- **Resultados**:
  - Accuracy: 1.00
  - Precision e Recall para True/False: 1.00
  - F1-score: 1.00

### 🔹 Modelo de Sentimento Crítico
- **Objetivo**: Identificar se a resposta é crítica, elogiosa, irônica ou neutra.
- **Técnica**: Vetorização + `RandomForestClassifier`
- **Classes**: `negativo`, `positivo`, `neutro`, `irônico`
- **Dataset**: 161.608 exemplos
- **Resultados**:
  - Accuracy: 0.97
  - Macro avg F1-score: 0.97

---

## 🤖 Lógica Híbrida (ML + LLM)

O arquivo `analise_texto_hibrido.py` combina:
- Resultados dos **modelos treinados (offline)** para escalabilidade
- Resultados de **modelos LLM externos (API IA)** para casos ambíguos (com score entre 0.4 e 0.8)

---

## 🔎 Testes Locais

Para testar o sistema localmente:

1. Execute os modelos de treino (caso necessário):
   ```bash
   python ml/learning/treinar_ofensivo.py
   python ml/learning/treinar_analise.py

2. Faça um teste manual de avaliação:
  ```bash
  python ml/preprocessing/teste_analise_texto.py

## 🗃️ Banco de Dados
- Utilizamos SQL Server com uma tabela central chamada Treinamento_Manual para alimentar os modelos.

- Outras tabelas de apoio:
  - Frases_Suspeitas
  - Frases_Analisadas

## 🔗 Modelos Utilizados
- ✅ Modelos personalizados via RandomForestClassifier

- 🔄 LLMs integradas via API externa gratuita (com fallback)
  - Modelos base: cardiffnlp/twitter-roberta-base-sentiment, Bertimbau toxicidade
  - API: openai/gpt-3.5-turbo

## ⚠️ Importante
- O uso de LLMs foi limitado após testes devido ao custo elevado e políticas de filtro de conteúdo ofensivo.

- O sistema segue operando com detecção 100% local, e a LLM só atua via analise_texto_llm.py ou analise_texto_hibrido.py.

## 📈 Exemplos de Resultados
- Resultado do modelo ofensivo:
| Classe   | Precision | Recall | F1-score | Support |
| -------- | --------- | ------ | -------- | ------- |
| False    | 1.00      | 1.00   | 1.00     | 75.300  |
| True     | 1.00      | 1.00   | 1.00     | 86.323  |
| Accuracy |           |        | 1.00     | 161.623 |

- Resultado do modelo de sentimento:
| Classe   | Precision | Recall | F1-score | Support |
| -------- | --------- | ------ | -------- | ------- |
| Irônico  | 0.98      | 0.99   | 0.99     | 4.488   |
| Negativo | 1.00      | 0.94   | 0.97     | 92.403  |
| Neutro   | 0.99      | 0.99   | 0.99     | 4.553   |
| Positivo | 0.92      | 1.00   | 0.96     | 60.164  |
| Accuracy |           |        | 0.97     | 161.608 |

## 👨‍💻 Autor
Desenvolvido por MárcioJr Almeida no contexto de processamento de linguagem natural (NLP) voltado para educação e análise de formulários acadêmicos.

## 📌 Licença
Este projeto é livre para fins acadêmicos e educativos.