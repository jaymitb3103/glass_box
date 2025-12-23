import streamlit as st
import sqlite3

# --- 1. SETUP THE DATABASE (In-Memory) ---
conn = sqlite3.connect(':memory:')
c = conn.cursor()

# Table 1: Users
c.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)')
c.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'super_secret_pass', 'administrator')")
c.execute("INSERT INTO users (username, password, role) VALUES ('alice', 'alice123', 'user')")
c.execute("INSERT INTO users (username, password, role) VALUES ('bob', 'bob456', 'user')")

# Table 2: The Hidden Loot
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
    "Level 3: The Data Heist (UNION)",
    "Level 4: The Unhackable Code (Secure)"
])

st.title("🛡️ The Glass Box")

# --- LEVEL 1 & 2 LOGIC (Login Bypass) ---
if level in ["Level 1: Login Bypass (No Filter)", "Level 2: Login Bypass (Blacklist)"]:
    # (Same login logic as before...)
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
    
    if level == "Level 1: Login Bypass (No Filter)":
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    else:
        clean_user = username.replace("OR", "").replace("--", "").replace("or", "")
        query = f"SELECT * FROM users WHERE username = '{clean_user}' AND password = '{password}'"

    with col2:
        st.markdown("### 🔍 The Glass Box")
        st.code(query, language="sql")

    if login:
        try:
            c.execute(query)
            if c.fetchone():
                st.balloons()
                st.success("🔓 ACCESS GRANTED! You are in.")
            else:
                st.error("🚫 Access Denied")
        except Exception as e:
            st.warning(f"⚠️ SQL Syntax Error: {e}")

# --- LEVEL 3: UNION ATTACK ---
elif level == "Level 3: The Data Heist (UNION)":
    # (Same Level 3 logic as before...)
    st.subheader("Level 3: The Data Heist")
    st.markdown("**Mission:** Use `UNION` to steal the credit cards.")
    col1, col2 = st.columns(2)
    with col1:
        search_input = st.text_input("Search for a User:", value="alice")
        search_btn = st.button("Search")
    query = f"SELECT username, role FROM users WHERE username LIKE '%{search_input}%'"
    with col2:
        st.markdown("### 🔍 The Glass Box (Unsafe)")
        st.code(query, language="sql")
    if search_btn:
        try:
            c.execute(query)
            results = c.fetchall()
            if results:
                for row in results:
                    st.write(f"Found: **{row[0]}** | Role: {row[1]}")
                    if "4444" in str(row) or "1111" in str(row):
                        st.balloons()
                        st.success("💰 JACKPOT! Data stolen.")
            else:
                st.warning("No users found.")
        except Exception as e:
            st.error(f"⚠️ Database Error: {e}")

# --- LEVEL 4: SECURE MODE ---
elif level == "Level 4: The Unhackable Code (Secure)":
    st.subheader("Level 4: The Patch")
    st.success("This level uses 'Parameterized Queries'. The Glass Box will show you how the database separates data from code.")
    
    col1, col2 = st.columns(2)
    with col1:
        # Same Search Box
        search_input = st.text_input("Search for a User:", value="' UNION SELECT owner, cc_number FROM credit_cards --")
        search_btn = st.button("Search (Secure)")

    # THE FIX: No F-Strings! We use ? placeholders.
    # The '%' are added to the data, not the query string.
    secure_query = "SELECT username, role FROM users WHERE username LIKE ?"
    secure_data = (f"%{search_input}%",)

    with col2:
        st.markdown("### 🔍 The Glass Box (Secure)")
        st.markdown("Notice the `?`. The database never sees your code.")
        st.code(secure_query, language="sql")
        st.markdown("**The Payload is treated as text:**")
        st.code(str(secure_data), language="python")

    if search_btn:
        st.divider()
        st.subheader("🖥️ Search Results")
        try:
            # We pass the query AND the data separately
            c.execute(secure_query, secure_data)
            results = c.fetchall()
            
            if results:
                for row in results:
                    st.write(f"Found: **{row[0]}** | Role: {row[1]}")
            else:
                # If the hack fails, it usually prints "No users found"
                # because no user is named "UNION SELECT..."
                st.info("No users found. (The attack failed!)")
                st.caption("The database looked for a user literally named: " + search_input)
                
        except Exception as e:
            st.error(f"⚠️ Database Error: {e}")