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

database_questions = json.loads(json.load(open('data/questions/exam_questions_2024.json')))
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
        
        8. Se quiser fazer a mesma prova novamente, na mesma seção, clique no botão RELOAD.

        """)
        exam_qtd = st.selectbox(
            'Você quer fazer uma prova inteira de um determinado ano ou uma quantidade específica de questões de vários anos?',
            ('Questões de um determinado ano', 'Questões de anos variados'),
            index=None,
            placeholder='Escolha uma opção'
        )
        quiz = []
        if exam_qtd == 'Questões de um determinado ano':
            exams_years_options = [d['ano'] for d in database_questions]
            exam_year = st.selectbox(
                'Selecione o ano da prova que quer fazer',
                exams_years_options,
                index=None,
                placeholder='Escolha uma opção'
            )
            quiz = [database_questions[i]['questoes'][0] for i in range(0, len(database_questions)) if database_questions[i]['ano'] == exam_year]

        elif exam_qtd == 'Questões de anos variados':
            all_list_subject = [q["disciplina"] for d in database_questions for q in d["questoes"]]
            subject_list_options = sorted(list(set(all_list_subject)))
            subject_list = st.multiselect('Selecione as disciplinas que quer fazer',
                                          options=subject_list_options,
                                          placeholder='Disciplinas')
            quiz = []
            for subject in subject_list:
                qt_qu = st.selectbox(
                    f'Quantas questões de {subject}?',
                    ['Aleatório'] + [q for q in range(1, all_list_subject.count(subject) + 1)],
                    index=None,
                    placeholder='Escolha uma opção'
                )
                quiz_all = [database_questions[i]['questoes'] for i in range(0, len(database_questions))][0]
                if qt_qu:
                    questions_subject = [d for d in quiz_all if d["disciplina"] == subject]
                    if qt_qu != 'Aleatório':
                        rs = random.sample(questions_subject, k=qt_qu)
                    else:
                        ale = [a for a in range(1, len(questions_subject) + 1)]
                        rs = random.sample(questions_subject, k=random.choice(ale))
                    for r in rs:
                        quiz.append(r)
        
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
                    for i in range(len(quiz)):
                        number_placeholder = st.empty()
                        text_placeholder = st.empty()
                        question_placeholder = st.empty()
                        options_placeholder = st.empty()
                        results_placeholder = st.empty()
                        expander_area = st.empty()
                        current_question = i+1
                        
                        number_placeholder.write(f"**Questão {current_question}**")
                        
                        text_placeholder.write(f"**{quiz[i].get('texto_apoio')}**") 
                        
                        question_placeholder.write(f"**{quiz[i].get('enunciado')}**") 
                        
                        options = quiz[i].get("alternativas")
                        
                        options_placeholder.radio("", options, index=0, key=f"Q{current_question}")
                        nl(1)
                        st.divider()
                        
                        if ss.stop:
                            # Track length of user_answers
                            if len(ss.user_answers) < 10: 
                                # comparing answers to track score
                                correct_value = next(
                                    (alt for alt in quiz[i].get("alternativas") if alt.startswith(quiz[i].get("alternativa_correta") + ")")),
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
                            
                            expander_area.write(f"*{quiz[i].get('resolucao')}*\n\nAlternativa correta: {quiz[i].get('alternativa_correta')}")

            if ss.stop:  
                ss['grade'] = ss.user_answers.count(True)           
                scorecard_placeholder.write(f"### **Seu resultado final nessa tentativa : {ss['grade']} / {len(quiz)}**")
                answers_session_id = uuid.uuid4()
                answers_session = pd.DataFrame({'user_answers': ss.user_answers, 'subject': [d['disciplina'] for d in quiz], 'subject_detail': [a['assunto'] for a in quiz]})
                answers_session['id'] = answers_session_id
                grade_session = pd.DataFrame({'id': [uuid.uuid4()], 'user_id': [user_logged_in['id'][0]],
                                              'grade': [ss['grade']], 'total_questions': [len(quiz)], 
                                              'answers_session_id': [answers_session_id], 'created_at': [datetime.today().strftime('%d/%m/%Y')]})

                save_answers_session(answers_session)
                save_grade_session(grade_session)
        st.button(label=ss.button_label[ss.counter], 
                key='button_press', on_click= btn_click)
        nl(3)
        quiz_app()
        nl(1)

test_your_knowledge(True)