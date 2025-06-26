-- ==============================
--  INSERÇÃO DE DADOS
-- ==============================

USE ifpe_sado
GO

-- DELETE FROM Aluno

-- Tabela Diretor -- OK
INSERT INTO Diretor (id_diretor, nome_diretor, data_hr_registro)
VALUES (1, 'Francisco Junior', GETDATE());

-- Tabela Aluno -- OK
INSERT INTO Aluno (matricula, email, data_hr_registro) VALUES
('20242TADS-JG0018', 'arthur.lopes@discente.ifpe.edu.br', GETDATE()),
('20242TADS-JG0026', 'bruna.silva@discente.ifpe.edu.br', GETDATE()),
('20242TADS-JG0034', 'danilo.melo@discente.ifpe.edu.br', GETDATE()),
('20242TADS-JG0336', 'edson.filho@discente.ifpe.edu.br', GETDATE()),
('20242TADS-JG0042', 'eduardo.amaral@discente.ifpe.edu.br', GETDATE()),
('20242TADS-JG0050', 'gabriel.guimaraes@discente.ifpe.edu.br', GETDATE()),
('20242TADS-JG0131', 'gabriel.nascimento@discente.ifpe.edu.br', GETDATE()),
('20242TADS-JG0044', 'herik.lima@discente.ifpe.edu.br', GETDATE()),
('20242TADS-JG0344', 'guilherme.luz@discente.ifpe.edu.br', GETDATE()),
('20242TADS-JG0069', 'henio.martins@discente.ifpe.edu.br', GETDATE()),
('20242TADS-JG0077', 'igor.pedrosa@discente.ifpe.edu.br', GETDATE()),
('20242TADS-JG0220', 'italo.antonio@discente.ifpe.edu.br', GETDATE()),
('20242TADS-JG0328', 'jefferson.bablino@discente.ifpe.edu.br', GETDATE()),
('20242TADS-JG0158', 'joao.carvalho@discente.ifpe.edu.br', GETDATE()),
('20242TADS-JG0085', 'joao.melo@discente.ifpe.edu.br', GETDATE()),
('20242TADS-JG0093', 'jobson.santos@discente.ifpe.edu.br', GETDATE()),
('20242TADS-JG0107', 'jose.silva@discente.ifpe.edu.br', GETDATE()),
('20242TADS-JG0156', 'jose.santiago@discente.ifpe.edu.br', GETDATE()),
('20242TADS-JG0132', 'jose.costa@discente.ifpe.edu.br', GETDATE()),
('20242TADS-JG0140', 'julia.silva@discente.ifpe.edu.br', GETDATE()),
('20242TADS-JG0153', 'juliana.felix@discente.ifpe.edu.br', GETDATE()),
('20242TADS-JG0239', 'kayllany.franco@discente.ifpe.edu.br', GETDATE()),
('20242TADS-JG0247', 'leonardo.silva@discente.ifpe.edu.br', GETDATE()),
('20242TADS-JG0255', 'luana.silva@discente.ifpe.edu.br', GETDATE()),
('20242TADS-JG0262', 'luciana.rocha@discente.ifpe.edu.br', GETDATE()),
('20242TADS-JG0174', 'marcilio.filho@discente.ifpe.edu.br', GETDATE()),
('20242TADS-JG0263', 'marcone.araujo@discente.ifpe.edu.br', GETDATE()),
('20242TADS-JG0271', 'marcos.barros@discente.ifpe.edu.br', GETDATE()),
('20242TADS-JG0280', 'maressa.santos@discente.ifpe.edu.br', GETDATE()),
('20242TADS-JG0298', 'maria.silva@discente.ifpe.edu.br', GETDATE()),
('20242TADS-JG0300', 'maria.santos@discente.ifpe.edu.br', GETDATE()),
('20242TADS-JG0301', 'marian.lima@discente.ifpe.edu.br', GETDATE()),
('20242TADS-JG0310', 'philipe.paixao@discente.ifpe.edu.br', GETDATE()),
('20242TADS-JG0319', 'sergio.junior@discente.ifpe.edu.br', GETDATE()),
('20242TADS-JG0212', 'vitor.santos@discente.ifpe.edu.br', GETDATE()),
('20242TADS-JG0352', 'wandeson.tavares@discente.ifpe.edu.br', GETDATE());

