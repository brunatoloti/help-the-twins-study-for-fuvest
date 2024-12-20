import base64
import pandas as pd
import streamlit as st
import uuid


def codifica():
    image_path = "images/questao.png"
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    print(encoded_string)
    df = pd.DataFrame({'image_str': [encoded_string]})
    df.to_csv('df_teste.csv', index=False)


def sign_up_user():
    st.subheader("Cadastro de Usuário")
    new_user = st.text_input("Nome de Usuário")
    new_password = st.text_input("Senha", type="password")
    st.button("Cadastrar")


def generate_uuid():
    return uuid.uuid4()