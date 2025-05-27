import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from pathlib import Path

def load_auth_config():
    config_path = Path(__file__).resolve().parents[2] / "config.yaml"
    with open(config_path) as file:
        return yaml.load(file, Loader=SafeLoader)

def create_authenticator(config):
    return stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"]
    )
