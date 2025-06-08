USE ifpe_sado

GO

SELECT
    a.id_avaliacao,
    p.texto_pergunta,
    r.conteudo_resposta
FROM Avaliacao a
JOIN Contem c ON a.id_avaliacao = c.id_avaliacao
JOIN Pergunta p ON c.id_pergunta = p.id_pergunta
JOIN Resposta r ON r.idAvaliacao = a.id_avaliacao
WHERE a.id_avaliacao = 1;
