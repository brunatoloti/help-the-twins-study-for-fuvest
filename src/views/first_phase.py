import ast
from datetime import datetime
from io import BytesIO
import json
import pandas as pd
import random
import requests
import streamlit as st
import time
import uuid

from src.db import get_all_users, save_answers_session, save_grade_session, get_all_first_phase_questions

st.title('📚 Primeira fase')
st.divider()

if st.session_state['authentication_status']:
    database_questions = get_all_first_phase_questions()
    database_questions = database_questions.astype({'ano': int, 'numero': int})
    username = st.session_state.get('username')

    users = get_all_users()
    user_logged_in = users[users['first_name'].str.lower()+users['last_name'].str.lower() == username].reset_index(drop=True)

    def nl(num_of_lines):
        for i in range(num_of_lines):
            st.write(" ")

    content_placeholder = st.empty()
    body_placeholder = st.empty()

    def set_landing_page(page_title = True):
        if page_title is False:
            content_placeholder.empty()
            body_placeholder.empty() 
        else:
            content_placeholder.empty()
            content_placeholder.header(page)
            body_placeholder.empty()

    def test_your_knowledge(val=False):
        if val == True:
            global page
            page = f"Teste seus conhecimentos, {user_logged_in['first_name'][0]}!"  
            set_landing_page()
            nl(1)
            st.markdown(f"""
            *Que tal testar suas habilidades nas questões da Fuvest?*
            \n*Leia as instruções abaixo e comece a prova.*

            Instruções:
            1. Selecione se quer fazer uma prova de um ano específico ou de anos variados.
                
            2. Se quiser fazer uma prova de um ano específico, selecione o ano que deseja fazer. 
            Se quiser fazer uma prova de anos variados, escolha as disciplinas que deseja fazer e quantas questões de cada. 
            Para o caso de anos variados, após escolher as disciplinas e as quantidades de cada uma, clique no botão CHOSEN.

            3. Quando estiver pronto, clique no botão START.
                        
            4. A alternativa "a" virá selecionada como padrão.
                
            5. Quando finalizar a prova, volte ao início da página e clique no botão SUBMIT.

            6. A prova não tem tempo máximo.

            7. Ao clicar no botão SUBMIT, verá seu resultado e as resoluções das questões com o gabarito. 
            Além disso, na aba Dashboard você verá seus resultados com mais detalhes.    
            
            8. Depois de finalizar a verificação do gabarito, ao finalizar a prova, sempre clique no botão RELOAD.
                        
            9. As resoluções foram criadas por uma IA. Logo, pode haver erros. 
            Porém, as alternativas indicadas como corretas seguem o gabarito oficial.

            """)

            ss = st.session_state
            
            if 'counter' not in ss:
                ss['counter'] = 0
            if 'start' not in ss:
                ss['start'] = False
            if 'stop' not in ss:
                ss['stop'] = False
            if 'refresh' not in ss:
                ss['refresh'] = False
            if "button_label" not in ss:
                ss['button_label'] = ['START', 'SUBMIT', 'RELOAD']
            if 'current_quiz' not in ss:
                ss['current_quiz'] = {}
            if 'user_answers' not in ss:
                ss['user_answers'] = []
            if 'grade' not in ss:
                ss['grade'] = 0
            if 'quiz' not in ss:
                ss['quiz'] = pd.DataFrame()

            exam_qtd = st.selectbox(
                'Você quer fazer uma prova inteira de um determinado ano ou uma quantidade específica de questões de vários anos?',
                ('Questões de um determinado ano', 'Questões de anos variados'),
                index=None,
                placeholder='Escolha uma opção'
            )

            if exam_qtd == 'Questões de um determinado ano':
                quiz = pd.DataFrame()
                exams_years_options = database_questions['ano'].unique()
                exam_year = st.selectbox(
                    'Selecione o ano da prova que quer fazer',
                    exams_years_options,
                    index=None,
                    placeholder='Escolha uma opção'
                )
                quiz = database_questions.query(f"ano == {exam_year}").reset_index(drop=True)
                st.session_state.quiz = quiz

            elif exam_qtd == 'Questões de anos variados':
                exam_varied_types = st.selectbox(
                    'Você quer fazer por disciplina ou por assunto?',
                    ('Por disciplina', 'Por assunto'),
                    index=None,
                    placeholder='Escolha uma opção'
                )
                if exam_varied_types == 'Por disciplina':
                    evt = 'disciplina'
                    nn = 'as'
                elif exam_varied_types == 'Por assunto':
                    evt = 'assunto'
                    nn = 'os'
                if exam_varied_types:
                    col1, col2 = st.columns([3, 1])
                    all_list_subject = database_questions[evt].unique()
                    subject_list_options = sorted(list(set(all_list_subject)))
                    with col1:
                        subject_list = st.multiselect(f'Selecione {nn} {evt}s que quer fazer',
                                                    options=subject_list_options,
                                                    placeholder=evt.title())
                        qt_questions = {}
                        for subject in subject_list:
                            max_linhas = database_questions[database_questions[evt] == subject].shape[0]
                            qt_questions[subject] = st.number_input(
                                f"Número de questões para '{subject}' (máx: {max_linhas})",
                                min_value=1,
                                max_value=max_linhas,
                                step=1,
                                key=f"n_{subject}"
                            )
                    with col2: 
                        st.write(f'Quando finalizar a escolha d{nn} {evt}s e o respectivo número de questões, clique no botão.')
                        if st.button('CHOSEN', disabled=not subject_list):
                            quiz = pd.concat([
                                database_questions[database_questions[evt] == subject].sample(n=n)
                                for subject, n in qt_questions.items()
                            ]).reset_index(drop=True)
                            if ss.quiz.empty:
                                st.session_state.quiz = quiz
            
            scorecard_placeholder = st.empty()
            nl(2)

            def btn_click():
                ss.counter += 1
                if ss.counter > 2: 
                    ss.counter = 0
                    ss.clear()
                else:
                    update_session_state()
                    with st.spinner("*this may take a while*"):
                        time.sleep(2)

            def update_session_state():
                if ss.counter == 1:
                    ss['start'] = True
                elif ss.counter == 2:
                    ss['start'] = True 
                    ss['stop'] = True
                elif ss.counter == 3:
                    ss['start'] = ss['stop'] = False
                    ss['refresh'] = True
                    ss.clear()

            def quiz_app():
                with st.container():
                    if (ss.start):
                        for i, row in st.session_state.quiz.iterrows():
                            current_question = i+1
                            
                            st.write(f"**Questão {current_question}**")
                            images_in_questions = ast.literal_eval(row['imagens_nas_questoes'])
                            if row['texto_apoio']:
                                text_enunc = row['texto_apoio'] + '\n\n' + row['enunciado']
                            else:
                                text_enunc = row['enunciado']
                            if images_in_questions:
                                if '{imagem}' in text_enunc:
                                    im_text = text_enunc.split('{imagem}')
                                    qt_im_text = len(images_in_questions) + 1
                                    for im in range(qt_im_text):
                                        if im_text[im]:
                                            st.markdown(f"<b>{im_text[im]}</b>", unsafe_allow_html=True)
                                        if im < qt_im_text - 1:
                                            req = requests.get(f"https://drive.google.com/uc?export=view&id={images_in_questions[im]}")
                                            image_data_text = BytesIO(req.content)
                                            st.image(image_data_text)
                                else:
                                    st.markdown(f"<b>{text_enunc}</b>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<b>{text_enunc}</b>", unsafe_allow_html=True)

                            options = ast.literal_eval(row['alternativas'])
                            images_in_options = ast.literal_eval(row['imagens_nas_alternativas'])
                            if images_in_options:
                                col1, col2 = st.columns(2)
                                with col1:
                                    req = requests.get(f"https://drive.google.com/uc?export=view&id={images_in_options[0]}")
                                    image_data = BytesIO(req.content)
                                    st.image(image_data, caption='I')
                                    req = requests.get(f"https://drive.google.com/uc?export=view&id={images_in_options[1]}")
                                    image_data = BytesIO(req.content)
                                    st.image(image_data, caption='II')
                                    req = requests.get(f"https://drive.google.com/uc?export=view&id={images_in_options[2]}")
                                    image_data = BytesIO(req.content)
                                    st.image(image_data, caption='III')
                                with col2:
                                    req = requests.get(f"https://drive.google.com/uc?export=view&id={images_in_options[3]}")
                                    image_data = BytesIO(req.content)
                                    st.image(image_data, caption='IV')
                                    req = requests.get(f"https://drive.google.com/uc?export=view&id={images_in_options[4]}")
                                    image_data = BytesIO(req.content)
                                    st.image(image_data, caption='V')
                            
                            st.radio("abcde", options, index=0, key=f"Q{current_question}", label_visibility='hidden')
                            nl(1)
                            
                            if ss.stop:
                                if len(ss.user_answers) < 90: 
                                    correct_value = next(
                                        (alt for alt in options if alt.startswith(row['alternativa_correta'] + ")")),
                                        None
                                    )
                                    if ss[f'Q{current_question}'] == correct_value:
                                        ss.user_answers.append(True)
                                    else:
                                        ss.user_answers.append(False)
                                else:
                                    pass
                                if ss.user_answers[i] == True:
                                    st.success("Correto")
                                else:
                                    st.error("Incorreto")
                                
                                st.write(f"*{row['resolucao']}*\n\nAlternativa correta: {row['alternativa_correta']}")
                            st.divider()

                if ss.stop:  
                    ss['grade'] = ss.user_answers.count(True)           
                    scorecard_placeholder.write(f"### **Seu resultado final nessa tentativa : {ss['grade']} / {st.session_state.quiz.shape[0]}**")
                    answers_session_id = uuid.uuid4()
                    answers_session = pd.DataFrame({'user_answers': ss.user_answers, 'subject': list(st.session_state.quiz['disciplina']), 'subject_detail': list(st.session_state.quiz['assunto'])})
                    answers_session['id'] = answers_session_id
                    grade_session = pd.DataFrame({'id': [uuid.uuid4()], 'user_id': [user_logged_in['id'][0]],
                                                'grade': [ss['grade']], 'total_questions': [st.session_state.quiz.shape[0]], 
                                                'answers_session_id': [answers_session_id], 'created_at': [datetime.today().strftime('%d/%m/%Y')]})

                    save_answers_session(answers_session)
                    save_grade_session(grade_session)
            st.button(label=ss.button_label[ss.counter], 
                    key='button_press', on_click= btn_click)
            nl(3)
            quiz_app()
            nl(1)

    test_your_knowledge(True)