-- Tabela Avaliacao -- OK
INSERT INTO Avaliacao (id_avaliacao, periodo, data_hr_registro, idDiretor)
VALUES (1, 202501, GETDATE(), 1);

-- Tabela Curso -- OK
INSERT INTO Curso (id_curso, nome_curso, data_hr_registro, idTurma)
VALUES (1, 'Análise e Desenvolvimento de Sistemas', GETDATE(), NULL);

-- Turma -- OK
INSERT INTO Turma (id_turma, data_hr_registro, idCurso)
VALUES (1, GETDATE(), 1);


-- Turma Aluno -- OK
INSERT INTO Turma_Aluno (id_turma, idAluno, data_hr_registro) VALUES
(1, '20242TADS-JG0018', GETDATE()),
(1, '20242TADS-JG0026', GETDATE()),
(1, '20242TADS-JG0034', GETDATE()),
(1, '20242TADS-JG0336', GETDATE()),
(1, '20242TADS-JG0042', GETDATE()),
(1, '20242TADS-JG0050', GETDATE()),
(1, '20242TADS-JG0131', GETDATE()),
(1, '20242TADS-JG0044', GETDATE()),
(1, '20242TADS-JG0344', GETDATE()),
(1, '20242TADS-JG0069', GETDATE()),
(1, '20242TADS-JG0077', GETDATE()),
(1, '20242TADS-JG0220', GETDATE()),
(1, '20242TADS-JG0328', GETDATE()),
(1, '20242TADS-JG0158', GETDATE()),
(1, '20242TADS-JG0085', GETDATE()),
(1, '20242TADS-JG0093', GETDATE()),
(1, '20242TADS-JG0107', GETDATE()),
(1, '20242TADS-JG0156', GETDATE()),
(1, '20242TADS-JG0132', GETDATE()),
(1, '20242TADS-JG0140', GETDATE()),
(1, '20242TADS-JG0153', GETDATE()),
(1, '20242TADS-JG0239', GETDATE()),
(1, '20242TADS-JG0247', GETDATE()),
(1, '20242TADS-JG0255', GETDATE()),
(1, '20242TADS-JG0262', GETDATE()),
(1, '20242TADS-JG0174', GETDATE()),
(1, '20242TADS-JG0263', GETDATE()),
(1, '20242TADS-JG0271', GETDATE()),
(1, '20242TADS-JG0280', GETDATE()),
(1, '20242TADS-JG0298', GETDATE()),
(1, '20242TADS-JG0300', GETDATE()),
(1, '20242TADS-JG0301', GETDATE()),
(1, '20242TADS-JG0310', GETDATE()),
(1, '20242TADS-JG0319', GETDATE()),
(1, '20242TADS-JG0212', GETDATE()),
(1, '20242TADS-JG0352', GETDATE());

-- Tabela Disciplina_Docente -- OK
INSERT INTO Disciplina_Docente (id_disciplina_docente, data_hr_registro)
VALUES 
(1, GETDATE()),
(2, GETDATE()),
(3, GETDATE()),
(4, GETDATE()),
(5, GETDATE()),
(6, GETDATE()),
(7, GETDATE());

-- Tabela Disciplina_Curso
INSERT INTO Disciplina_Curso (id_disciplina_curso, data_hr_registro, idCurso)
VALUES 
(1, GETDATE(), 1),
(2, GETDATE(), 1),
(3, GETDATE(), 1),
(4, GETDATE(), 1),
(5, GETDATE(), 1),
(6, GETDATE(), 1),
(7, GETDATE(), 1);

