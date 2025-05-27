import { useState } from 'react';
import StarRating from './StarRating';
import Resultado from './Resultado';
import { motion, AnimatePresence } from 'framer-motion';
import './FormularioPW1.css';

const FormularioPW1 = () => {
  const perguntas = [
    "O professor explicou bem os conceitos de HTML?",
    "O professor trouxe bons exemplos sobre CSS?",
    "As aulas sobre JavaScript foram claras?",
    "O professor tornou as aulas interativas?",
  ];

  const totalEtapas = perguntas.length + 1; // +1 para o comentário opcional

  const [respostas, setRespostas] = useState<number[]>(Array(perguntas.length).fill(0));
  const [comentario, setComentario] = useState('');
  const [etapaAtual, setEtapaAtual] = useState(0);
  const [concluido, setConcluido] = useState(false);

  const handleResposta = (nota: number) => {
    const novasRespostas = [...respostas];
    novasRespostas[etapaAtual] = nota;
    setRespostas(novasRespostas);
    handleProximo();
  };

  const handleProximo = () => {
    if (etapaAtual < totalEtapas - 1) {
      setEtapaAtual(etapaAtual + 1);
    } else {
      setConcluido(true);
    }
  };

  const handleVoltar = () => {
    if (etapaAtual > 0) {
      setEtapaAtual(etapaAtual - 1);
    }
  };

  const progresso = ((etapaAtual + 1) / totalEtapas) * 100;

  return (
    <div className="container-formulario">
      {/* <h1>🚀 Formulário de Avaliação - Programação Web 1</h1> */}

      <div className="barra-progresso">
        <div className="progresso" style={{ width: `${progresso}%` }}></div>
      </div>

      <AnimatePresence>
        {!concluido ? (
          <motion.div
            key={etapaAtual}
            className="card"
            initial={{ opacity: 0, x: 100 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -100 }}
            transition={{ duration: 0.4 }}
          >
            {etapaAtual < perguntas.length ? (
              <>
                <h2>{perguntas[etapaAtual]}</h2>
                <StarRating
                  value={respostas[etapaAtual]}
                  onChange={handleResposta}
                />
                <div className="botoes">
                  {etapaAtual > 0 && (
                    <button onClick={handleVoltar}>⬅️ Voltar</button>
                  )}
                </div>
              </>
            ) : (
              <>
                <h2>✍️ Comentário opcional (máx. 240 caracteres)</h2>
                <textarea
                  value={comentario}
                  onChange={(e) =>
                    e.target.value.length <= 240 &&
                    setComentario(e.target.value)
                  }
                  rows={4}
                  placeholder="Digite aqui seu comentário..."
                  className="input-comentario"
                />
                <p>{comentario.length}/240 caracteres</p>
                <div className="botoes">
                  <button onClick={handleVoltar}>⬅️ Voltar</button>
                  <button onClick={handleProximo}>✅ Finalizar</button>
                </div>
              </>
            )}
          </motion.div>
        ) : (
          <Resultado respostas={respostas} perguntas={perguntas} comentario={comentario} />
        )}
      </AnimatePresence>
    </div>
  );
};

export default FormularioPW1;
