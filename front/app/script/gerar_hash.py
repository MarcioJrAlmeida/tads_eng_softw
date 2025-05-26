import streamlit_authenticator as stauth
import bcrypt

senha_dir = 'diretor123'
hash_dir = stauth.Hasher(['diretor123']).generate()[0]
print("\nHash gerado diretor:\n", hash_dir)


senha_coord = "coordenador123"
hash_coord = stauth.Hasher(['coordenador123']).generate()[0]
print("\nHash gerado coordenador:\n", hash_coord)
