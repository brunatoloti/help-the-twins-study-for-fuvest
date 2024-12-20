import hashlib
import streamlit as st
from streamlit_gsheets import GSheetsConnection

from src.utils import generate_uuid


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Create user
def add_user(first_name, last_name, password, email):
    conn = st.connection('gsheets', type=GSheetsConnection)
    conn.query('INSERT INTO users (id, first_name, last_name, password, email) VALUES (?, ?, ?, ?, ?)', (str(generate_uuid()), first_name, last_name, hash_password(password), email))


# Get User
def check_user(username, password):
    conn = st.connection('gsheets', type=GSheetsConnection)
    result = conn.query('SELECT * FROM users WHERE username = ? AND password = ?', (username, hash_password(password)))
    return result


def get_all_users():
    conn = st.connection('gsheets', type=GSheetsConnection)
    result = conn.query('SELECT * FROM users')
    return result