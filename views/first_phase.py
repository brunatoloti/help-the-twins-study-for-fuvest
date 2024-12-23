import streamlit as st
import pandas as pd
import base64


st.title('📚 Simulado Fuvest')
st.divider()


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