-- Tabela Professor -- OK
INSERT INTO Professor (id_professor, nome_docente, data_hr_registro, idDisciplina_Docente)
VALUES
(1, 'Emanuel Dantas', GETDATE(), 1),
(2, 'Josino Alves', GETDATE(), 2),
(3, 'Bruno Wagner', GETDATE(), 3),
(4, 'Viviane Cristina', GETDATE(), 4),
(5, 'Geraldo Azevedo', GETDATE(), 5),
(6, 'Juarez Oliveira', GETDATE(), 6),
(7, 'Diego dos Passos', GETDATE(), 7);

-- Tabela Disciplina -- OK
INSERT INTO Disciplina (id_disciplina, nome_disciplina, data_hr_registro, idDisciplina_Docente, idDisciplina_Curso)
VALUES 
(1, 'Banco de Dados I', GETDATE(), 1, 1),
(2, 'Programação Web 2', GETDATE(), 2, 1),
(3, 'Engenharia de Software', GETDATE(), 3, 1),
(4, 'Estruturas de Dados', GETDATE(), 4, 1),
(5, 'Matematica Discreta', GETDATE(), 5, 1),
(6, 'Inglês II', GETDATE(), 6, 1),
(7, 'Redes de Computadores', GETDATE(), 7, 1);

-- Tabela Pergunta -- OK
INSERT INTO Pergunta (id_pergunta, texto_pergunta, tipo_pergunta, data_hr_registro) VALUES
(1, 'O professor demonstra domínio profundo sobre os temas abordados?', 'Fechada', GETDATE()),
(2, 'As aulas seguem um plano coerente com os objetivos da disciplina?', 'Fechada', GETDATE()),
(3, 'O professor relaciona o conteúdo com situações práticas ou atuais?', 'Fechada', GETDATE()),
(4, 'Utiliza métodos variados para facilitar o aprendizado?', 'Fechada', GETDATE()),
(5, 'O conteúdo é apresentado de forma clara e organizada?', 'Fechada', GETDATE()),
(6, 'As explicações ajudam a esclarecer dúvidas e conceitos difíceis?', 'Fechada', GETDATE()),
(7, 'Comunica-se com clareza oral e escrita?', 'Fechada', GETDATE()),
(8, 'Estimula a participação e o diálogo durante as aulas?', 'Fechada', GETDATE()),
(9, 'Responde às dúvidas com atenção e paciência?', 'Fechada', GETDATE()),
(10, 'Os critérios de avaliação são claros desde o início da disciplina?', 'Fechada', GETDATE()),
(11, 'As correções são feitas dentro de prazos razoáveis?', 'Fechada', GETDATE()),
(12, 'Oferece feedback construtivo que contribui para o aprendizado?', 'Fechada', GETDATE()),
(13, 'Trata todos os alunos com respeito e imparcialidade?', 'Fechada', GETDATE()),
(14, 'Mantém comportamento ético e profissional?', 'Fechada', GETDATE()),
(15, 'Está disponível para apoiar os alunos fora do horário de aula?', 'Fechada', GETDATE());

INSERT INTO Pergunta (id_pergunta, texto_pergunta, tipo_pergunta, data_hr_registro)
VALUES (16, 'O que poderia ser melhorado na prática do docente?', 'Aberta', GETDATE());


-- Tabela Contém -- OK
INSERT INTO Contem (id_avaliacao, id_pergunta) VALUES
(1, 1),
(1, 2),
(1, 3),
(1, 4),
(1, 5),
(1, 6),
(1, 7),
(1, 8),
(1, 9),
(1, 10),
(1, 11),
(1, 12),
(1, 13),
(1, 14),
(1, 15);

INSERT INTO Contem (id_avaliacao, id_pergunta)
VALUES (1, 16);

-- Update Tabela Curso, para Coluna idTurma
UPDATE Curso
SET idTurma = 1
WHERE id_curso = 1;
