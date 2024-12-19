import hashlib
import streamlit as st
from streamlitgsheets import GSheetsConnection


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Create user
def add_user(username, password):
    conn = st.experimental_connection('gsheets', type=GSheetsConnection)
    conn.query('INSERT INTO users (username, password) VALUES (?, ?)', (username, hash_password(password)))


# Get User
def check_user(username, password):
    conn = st.experimental_connection('gsheets', type=GSheetsConnection)
    result = conn.query('SELECT * FROM users WHERE username = ? AND password = ?', (username, hash_password(password)))
    return result