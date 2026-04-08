from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
import sqlite3
from dotenv import load_dotenv
from agents.graph import build_graph
from agents.state import TravelState

load_dotenv()

app = Flask(__name__, static_folder='.', static_url_path='')
DATABASE = 'users.db'

# Initialize the VoyageVeda Graph
workflow = build_graph()

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            age INTEGER,
            mobile TEXT UNIQUE NOT NULL,
            interests TEXT DEFAULT ''
        )
    ''')
    # Migration for existing users table
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN interests TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass # Column already exists
    conn.commit()
    conn.close()

# Initialize DB on startup
init_db()

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

# Authentication Routes
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    age = data.get('age')
    mobile = data.get('mobile')

    if not all([username, email, password, mobile]):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check username
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    if cursor.fetchone():
        conn.close()
        return jsonify({"error": "Username already exists. Please choose another name."}), 409

    # Check mobile
    cursor.execute('SELECT id FROM users WHERE mobile = ?', (mobile,))
    if cursor.fetchone():
        conn.close()
        return jsonify({"error": "Mobile number already registered."}), 409

    # Hash password and save
    hashed_pw = generate_password_hash(password)
    try:
        cursor.execute('''
            INSERT INTO users (username, email, password, age, mobile)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, email, hashed_pw, age, mobile))
        conn.commit()
        return jsonify({"message": "Signup successful", "user": {"username": username, "email": email}})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    identifier = data.get('identifier') # username or email
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check by username or email
    cursor.execute('SELECT * FROM users WHERE username = ? OR email = ?', (identifier, identifier))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user['password'], password):
        return jsonify({
            "message": "Login successful",
            "user": {
                "username": user['username'],
                "email": user['email'],
                "mobile": user['mobile']
            }
        })
    else:
        return jsonify({"error": "Invalid username or password."}), 401


@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)


@app.route('/mood/<mood_name>')
def serve_mood(mood_name):
    return send_from_directory('.', 'mood.html')

@app.route('/city/<city_name>')
def serve_city(city_name):
    return send_from_directory('.', 'city.html')

@app.route('/itinerary')
def serve_itinerary():
    return send_from_directory('.', 'itinerary.html')

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

def load_data():
    file_path = os.path.join(os.path.dirname(__file__), 'data.json')
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

@app.route('/api/data', methods=['GET'])
def get_data():
    data = load_data()
    if data:
        return jsonify(data)
    return jsonify({"error": "Failed to load database"}), 500

@app.route('/api/user/update_interests', methods=['POST'])
def update_interests():
    data = request.json
    username = data.get('username')
    new_interests = data.get('interests', []) # List of strings like ['beach', 'trekking']
    
    if not username:
        return jsonify({"error": "Username required"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get existing interests
    cursor.execute('SELECT interests FROM users WHERE username = ?', (username,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "User not found"}), 404
        
    existing = row['interests'] or ""
    existing_list = [i.strip() for i in existing.split(',') if i.strip()]
    
    # Merge and unique
    combined = list(set(existing_list + new_interests))
    updated_str = ",".join(combined)
    
    cursor.execute('UPDATE users SET interests = ? WHERE username = ?', (updated_str, username))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Interests updated", "interests": combined})

@app.route('/api/user/recommendations', methods=['GET'])
def get_recommendations():
    username = request.args.get('username')
    if not username:
        return jsonify({"error": "Username required"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT interests FROM users WHERE username = ?', (username,))
    row = cursor.fetchone()
    conn.close()
    
    if not row or not row['interests']:
        return jsonify({"recommendations": []})
        
    user_interests = [i.strip().lower() for i in row['interests'].split(',') if i.strip()]
    data = load_data()
    if not data:
        return jsonify({"recommendations": []})
        
    results = []
    cities = data.get('cities', {})
    
    # Simple matching logic: if any keyword from user interests is in city description or title
    for city_id, city_info in cities.items():
        desc = city_info.get('description', '').lower()
        title = city_info.get('title', '').lower()
        
        match_score = 0
        for interest in user_interests:
            if interest in desc or interest in title:
                match_score += 1
        
        if match_score > 0:
            results.append({
                "id": city_id,
                "title": city_info['title'],
                "img": city_info['img'],
                "score": match_score
            })
            
    # Sort by score descending
    results.sort(key=lambda x: x['score'], reverse=True)
    return jsonify({"recommendations": results[:6]}) # Top 6 recommendations


import re

@app.route('/api/chat', methods=['POST'])
def handle_chat():
    req = request.get_json()
    if not req:
        return jsonify({"displayMarkup": "Error processing request.", "saveMarkup": "Error"}), 400
        
    text = req.get('text', '')
    state = req.get('state', {})
    
    # 2. Invoke VoyageVeda Agentic Graph
    try:
        inputs = {
            "messages": state.get("messages", []) + [text],
            "destination": state.get('destination'),
            "source": state.get('source'),
            "budget": state.get('budget'),
            "duration": state.get('duration'),
            "preferences": state.get('preferences'),
            "ready_to_save": False,
            "ready_to_proceed": False
        }
        
        # Run the workflow
        final_state = workflow.invoke(inputs)
        
        # Update local state from Agent results
        state.update({
            "destination": final_state.get("destination"),
            "source": final_state.get("source"),
            "budget": final_state.get("budget"),
            "duration": final_state.get("duration"),
            "preferences": final_state.get("preferences"),
            "travel_mode": final_state.get("travel_mode"),
            "weather": final_state.get("weather"),
            "ready_to_save": final_state.get("ready_to_save"),
            "messages": final_state.get("messages")
        })
        
        return jsonify({
            "displayMarkup": final_state.get("itinerary_markup") or "I've processed your request. What's next?",
            "saveMarkup": final_state.get("itinerary_markup"),
            "newState": state,
            "agentData": final_state
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"Agent Error: {error_msg}")
        
        if "rate_limit_exceeded" in error_msg.lower():
            friendly_error = "My apologies! 😅 I'm getting so many travel requests right now that I need a quick 30-second breather. Could you try sending that last message again in a moment?"
        else:
            friendly_error = f"VoyageVeda encountered an unexpected glitch: {error_msg}. Let's try that again!"
            
        return jsonify({
            "displayMarkup": friendly_error,
            "newState": state
        }), 500

if __name__ == '__main__':
    print("Starting India Travel Backend on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
