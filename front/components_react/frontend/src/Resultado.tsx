interface ResultadoProps {
  respostas: number[];
  perguntas: string[];
  comentario: string;
}

const Resultado = ({ respostas, perguntas, comentario }: ResultadoProps) => {
  const totalPontos = respostas.reduce((acc, val) => acc + val, 0) * 10;

  const badge =
    totalPontos >= 150 ? "🏆 Avaliador de Ouro"
    : totalPontos >= 100 ? "🥈 Avaliador Prata"
    : totalPontos >= 50 ? "🥉 Avaliador Bronze"
    : "🔰 Iniciante";

  const badgeComentario = comentario.trim().length > 0 ? "💡 Comentário Valioso" : null;

  return (
    <div className="card">
      <h2>✅ Avaliação Concluída!</h2>
      <p>🎯 Pontuação Total: <strong>{totalPontos} pontos</strong></p>
      <h3>🏅 Conquista: <strong>{badge}</strong></h3>
      {badgeComentario && <h4>{badgeComentario}</h4>}

      <ul>
        {perguntas.map((pergunta, index) => (
          <li key={index}>
            {pergunta} → ⭐ {respostas[index]}
          </li>
        ))}
      </ul>

      {comentario.trim() && (
        <>
          <h4>📝 Seu Comentário:</h4>
          <p>{comentario}</p>
        </>
      )}
    </div>
  );
};

export default Resultado;
