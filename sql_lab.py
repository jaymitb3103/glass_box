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
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    else:
        # Level 2: The "Bad" Filter
        clean_user = username.replace("OR", "").replace("--", "").replace("or", "")
        query = f"SELECT * FROM users WHERE username = '{clean_user}' AND password = '{password}'"

    with col2:
        st.markdown("### 🔍 The Glass Box")
        st.code(query, language="sql")
        
        if level == "Level 2: Login Bypass (Blacklist)":
            st.caption("Filter active: Removing 'OR', 'or', '--'")

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


# --- LEVEL 3 LOGIC (Data Extraction) ---
elif level == "Level 3: The Data Heist (UNION)":
    st.subheader("Level 3: The Data Heist")
    st.markdown("""
    **Mission:** This is a User Search page.
    There is a hidden table called `credit_cards` (Columns: `owner`, `cc_number`).
    **Goal:** Trick the search box into displaying the Credit Card numbers.
    """)

    col1, col2 = st.columns(2)
    with col1:
        # Search Box
        search_input = st.text_input("Search for a User:", value="alice")
        search_btn = st.button("Search")

    # The Vulnerable Search Query
    # It selects 2 columns: username, role
    query = f"SELECT username, role FROM users WHERE username LIKE '%{search_input}%'"

    with col2:
        st.markdown("### 🔍 The Glass Box")
        st.markdown("The query expects **2 columns** (Username, Role).")
        st.code(query, language="sql")

    if search_btn:
        st.divider()
        st.subheader("🖥️ Search Results")
        try:
            c.execute(query)
            results = c.fetchall()
            
            if results:
                for row in results:
                    st.write(f"Found: **{row[0]}** | Role: {row[1]}")
                    
                    # DETECT IF USER STOLE THE CREDIT CARDS
                    if "4444" in str(row) or "1111" in str(row):
                        st.balloons()
                        st.success("💰 JACKPOT! You successfully dumped the Credit Card table.")
            else:
                st.warning("No users found.")
                
        except Exception as e:
            st.error(f"⚠️ Database Error: {e}")
            st.info("Hint: Your UNION statement must have the SAME number of columns as the original query (2).")