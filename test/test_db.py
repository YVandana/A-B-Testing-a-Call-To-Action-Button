# check_db.py
import sqlite3
import os

# Absolute path based on this script's location
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'experiment.db')

print(f"Database: {DB_PATH}")
print(f"Exists: {os.path.exists(DB_PATH)}")
print(f"Size: {os.path.getsize(DB_PATH)} bytes")

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

c.execute("SELECT COUNT(*) FROM events")
total = c.fetchone()[0]

c.execute("SELECT event_type, COUNT(*) FROM events GROUP BY event_type")
counts = c.fetchall()

c.execute("SELECT variant, COUNT(*) FROM events WHERE event_type='view' GROUP BY variant")
variants = c.fetchall()

c.execute("SELECT variant, COUNT(*) FROM events WHERE event_type='click' GROUP BY variant")
clicks = c.fetchall()

print(f"\n Total events: {total}")
for event_type, count in counts:
    print(f"   {event_type}: {count}")

print(f"\n Views by variant:")
for variant, count in variants:
    print(f"   {variant}: {count}")

print(f"\n Clicks by variant:")
for variant, count in clicks:
    print(f"   {variant}: {count}")

# Calculate conversion rates
if variants and clicks:
    variant_dict = {v: c for v, c in variants}
    click_dict = {v: c for v, c in clicks}
    print(f"\n Conversion Rates:")
    for variant in ['control', 'treatment']:
        views = variant_dict.get(variant, 0)
        cl = click_dict.get(variant, 0)
        rate = cl/views*100 if views > 0 else 0
        print(f"   {variant}: {rate:.2f}% ({cl}/{views})")

conn.close()