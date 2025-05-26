import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

def load_auth_config():
    with open("config.yaml") as file:
        return yaml.load(file, Loader=SafeLoader)

def create_authenticator(config):
    return stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"]
    )
