import streamlit as st
import sqlite3
import uuid
import random
import hashlib
import os
from datetime import datetime, timezone

# Setting Database path 
'''
The database is logging all the clicks every time a button is clicked
'''
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) # Code/app
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR)) # Goes up 2 levels to project root
DB_PATH = os.path.join(PROJECT_ROOT, 'data', 'experiment.db')

os.makedirs(os.path.dirname(DB_PATH), exist_ok = True)


# Setting up the database

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            variant TEXT NOT NULL,
            event_type TEXT NOT NULL, -- 'view' or 'click'
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def log_event(session_id, variant, event_type):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO events (session_id, variant, event_type, timestamp) VALUES (?, ?, ?, ?)',
              (session_id, variant, event_type, datetime.now(timezone.utc).isoformat()))
    
    conn.commit()
    conn.close()

# Assiging Variant & Session

def assign_variant(session_id):
    ''' Random assignment based on session_id'''
    hash_digest = hashlib.sha256(session_id.encode()).hexdigest()
    
    return 'treatment' if int(hash_digest[:8], 16) % 2 == 0 else 'control'

# Initialising the Database
init_db()

# Creating session_id (Per Browser Tab, persists across reruns)
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.variant = assign_variant(st.session_state.session_id)
    st.session_state.view_logged = False
    st.session_state.clicked = False

# Log page view only once per session
if not st.session_state.view_logged:
    log_event(st.session_state.session_id, st.session_state.variant, 'view')
    st.session_state.view_logged = True

# App UI

st.set_page_config(page_title = 'DuckIO', page_icon = '🦆')
st.title('Discover Our Products')
st.write('Sign up Today and get our Weekly Newsletter with Free Patterns & Tips& Tricks!')

variant = st.session_state.variant
if variant == 'control':
    button_label = 'Start First Free Month'
    button_color = 'LightSeaGreen'
else:
    button_label = 'Join The Community!'
    button_color = 'plum'

# Custom button Style (CSS)
st.markdown(f'''
    <style>
    .stButton > button {{
        background-color: {button_color};
        color: lemonchiffon;
        font-size: 20px;
        padding: 10px 24px;
        border-radius: 8px;
        border: none;
    }}
    </style>
    ''', unsafe_allow_html = True)

# Button Click Handling
if st.button(button_label):
    if not st.session_state.clicked:
        log_event(st.session_state.session_id, variant, 'click')
        st.session_state.clicked = True
    st.success('Thank You For Joining the Community!! 🧶')
else:
    st.info('👆🏽Click the button above to join!')


# Module to simulate browser visits randomly
if st.query_params.get('simulate_click') == 'true':
    if not st.session_state.clicked:
        log_event(st.session_state.session_id, st.session_state.variant, 'click')
        st.session_state.clicked = True
    st.write('Simulated click logged')
    st.stop()