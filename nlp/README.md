## 🧠 Análise de Sentimento com Hugging Face Transformers
Este projeto implementa uma análise de sentimento multilíngue utilizando a biblioteca 🤗 Transformers da Hugging Face, com foco especial em textos em português. O modelo utilizado é o nlptown/bert-base-multilingual-uncased-sentiment, treinado para classificar sentenças em uma escala de 1 a 5 estrelas, onde:

⭐️ 1-2 estrelas representam sentimentos negativos

⭐️ 3 estrelas representam sentimento neutro

⭐️ 4-5 estrelas representam sentimentos positivos

A análise é integrada ao backend Flask (via API REST) e também ao frontend desenvolvido com Streamlit, permitindo a interação visual e o envio de textos para avaliação de sentimento.

## 🔍 Retorno do modelo
O modelo retorna:

json
[
  {
    "label": "5 stars",
    "score": 0.89
  }
]

### A aplicação interpreta esse retorno para gerar categorias mais compreensíveis ao usuário:

- Bom (4 ou 5 estrelas)

- Neutro (3 estrelas)

- Ruim (1 ou 2 estrelas)

## ⚙️ Aplicações práticas

- Análise de respostas abertas de formulários

- Classificação de feedbacks de usuários

- Indicadores de sentimento para dashboards

- Visualização de opinião pública em sistemas internos

