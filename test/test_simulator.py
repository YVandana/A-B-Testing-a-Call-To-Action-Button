# test_simulator.py - Quick test to verify connection
import requests

BASE_URL = 'http://localhost:8501'

print(f"Testing connection to {BASE_URL}...")

try:
    # Test 1: Basic connection
    response = requests.get(BASE_URL, timeout=5)
    print(f"Status code: {response.status_code}")
    print(f"Response length: {len(response.text)} characters")
    
    # Test 2: Simulate click
    click_response = requests.get(f'{BASE_URL}?simulate_click=true', timeout=5)
    print(f"Click response: {click_response.status_code}")
    
except requests.exceptions.ConnectionError:
    print(f"Cannot connect to {BASE_URL}")
    print("Is Streamlit running?")
    print("Run: streamlit run Code/app/experiment_app.py")
except Exception as e:
    print(f"Error: {e}")