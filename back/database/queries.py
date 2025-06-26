# back/database/queries.py

BUSCAR_ALUNOS = "SELECT * FROM Aluno"
INSERIR_ALUNO = "INSERT INTO Aluno (nome, matricula) VALUES (?, ?)"
