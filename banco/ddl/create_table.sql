-- CREATE DATABASE ifpe_sado;

USE ifpe_sado
GO
-- TABELAS

CREATE TABLE Aluno (
    matricula VARCHAR(30) PRIMARY KEY,
    email VARCHAR(100),
    data_hr_registro DATETIME
);

CREATE TABLE Professor (
    id_professor INT PRIMARY KEY,
    nome_docente VARCHAR(100),
    data_hr_registro DATETIME,
    idDisciplina_Docente INT
);

CREATE TABLE Diretor (
    id_diretor INT PRIMARY KEY,
    nome_diretor VARCHAR(100),
    data_hr_registro DATETIME
);

CREATE TABLE Curso (
    id_curso INT PRIMARY KEY,
    nome_curso VARCHAR(100),
    data_hr_registro DATETIME,
    idTurma INT
);

CREATE TABLE Disciplina (
    id_disciplina INT PRIMARY KEY,
    nome_disciplina VARCHAR(100),
    data_hr_registro DATETIME,
    idDisciplina_Docente INT,
    idDisciplina_Curso INT
);

CREATE TABLE Disciplina_Docente (
    id_disciplina_docente INT PRIMARY KEY,
    data_hr_registro DATETIME
);

CREATE TABLE Avaliacao (
    id_avaliacao INT PRIMARY KEY,
    periodo INT,
    data_hr_registro DATETIME,
    idDiretor INT,
    modelo_avaliacao NVARCHAR(MAX), -- Novo campo para armazenar JSON com configuração
    status_avaliacao VARCHAR(10) DEFAULT 'Inativo',  -- Novo campo para armazenar o status da avaliação ou lançamento dela
    data_lancamento DATETIME -- Novo campo para armazenar a data laçamento do formulario
);


CREATE TABLE Pergunta (
    id_pergunta INT PRIMARY KEY,
    texto_pergunta VARCHAR(255),
    tipo_pergunta VARCHAR(50),
    data_hr_registro DATETIME
);

CREATE TABLE Resposta (
    id_resposta INT PRIMARY KEY,
    conteudo_resposta VARCHAR(MAX),
    data_hr_registro DATETIME,
    idAvaliacao INT,
    id_pergunta INT
);

CREATE TABLE Disciplina_Curso (
    id_disciplina_curso INT PRIMARY KEY,
    data_hr_registro DATETIME,
    idCurso INT
);

CREATE TABLE Turma (
    id_turma INT PRIMARY KEY,
    data_hr_registro DATETIME,
    idCurso INT,
    FOREIGN KEY (idCurso) REFERENCES Curso(id_curso)
);

CREATE TABLE Turma_Aluno (
    id_turma INT,
    idAluno VARCHAR(30),
    data_hr_registro DATETIME,
    PRIMARY KEY (id_turma, idAluno),
    FOREIGN KEY (id_turma) REFERENCES Turma(id_turma),
    FOREIGN KEY (idAluno) REFERENCES Aluno(matricula)
);


CREATE TABLE Contem (
    id_avaliacao INT,
    id_pergunta INT,
    PRIMARY KEY (id_avaliacao, id_pergunta)
);

CREATE TABLE Possui (
    id_disciplina_docente INT,
    id_resposta INT,
    PRIMARY KEY (id_disciplina_docente, id_resposta)
);

-- RELACIONAMENTOS (FKs)

ALTER TABLE Professor
ADD FOREIGN KEY (idDisciplina_Docente) REFERENCES Disciplina_Docente(id_disciplina_docente);

ALTER TABLE Curso
ADD FOREIGN KEY (idTurma) REFERENCES Turma(id_turma);

ALTER TABLE Disciplina
ADD FOREIGN KEY (idDisciplina_Docente) REFERENCES Disciplina_Docente(id_disciplina_docente);

ALTER TABLE Disciplina
ADD FOREIGN KEY (idDisciplina_Curso) REFERENCES Disciplina_Curso(id_disciplina_curso);

ALTER TABLE Avaliacao
ADD FOREIGN KEY (idDiretor) REFERENCES Diretor(id_diretor);

ALTER TABLE Resposta
ADD FOREIGN KEY (idAvaliacao) REFERENCES Avaliacao(id_avaliacao);

ALTER TABLE Disciplina_Curso
ADD FOREIGN KEY (idCurso) REFERENCES Curso(id_curso);

ALTER TABLE Contem
ADD FOREIGN KEY (id_avaliacao) REFERENCES Avaliacao(id_avaliacao);

ALTER TABLE Contem
ADD FOREIGN KEY (id_pergunta) REFERENCES Pergunta(id_pergunta);

ALTER TABLE Possui
ADD FOREIGN KEY (id_disciplina_docente) REFERENCES Disciplina_Docente(id_disciplina_docente);

ALTER TABLE Possui
ADD FOREIGN KEY (id_resposta) REFERENCES Resposta(id_resposta);

ALTER TABLE Resposta 
ADD FOREIGN KEY (id_pergunta) REFERENCES Pergunta(id_pergunta);
