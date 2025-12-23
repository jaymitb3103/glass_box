import streamlit as st
import sqlite3

# --- 1. SETUP THE VULNERABLE DATABASE (In-Memory) ---
# We create a fresh DB every time the script runs (Sandbox Mode)
conn = sqlite3.connect(':memory:')
c = conn.cursor()

# Create a users table
c.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        password TEXT,
        role TEXT
    )
''')

# Insert a "Target" User
c.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'super_secret_pass', 'administrator')")
c.execute("INSERT INTO users (username, password, role) VALUES ('alice', 'alice123', 'user')")
conn.commit()

# --- 2. THE APP INTERFACE ---
st.set_page_config(page_title="The Glass Box: SQLi Lab", page_icon="🛡️")

st.title("🛡️ The Glass Box")
st.subheader("Level 1: The Login Bypass")
st.markdown("""
**Mission:** Log in as the `admin` *without* knowing the password.
<br>
**Hint:** Look at the 'Glass Box' below. Can you trick the database into thinking the password check is True?
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    username_input = st.text_input("Username", value="admin")
    password_input = st.text_input("Password", type="password")
    login_btn = st.button("Attempt Login")

# --- 3. THE GLASS BOX (Visualizing the Vulnerability) ---
# This is the "Unsafe" way to write SQL (String Concatenation)
# We show this to the user so they can learn.
sql_query_string = f"SELECT * FROM users WHERE username = '{username_input}' AND password = '{password_input}'"

with col2:
    st.markdown("### 🔍 The Glass Box (Backend View)")
    st.markdown("This is the exact command the database receives:")
    
    # We use a code block to show the query clearly
    st.code(sql_query_string, language="sql")
    
    st.info("👆 Watch how this query changes as you type in the boxes.")

st.divider()

# --- 4. EXECUTION ENGINE ---
if login_btn:
    try:
        # DANGER: We are executing the raw string directly!
        # This is what allows the hack to work.
        c.execute(sql_query_string)
        user = c.fetchone()
        
        if user:
            # SUCCESS
            user_id, name, pwd, role = user
            st.success(f"🔓 ACCESS GRANTED! Welcome, {name}.")
            st.balloons()
            
            st.write("---")
            st.markdown(f"**You dumped the database row:**")
            st.json({"id": user_id, "username": name, "role": role})
            
            if role == 'administrator':
                st.success("🏆 YOU WIN! You stole the Admin session.")
        else:
            # FAILURE
            st.error("🚫 ACCESS DENIED. Invalid credentials.")
            
    except sqlite3.OperationalError as e:
        # SYNTAX ERROR (Happens if the user types a broken hack)
        st.warning("⚠️ SQL SYNTAX ERROR")
        st.error(f"The database crashed: {e}")
        st.write("This means you 'broke' the query structure. You are close!")

conn.close()