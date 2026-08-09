'''
Generate realistic A/B test data directly in the database.
Run this AFTER starting the Streamlit app to populate test data.
'''

import sqlite3
import uuid
import hashlib
import random
import os
from datetime import datetime, timezone, timedelta

# Use absolute path based on script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
DB_PATH = os.path.join(PROJECT_ROOT, 'data', 'experiment.db')

# Configuration
NUM_SESSIONS = 10000
TRUE_CTR = {'control': 0.10, 'treatment': 0.12}
SIMULATION_DAYS = 7

print(f'Generating {NUM_SESSIONS} sessions directly in database...')
print(f'Database: {DB_PATH}')
print(f'True rates: Control={TRUE_CTR["control"]}, Treatment={TRUE_CTR["treatment"]}')
print('-' * 50)

def assign_variant(session_id):
    '''Same deterministic assignment as Streamlit app'''
    hash_digest = hashlib.sha256(session_id.encode()).hexdigest()
    return 'treatment' if int(hash_digest[:8], 16) % 2 == 0 else 'control'

# Ensure data directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Create table if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        variant TEXT NOT NULL,
        event_type TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )
''')

# Clear old data
c.execute("DELETE FROM events")
print("Cleared old data")

# Generate sessions
control_views = control_clicks = 0
treatment_views = treatment_clicks = 0

for i in range(NUM_SESSIONS):
    session_id = str(uuid.uuid4())
    variant = assign_variant(session_id)
    
    # Random timestamp within simulation period
    seconds_ago = random.randint(0, SIMULATION_DAYS * 24 * 3600)
    view_time = (datetime.now(timezone.utc) - timedelta(seconds=seconds_ago)).isoformat()
    
    # Log view
    c.execute('INSERT INTO events (session_id, variant, event_type, timestamp) VALUES (?, ?, ?, ?)',
              (session_id, variant, 'view', view_time))
    
    if variant == 'control':
        control_views += 1
    else:
        treatment_views += 1
    
    # Determine click based on true conversion rate
    if random.random() < TRUE_CTR[variant]:
        click_delay = random.randint(1, 300)
        click_time = (datetime.fromisoformat(view_time) + timedelta(seconds=click_delay)).isoformat()
        
        c.execute('INSERT INTO events (session_id, variant, event_type, timestamp) VALUES (?, ?, ?, ?)',
                  (session_id, variant, 'click', click_time))
        
        if variant == 'control':
            control_clicks += 1
        else:
            treatment_clicks += 1
    
    if (i + 1) % 400 == 0:
        print(f'{i + 1}/{NUM_SESSIONS} sessions generated...')

conn.commit()
conn.close()

print('-' * 50)
print(f'Complete!')
print(f'   Control:   {control_views} views, {control_clicks} clicks ({control_clicks/control_views*100:.1f}%)')
print(f'   Treatment: {treatment_views} views, {treatment_clicks} clicks ({treatment_clicks/treatment_views*100:.1f}%)')
lift = (treatment_clicks/treatment_views - control_clicks/control_views) * 100
print(f'   Lift:      {lift:.1f} percentage points')
print(f'\nData saved: {DB_PATH}')
print(f'\nReady for analysis! Run: python Code/Analysis/analysis.py')