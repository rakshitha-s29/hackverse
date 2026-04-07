from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
import sqlite3

app = Flask(__name__, static_folder='.', static_url_path='')
DATABASE = 'users.db'

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
    
    # 1. NLP EXTRACTION
    text_lower = text.lower()
    
    # Match budget
    
    clean_text = text_lower.replace(',', '').replace('k', '000')
    budget_match = re.search(r'(\d{3,})', clean_text)

    if budget_match:
        val = budget_match.group(1).replace(',', '')
        state['budget'] = int(val)
        
    # Match days
    days_match = re.search(r'(\d+)\s*day', text_lower)
    days_match = re.search(r'(\d+)\s*day', text_lower)
    if not days_match:
        # Check if they just wrote a number below 30 without saying 'days'
        # if and only if we already asked for days
        lone_num = re.search(r'^(\d{1,2})$', text_lower.strip())
        if lone_num:
            days_match = lone_num

    if days_match:
        state['days'] = int(days_match.group(1))
    elif 'weekend' in text_lower:
        state['days'] = 2
        
    # Match interest
    interests = ['beach', 'nature', 'mountain', 'hill', 'cultural', 'historic', 'party', 'adventure']
    for i in interests:
        if i in text_lower:
            state['interest'] = i
            break
            
    # Match explicit destination
    destinations = ['goa', 'mysore', 'delhi', 'coorg', 'munnar', 'jaipur', 'dharamshala', 'bangalore', 'chennai', 'mumbai', 'kolkata']
    dest_match = re.search(r'to\s+([a-zA-Z]+)', text_lower)
    if dest_match and dest_match.group(1) in destinations:
        state['destination'] = dest_match.group(1).title()
    else:
        for d in destinations:
            if d in text_lower:
                state['destination'] = d.title()
                break

    # Increase budget hook
    if 'increase budget' in text_lower or 'add budget' in text_lower:
        num = re.search(r'by\s+(\d+)', text_lower)
        if num and state.get('budget'):
            state['budget'] += int(num.group(1))
        elif state.get('budget'):
            state['budget'] += 2000 # default increase
            
    # Add day hook
    if 'add one more day' in text_lower or 'add a day' in text_lower:
        if state.get('days'):
            state['days'] += 1

    # Decrease budget hook
    if 'make it cheaper' in text_lower or 'reduce budget' in text_lower or 'lower budget' in text_lower:
        if state.get('budget'):
            state['budget'] = int(state['budget'] * 0.8) # Reduce by 20%
            
    # Add adventure hook
    if 'add adventure' in text_lower or 'more adventurous' in text_lower:
        state['interest'] = 'adventure'


    # 2. INTENT & FALLBACK HANDLING
    if not state.get('budget') and not state.get('days'):
        return jsonify({
            "displayMarkup": "Hello there! I am your personal GuideGeek-style AI Travel Expert ✨! I am super excited to help you plan. To get started, could you let me know your **budget** and roughly **how many days** you are planning?",
            "newState": state
        })
    elif not state.get('budget'):
        return jsonify({
            "displayMarkup": f"A {state.get('days')}-day trip sounds absolutely fantastic! I am thrilled to help you design it. What is your **budget** for this trip? What's your **budget** for this trip?",
            "newState": state
        })
    elif not state.get('days'):
        return jsonify({
            "displayMarkup": f"Perfect! With a healthy budget of ₹{state.get('budget')}, we can do a lot. Roughly how many **days** are you planning to travel?",
            "newState": state
        })

    # 3. DECISION ENGINE
    if not state.get('destination'):
        budget = state.get('budget', 5000)
        days = state.get('days', 2)
        interest = state.get('interest', 'general')
        
        if interest == 'beach':
            state['destination'] = 'Goa' if budget >= 5000 else 'Gokarna'
        elif interest in ['nature', 'mountain', 'hill']:
            state['destination'] = 'Munnar' if days > 2 else 'Coorg'
        elif interest == 'cultural':
            state['destination'] = 'Jaipur' if budget > 8000 else 'Mysore'
        else:
            state['destination'] = 'Mysore' # default fallback
            
    dest = state['destination']
    days = state['days']
    budget = state['budget']
    interest = state.get('interest', 'leisure')

    # 4. BUDGET SPLIT
    t_split = int(budget * 0.25)
    s_split = int(budget * 0.40)
    f_split = int(budget * 0.35)
    
    improvement = ""

    eco_reason = "Medium (Standard travel footprint)."
    if interest in ['nature', 'mountain'] or budget < 10000:
        eco_reason = "High 🌱 (Prioritizing local transport, homestays, and natural exploration deeply minimizes your footprint!)"
        improvement += "<br><i>🌱 Eco-Tip: Carry a reusable water bottle and support local artisans to maximize your eco-score!</i>"
    elif budget > 20000:
        eco_reason = "Moderate (Premium travel usually involves flights)."
        improvement += "<br><i>🌱 Eco-Tip: Select eco-certified luxury resorts to offset carbon emissions!</i>"

    if budget < 5000:
        improvement = "<i>💡 Tip: Consider taking a sleeper bus and staying in local hostels to easily meet this budget.</i>"
    elif budget > 15000:
        improvement = "<i>💡 Tip: Your budget supports premium transport. Look for fast flights and boutique hotels!</i>"

    # 5. REVIEWS & RATINGS
    reviews_db = {
        'Goa': 'Highly rated for vibrant beaches, cafes, and nightlife.',
        'Mysore': 'Famous for its deeply rich royal heritage and peaceful ambiance.',
        'Munnar': 'Stunningly peaceful and scenic hill station with endless tea gardens.',
        'Coorg': 'The Scotland of India; incredible coffee estates and misty weather.',
        'Jaipur': 'Royal architecture, imposing forts, and world-class hospitality.',
        'Delhi': 'A melting pot of centuries of history and vibrant street food.',
        'Gokarna': 'A serene, budget-friendly alternative to Goa with untouched beaches.'
    }
    rev = reviews_db.get(dest, f"A fantastic choice offering unique experiences tailored to your {interest} style.")

    # 6. ITINERARY GENERATION
    itin_html = "<ul>"
    itin_array = []
    
    # Day 1
    itin_html += f"<li><b>Day 1: Arrival & Exploration</b><br> - Arrive in {dest} and Check-in to your accommodation.<br> - Afternoon: Explore the famous local centers.<br> - Evening: Enjoy regional dinner (Budget: ₹{int(f_split/days)}).</li>"
    itin_array.append({"day": 1, "plan": "Arrival, Check-in, Local exploration, Regional dining."})
    
    # Day 2 to N
    for d in range(2, days + 1):
        if d == days:
            itin_html += f"<li><b>Day {d}: Farewell & Departure</b><br> - Morning: Last minute shopping or relaxing breakfasts.<br> - Afternoon: Proceed to terminal/station for return trip.</li>"
            itin_array.append({"day": d, "plan": "Farewell breakfasts, relaxed morning, return trip."})
        else:
            itin_html += f"<li><b>Day {d}: Sightseeing & Deep Dive</b><br> - Morning: Visit the top historical or scenic viewpoints of {dest}.<br> - Evening: Leisure walks and local street food.</li>"
            itin_array.append({"day": d, "plan": "Main sightseeing, immersive local experiences."})
    itin_html += "</ul>"

    json_response = {
        "destination": dest,
        "itinerary": itin_array,
        "budget_split": {"travel": t_split, "stay": s_split, "food": f_split},
        "eco_score": eco_reason,
        "review": rev,
        "reason": f"Selected because it perfectly fits your {days}-day timeline and ₹{budget} budget constraints."
    }
    
    # 7. RENDER MARKUPS
    state['ready_to_save'] = True

    display_msg = f"Great choice! Based on your budget of <b>₹{budget}</b> for <b>{days} days</b>, here’s a perfect plan for you ✨<br><br>"
    display_msg += f"<h3>Trip to {dest}</h3>"
    display_msg += f"<b>Destination Review:</b> {rev}<br>"
    display_msg += f"<b>Why this location?</b> {json_response['reason']}<br><br>"
    
    display_msg += f"<b>Smart Budget Split (₹{budget}):</b><br>"
    display_msg += f"➔ Travel: ₹{t_split}<br>➔ Stay: ₹{s_split}<br>➔ Food: ₹{f_split}<br>{improvement}<br><br>"
    
    display_msg += itin_html
    
    display_msg += f"<br>Does this look perfect? (Type <b>Confirm</b> to rigidly save this itinerary to your dashboard, or say things like 'Increase budget by 2000' or 'Add one more day')."

    # Save markup (clean variant for dashboard)
    save_msg = f"<h3>Trip to {dest} ({days} Days / ₹{budget})</h3>"
    save_msg += f"<b>Review:</b> {rev}<br>"
    save_msg += f"<b>Budget:</b> Travel: ₹{t_split} | Stay: ₹{s_split} | Food: ₹{f_split}<br>"
    save_msg += itin_html

    return jsonify({
        "displayMarkup": display_msg,
        "saveMarkup": save_msg,
        "newState": state,
        "agentData": json_response
    })

if __name__ == '__main__':
    print("Starting India Travel Backend on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
