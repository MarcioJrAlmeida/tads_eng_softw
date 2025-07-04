-- CREATE DATABASE ml_ifpe_sado

USE ml_ifpe_sado;
GO

CREATE TABLE suspeitas_ofensivas (
    id INT IDENTITY(1,1) PRIMARY KEY,
    conteudo_resposta NVARCHAR(255),
    contexto_pergunta NVARCHAR(255),
    id_avaliacao INT,
    similaridade_palavra NVARCHAR(255),
    similaridade_frase NVARCHAR(255),
    sentimento_label VARCHAR(50),
    sentimento_score FLOAT,
    classificado_manual BIT DEFAULT 0,
    eh_ofensivo BIT NULL, -- NULL enquanto n�o for validado ou previsto pelo modelo
    data_insercao DATETIME DEFAULT GETDATE()
);


CREATE TABLE Frases_Analisadas (
    id INT IDENTITY(1,1) PRIMARY KEY,
	id_avaliacao INT,
    contexto_pergunta NVARCHAR(255),
	conteudo_resposta NVARCHAR(255),
    modelo_utilizado NVARCHAR(100),
    sentimento_classificado NVARCHAR(20), -- positivo, negativo, neutro
    ofensiva BIT,                         -- 1 = sim, 0 = n�o
    motivo_ofensivo NVARCHAR(200),       -- palavra-chave, similaridade, sem�ntica, etc.
    score FLOAT,
    data_analise DATETIME DEFAULT GETDATE()
);

CREATE TABLE Frases_Suspeitas (
    id INT IDENTITY(1,1) PRIMARY KEY,
	id_avaliacao INT,
    contexto_pergunta NVARCHAR(255),
	conteudo_resposta NVARCHAR(255),
    metodo_detectado NVARCHAR(100),      -- ex: rapidfuzz, profanity, BERT...
    tipo_suspeita NVARCHAR(50),          -- ex: leetspeak, similaridade, sem�ntica
    score FLOAT,
    analisada_por_ml BIT DEFAULT 0,
    eh_ofensiva BIT,                     -- NULL se ainda n�o classificada
    sentimento_previsto NVARCHAR(20),    -- baseado no modelo de ML
    data_registro DATETIME DEFAULT GETDATE()
);

CREATE TABLE Treinamento_Manual (
    id INT IDENTITY(1,1) PRIMARY KEY,
	contexto_pergunta NVARCHAR(255),
	conteudo_resposta NVARCHAR(255),
    classificada_como_ofensiva BIT,
    classificada_como_sentimento NVARCHAR(20),
    observacao NVARCHAR(255),
    data_classificacao DATETIME DEFAULT GETDATE()
);

CREATE TABLE Treinamento_Sentimento (
    id INT IDENTITY(1,1) PRIMARY KEY,
	contexto_pergunta NVARCHAR(MAX),
	conteudo_resposta NVARCHAR(MAX),
    classificada_como_sentimento NVARCHAR(20),
    observacao NVARCHAR(255),
    data_classificacao DATETIME DEFAULT GETDATE()
);

---- INSERT 
INSERT INTO [Treinamento_Sentimento] ([contexto_pergunta], [conteudo_resposta], [classificada_como_sentimento], [observacao])
SELECT [contexto_pergunta]
      ,[conteudo_resposta]
      --,[classificada_como_ofensiva]
      ,[classificada_como_sentimento]
      ,[observacao]
      --,[data_classificacao]
  FROM [ml_ifpe_sado].[dbo].[Treinamento_Manual]
  WHERE [classificada_como_ofensiva] = 0
