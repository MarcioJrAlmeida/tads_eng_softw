-- Inserções Dados Ficticios

INSERT INTO Aluno (matricula, email, data_hr_registro) VALUES
(101, 'ana@ifpe.edu.br', GETDATE()),
(102, 'joao@ifpe.edu.br', GETDATE());

INSERT INTO Diretor (id_diretor, nome_diretor, data_hr_registro) VALUES
(1, 'Marcos Almeida', GETDATE());

INSERT INTO Avaliacao (id_avaliacao, periodo, data_hr_registro, idDiretor) VALUES
(1, 2024, GETDATE(), 1);

INSERT INTO Pergunta (id_pergunta, texto_pergunta, tipo_pergunta, data_hr_registro) VALUES
(1, 'Como você avalia o docente?', 'Objetiva', GETDATE()),
(2, 'A disciplina foi bem conduzida?', 'Objetiva', GETDATE());

INSERT INTO Resposta (id_resposta, conteudo_resposta, data_hr_registro, idAvaliacao) VALUES
(1, 'Muito bom', GETDATE(), 1),
(2, 'Sim, com certeza', GETDATE(), 1);

INSERT INTO Contem (id_avaliacao, id_pergunta) VALUES
(1, 1),
(1, 2);

INSERT INTO Disciplina_Docente (id_disciplina_docente, data_hr_registro)
VALUES (1, GETDATE());

INSERT INTO Possui (id_disciplina_docente, id_resposta) VALUES
(1, 1),
(1, 2);