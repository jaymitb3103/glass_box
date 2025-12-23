import streamlit as st
import sqlite3

# --- SETUP (Same DB as before) ---
conn = sqlite3.connect(':memory:')
c = conn.cursor()
c.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)')
c.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'super_secret_pass', 'administrator')")
conn.commit()

st.set_page_config(page_title="SQLi Training Lab", page_icon="🛡️", layout="wide")

# --- SIDEBAR: LEVEL SELECTOR ---
st.sidebar.title("🎚️ Mission Select")
level = st.sidebar.radio("Choose Difficulty:", ["Level 1: No Defense", "Level 2: The Blacklist"])

st.title("🛡️ The Glass Box: SQL Injection")

# --- LEVEL LOGIC ---

if level == "Level 1: No Defense":
    st.subheader("Level 1: The Open Door")
    st.info("Mission: Log in as 'admin' without the password.")
    
    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("Username", value="admin")
        password = st.text_input("Password", type="password")
        login = st.button("Login (Level 1)")
    
    # VULNERABLE QUERY (Direct F-String)
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    
    with col2:
        st.markdown("### 🔍 The Glass Box")
        st.code(query, language="sql")

    if login:
        try:
            c.execute(query)
            if c.fetchone():
                st.balloons()
                st.success("✅ HACKED! You bypassed the login.")
            else:
                st.error("❌ Access Denied")
        except Exception as e:
            st.warning(f"⚠️ SQL Error: {e}")


elif level == "Level 2: The Blacklist":
    st.subheader("Level 2: The 'Stupid' Firewall")
    st.warning("Mission: The developer has blocked the word 'OR' and '--'. Can you still get in?")
    
    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("Username (Lvl 2)", value="admin")
        password = st.text_input("Password (Lvl 2)", type="password")
        login = st.button("Login (Level 2)")

    # THE "DEFENSE": Removing dangerous keywords
    # This is a bad way to secure code, but common in beginner apps.
    clean_user = username.replace("OR", "").replace("--", "").replace("or", "")
    
    query = f"SELECT * FROM users WHERE username = '{clean_user}' AND password = '{password}'"
    
    with col2:
        st.markdown("### 🔍 The Glass Box")
        st.caption("Notice how your input gets 'cleaned' before the query builds.")
        st.code(query, language="sql")

    if login:
        try:
            c.execute(query)
            if c.fetchone():
                st.balloons()
                st.success("🏆 MASTER HACKER! You beat the filter.")
            else:
                st.error("❌ Access Denied")
        except Exception as e:
            st.warning(f"⚠️ SQL Error: {e}")