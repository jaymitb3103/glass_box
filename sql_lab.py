import streamlit as st
import sqlite3

# --- 1. SETUP THE DATABASE (In-Memory) ---
# We run this every time the app loads to reset the sandbox
conn = sqlite3.connect(':memory:')
c = conn.cursor()

# Table 1: Users (For Levels 1 & 2)
c.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)')
c.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'super_secret_pass', 'administrator')")
c.execute("INSERT INTO users (username, password, role) VALUES ('alice', 'alice123', 'user')")
c.execute("INSERT INTO users (username, password, role) VALUES ('bob', 'bob456', 'user')")

# Table 2: The Hidden Loot (For Level 3)
# Hackers want this table.
c.execute('CREATE TABLE credit_cards (id INTEGER PRIMARY KEY, owner TEXT, cc_number TEXT, cvv TEXT)')
c.execute("INSERT INTO credit_cards (owner, cc_number, cvv) VALUES ('Elon Musk', '4444-5555-6666-7777', '123')")
c.execute("INSERT INTO credit_cards (owner, cc_number, cvv) VALUES ('Jeff Bezos', '1111-2222-3333-4444', '999')")

conn.commit()

# --- 2. APP CONFIG ---
st.set_page_config(page_title="SQLi Training Lab", page_icon="🛡️", layout="wide")

st.sidebar.title("🎚️ Mission Select")
level = st.sidebar.radio("Choose Difficulty:", [
    "Level 1: Login Bypass (No Filter)", 
    "Level 2: Login Bypass (Blacklist)",
    "Level 3: The Data Heist (UNION)"
])

st.title("🛡️ The Glass Box")

# --- LEVEL 1 & 2 LOGIC (Login Bypass) ---
if level in ["Level 1: Login Bypass (No Filter)", "Level 2: Login Bypass (Blacklist)"]:
    
    if level == "Level 1: Login Bypass (No Filter)":
        st.subheader("Level 1: The Open Door")
        st.info("Mission: Log in as 'admin' without the password.")
    else:
        st.subheader("Level 2: The Blacklist")
        st.warning("Mission: The developer blocked 'OR' and '--'. Can you still get in?")

    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("Username", value="admin")
        password = st.text_input("Password", type="password")
        login = st.button("Login")
    
    # Construct the Query based on Level
    if level == "Level 1: Login Bypass (No Filter)":
        query = f"SELECT * FROM users WHERE username = '{username