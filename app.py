import streamlit as st
import pandas as pd
import base64
import streamlit_authenticator as stauth

from src.db import get_all_users



st.set_page_config(layout="wide", page_title="Simulado Fuvest", page_icon="📚")

users = get_all_users().to_dict()

emails = [v for k, v in users['email'].items()]
first_names = [v for k, v in users['first_name'].items()]
last_names = [v for k, v in users['last_name'].items()]
hashed_passwords = [v for k, v in users['password'].items()]

credentials = {"usernames": {first_name+last_name: {"name": first_name, "password": password, "email": email} for first_name, last_name, password, email in zip(first_names, last_names, hashed_passwords, emails)}}

authenticator = stauth.Authenticate(credentials, "simulado_fuvest", "abcdef", cookie_expiry_days=30)

authenticator.login("main", "Login")
authentication_status = st.session_state['authentication_status']

if authentication_status == False:
    st.error("Usuário/senha está incorreto")

if authentication_status == None:
    st.warning("Por favor, entre com seu usuário e senha")

if authentication_status:
    st.title('📚 Simulado Fuvest')
    st.divider()
    authenticator.logout("Sair", "sidebar")
    st.sidebar.title(f"Olá, {st.session_state['name']}!")

    st.sidebar.subheader('Opções')

    exam_type = st.sidebar.selectbox(
        'Para qual fase você quer fazer o simulado?',
        ('1ª fase', '2ª fase'),
        index=None,
        placeholder='Escolha uma opção'
    )

    if exam_type == '2ª fase':
        st.sidebar.text_input('Digite sua Gemini API Key')

    exam_qtd = st.sidebar.selectbox(
        'Você quer fazer uma prova inteira de um determinado ano ou uma quantidade específica de questões de vários anos?',
        ('Questões de um determinado ano', 'Questões de anos variados'),
        index=None,
        placeholder='Escolha uma opção'
    )
    if exam_qtd == 'Questões de um determinado ano':
        exame_year = st.sidebar.selectbox(
            'Selecione o ano da prova que quer fazer',
            [y for y in range(2010, 2024, 1)],
            index=None,
            placeholder='Escolha uma opção'
        )
    elif exam_qtd == 'Questões de anos variados':
        subject_list = st.sidebar.multiselect('Selecione as disciplinas que quer fazer',
                                            options=['Matemática', 'Gramática', 'Literatura', 'História', 'Geografia', 'Química', 'Biologia', 'etc'],
                                            placeholder='Disciplinas')
        for subject in subject_list:
            st.sidebar.selectbox(
                f'Quantas questões de {subject}?',
                ['Aleatório'] + [q for q in range(1, 11)],
                index=None,
                placeholder='Escolha uma opção'
            )

    df = pd.read_csv('df_teste.csv')
    im = df['image_str'][0]
    image_data = base64.b64decode(im)

    st.image(image_data)

