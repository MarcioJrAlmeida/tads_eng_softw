# backend_app.py
import sys
from pathlib import Path
from flask import Flask

# Adiciona o caminho raiz ao PYTHONPATH
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from app.api.perguntas_service import pergunta_api
from app.api.configuracao_service import configuracao_api 
from app.api.avaliacao_service import modelo_avaliacao_api, avaliacoes_api

app = Flask(__name__)
app.register_blueprint(pergunta_api, url_prefix="/api")
app.register_blueprint(configuracao_api, url_prefix="/api") 
app.register_blueprint(modelo_avaliacao_api, url_prefix='/api')
app.register_blueprint(avaliacoes_api, url_prefix='/api')


if __name__ == '__main__':
    app.run(debug=True, port=5001)
