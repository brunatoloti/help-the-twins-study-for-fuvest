import ast
from datetime import datetime
import json
import pandas as pd
import random
import streamlit as st
import time
import uuid

from src.db import get_all_users, save_answers_session, save_grade_session

st.title('📚 Primeira fase')
st.divider()

database_questions = pd.read_json("data/questions_by_images/all/questions.json")
username = st.session_state.get('username')

users = get_all_users()
user_logged_in = users[users['first_name'].str.lower()+users['last_name'].str.lower() == username]

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
        exam_qtd = st.selectbox(
            'Você quer fazer uma prova inteira de um determinado ano ou uma quantidade específica de questões de vários anos?',
            ('Questões de um determinado ano', 'Questões de anos variados'),
            index=None,
            placeholder='Escolha uma opção'
        )
        quiz = pd.DataFrame()
        if exam_qtd == 'Questões de um determinado ano':
            exams_years_options = database_questions['ano'].unique()
            exam_year = st.selectbox(
                'Selecione o ano da prova que quer fazer',
                exams_years_options,
                index=None,
                placeholder='Escolha uma opção'
            )
            quiz = database_questions.query(f"ano == {exam_year}").reset_index(drop=True)

        elif exam_qtd == 'Questões de anos variados':
            all_list_subject = database_questions['disciplina'].unique()
            subject_list_options = sorted(list(set(all_list_subject)))
            subject_list = st.multiselect('Selecione as disciplinas que quer fazer',
                                          options=subject_list_options,
                                          placeholder='Disciplinas')
            quiz = pd.DataFrame()
            for subject in subject_list:
                qt_qu = st.selectbox(
                    f'Quantas questões de {subject}?',
                    ['Aleatório'] + [q for q in range(1, list(all_list_subject).count(subject) + 1)],
                    index=None,
                    placeholder='Escolha uma opção'
                )
                if qt_qu:
                    questions_subject = database_questions.query(f"disciplina == '{subject}'").reset_index(drop=True)
                    if qt_qu != 'Aleatório':
                        quiz = pd.concat([quiz, questions_subject.sample(n=qt_qu)])
                    else:
                        ale = [a for a in range(1, questions_subject.shape[0] + 1)]
                        quiz = pd.concat([quiz, questions_subject.sample(n=random.choice(ale))])
        
        scorecard_placeholder = st.empty()
        nl(2)
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
                    for i, row in quiz.iterrows():
                        number_placeholder = st.empty()
                        text_placeholder = st.empty()
                        question_placeholder = st.empty()
                        options_placeholder = st.empty()
                        results_placeholder = st.empty()
                        expander_area = st.empty()
                        current_question = i+1
                        
                        number_placeholder.write(f"**Questão {current_question}**")
                        
                        if row['texto_apoio']:
                            text_placeholder.write(f"**{row['texto_apoio']}**") 
                        
                        question_placeholder.write(f"**{row['enunciado']}**") 
                        
                        options = ast.literal_eval(row['alternativas'])
                        
                        options_placeholder.radio("", options, index=0, key=f"Q{current_question}")
                        nl(1)
                        st.divider()
                        
                        if ss.stop:
                            # Track length of user_answers
                            if len(ss.user_answers) < 90: 
                                # comparing answers to track score
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
                                results_placeholder.success("Correto")
                            else:
                                results_placeholder.error("Incorreto")
                            
                            expander_area.write(f"*{row['resolucao']}*\n\nAlternativa correta: {row['alternativa_correta']}")

            if ss.stop:  
                ss['grade'] = ss.user_answers.count(True)           
                scorecard_placeholder.write(f"### **Seu resultado final nessa tentativa : {ss['grade']} / {quiz.shape[0]}**")
                answers_session_id = uuid.uuid4()
                answers_session = pd.DataFrame({'user_answers': ss.user_answers, 'subject': list(quiz['disciplina']), 'subject_detail': list(quiz['assunto'])})
                answers_session['id'] = answers_session_id
                grade_session = pd.DataFrame({'id': [uuid.uuid4()], 'user_id': [user_logged_in['id'][0]],
                                              'grade': [ss['grade']], 'total_questions': [quiz.shape[0]], 
                                              'answers_session_id': [answers_session_id], 'created_at': [datetime.today().strftime('%d/%m/%Y')]})

                save_answers_session(answers_session)
                save_grade_session(grade_session)
        st.button(label=ss.button_label[ss.counter], 
                key='button_press', on_click= btn_click)
        nl(3)
        quiz_app()
        nl(1)

test_your_knowledge(True)