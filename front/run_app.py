# run_app.py
import os
import sys
import subprocess
from pathlib import Path
import shutil


# Caminho raiz do projeto
root_dir = Path(__file__).resolve().parent

# Adiciona o caminho ao sys.path e PYTHONPATH
sys.path.insert(0, str(root_dir))
os.environ["PYTHONPATH"] = str(root_dir)

# Copia config.toml para ~/.streamlit
streamlit_config_dir = Path.home() / ".streamlit"
streamlit_config_dir.mkdir(exist_ok=True)
shutil.copyfile(root_dir / "app" / "streamlit" / "config.toml", streamlit_config_dir / "config.toml")

# Roda o Streamlit apontando para app/login.py
subprocess.run(["streamlit", "run", str(root_dir / "app" / "login.py")])

# import streamlit as st
# from PIL import Image

# # Configurações da página
# st.set_page_config(
#     page_title="Sistema de Avaliação Docente",
#     page_icon="📊",
#     layout="wide"
# )

# # Logo ou cabeçalho
# st.title("📊 Sistema de Avaliação Docente")
# st.subheader("Projeto - TADS IFPE | Engenharia de Software")

# st.markdown("""
# Bem-vindo ao sistema de avaliação de docentes. 
# Utilize o menu lateral para navegar entre as páginas disponíveis.
# """)

# # Imagem opcional (se tiver na pasta /assets)
# # image = Image.open('assets/logo.png')
# # st.image(image, width=300)

# st.info("Escolha uma página no menu lateral para começar.")
