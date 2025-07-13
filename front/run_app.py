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
os.environ["STREAMLIT_WATCH_DISABLE"] = "true"

# Copia config.toml para ~/.streamlit
streamlit_config_dir = Path.home() / ".streamlit"
streamlit_config_dir.mkdir(exist_ok=True)
shutil.copyfile(root_dir / "app" / "streamlit" / "config.toml", streamlit_config_dir / "config.toml")

# Roda o Streamlit apontando para app/login.py
subprocess.run(["streamlit", "run", str(root_dir / "app" / "login.py")])
