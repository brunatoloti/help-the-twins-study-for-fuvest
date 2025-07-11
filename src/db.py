import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection


def get_all_users():
    conn = st.connection('gsheets', type=GSheetsConnection)
    result = conn.query('SELECT * FROM users')
    return result


def get_all_first_phase_questions():
    conn = st.connection('gsheets', type=GSheetsConnection)
    questions = conn.query('SELECT * FROM first_phase_questions;')
    return questions


def get_sessions_results_by_user(user_id):
    conn = st.connection('gsheets', type=GSheetsConnection)
    session_results = conn.query(f"""SELECT g.id, g.grade, g.total_questions, g.created_at, a.user_answers, a.subject, a.subject_detail
                                        FROM grade_session g 
                                        JOIN answers_session a 
                                        ON g.answers_session_id=a.id 
                                        WHERE user_id='{user_id}';""")
    return session_results



def save_grade_session(df):
    conn = st.connection('gsheets', type=GSheetsConnection)
    gs = conn.query('SELECT * FROM grade_session;')
    df = pd.concat([gs, df])
    conn.update(worksheet='grade_session', data=df)
    st.cache_data.clear()


def save_answers_session(df):
    conn = st.connection('gsheets', type=GSheetsConnection)
    aso = conn.query('SELECT * FROM answers_session;')
    df = pd.concat([aso, df])
    conn.update(worksheet='answers_session', data=df)
    st.cache_data.clear()