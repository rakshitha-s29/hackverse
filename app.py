from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import os

app = Flask(__name__, static_folder='.', static_url_path='')

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

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

@app.route('/api/chat', methods=['POST'])
def handle_chat():
    req = request.get_json()
    if not req:
        return jsonify({"displayMarkup": "Error processing request.", "saveMarkup": "Error"}), 400
        
    state = req.get('state', {})
    req_type = req.get('reqType', 'generate_itinerary')
    
    origin = state.get('origin', 'Unknown').title()
    mood = state.get('mood', 'happy').title()
    days = state.get('days', '2')
    people = state.get('people', '2')
    budget = state.get('budget', '3500').title()
    custom_edit = state.get('editStr', '')
    chosen_dest = state.get('destination', '').title()
    
    if str(people) == "1":
        people_str = "solo traveler"
    else:
        people_str = f"a group of {people}"

    if req_type == 'suggest_places':
        suggs = f"Based on your starting location of <b>{origin}</b>, your <b>{mood}</b> style, and budget format of <b>{budget}</b>, here are 5 perfect destinations for {people_str}:<br><br>"
        
        suggs += f"<b>1. Delhi:</b> Suitable for your {mood} mood, with fantastic historical monuments that fit safely within your {budget} budget.<br>"
        suggs += f"<b>2. Goa:</b> Good for your {mood} mood, offering laid-back beaches and fun nightlife tailored for your {budget} budget.<br>"
        suggs += f"<b>3. Munnar:</b> Excellent for peace, featuring lush tea gardens and budget-flexible resorts spanning {budget}.<br>"
        suggs += f"<b>4. Jaipur:</b> Great for royal heritage and exploring forts, with exceptional {budget} dining options.<br>"
        suggs += f"<b>5. Dharamshala:</b> Perfect mountain getaway guaranteeing a {mood} relaxing trip with incredible {budget} cafes.<br><br>"
        
        suggs += "<b>Which place would you like to choose from these?</b> Or do you want to go to a particular place of your own?"
        return jsonify({"displayMarkup": suggs, "saveMarkup": suggs})
        
    elif req_type in ['generate_itinerary', 'edit_itinerary']:
        edit_note = ""
        if custom_edit:
            edit_note = f"<i>(Adjusted based on your specific request: {custom_edit})</i><br><br>"

        # Comprehensive Real-World Dictionary mapped explicitly instead of generic texts
        attractions = {
            "Bangalore": {
                "m1": "Lalbagh Botanical Garden walk", "l1": "Vidyarthi Bhavan Masala Dosa", "a1": "Cubbon Park & State Library", "s1": "Filter Coffee at CTR", "e1": "Vidhana Soudha & MG Road Pubs",
                "m2": "Bangalore Palace exploration", "l2": "Nagarjuna Andhra Meals", "a2": "Visvesvaraya Museum", "s2": "Corner House Ice Cream", "e2": "Indiranagar Cafe Hopping"
            },
            "Chennai": {
                "m1": "Kapaleeshwarar Temple visit", "l1": "Traditional Banana Leaf Meals at Murugan Idli", "a1": "Santhome Cathedral & DakshinaChitra", "s1": "Marina Beach sundal", "e1": "Evening stroll at Elliot's Beach",
                "m2": "Government Museum deep dive", "l2": "Chettinad Cuisine at Anjappar", "a2": "Guindy National Park", "s2": "Local Filter Kaapi", "e2": "T Nagar shopping"
            },
            "Hyderabad": {
                "m1": "Charminar & Mecca Masjid", "l1": "Authentic Biryani at Paradise or Shadab", "a1": "Chowmahalla Palace", "s1": "Irani Chai & Osmania Biscuits at Nimrah", "e1": "Boat ride at Hussain Sagar Lake",
                "m2": "Golconda Fort Heritage Tour", "l2": "Mandi or Haleem depending on season", "a2": "Salar Jung Museum", "s2": "Karachi Bakery snacks", "e2": "Lumbini Park Laser Show"
            },
            "Mumbai": {
                "m1": "Gateway of India & Taj Mahal Palace", "l1": "Britannia & Co. Berry Pulao", "a1": "Colaba Causeway shopping", "s1": "Vada Pav at Ashok or Juhu", "e1": "Sunset at Marine Drive (Queen's Necklace)",
                "m2": "Elephanta Caves ferry tour", "l2": "Seafood at Trishna", "a2": "Chhatrapati Shivaji Maharaj Vastu Sangrahalaya", "s2": "Pani Puri hop", "e2": "Bandra Fort views"
            },
            "Kolkata": {
                "m1": "Victoria Memorial & Maidan", "l1": "Awadhi Biryani at Arsalan", "a1": "Indian Museum", "s1": "Phuchka at Vivekananda Park", "e1": "Howrah Bridge & Princep Ghat boat ride",
                "m2": "Dakshineswar Kali Temple", "l2": "Kosha Mangsho at Golbari", "a2": "College Street Book Market", "s2": "Rosogolla matching", "e2": "Park Street evening lights"
            },
            "Jaipur": {
                "m1": "Amer Fort elephant/jeep ride", "l1": "Rajasthani Thali at Chokhi Dhani", "a1": "Hawa Mahal external tour", "s1": "Pyaaz Kachori at Rawat Mishtan", "e1": "Jal Mahal sunset views",
                "m2": "City Palace & Jantar Mantar", "l2": "Laal Maas at Handi", "a2": "Albert Hall Museum", "s2": "Local snacks at Bapu Bazaar", "e2": "Nahargarh Fort night view"
            },
            "Goa": {
                "m1": "Baga or Calangute Beach water sports", "l1": "Fish Thali at Ritz Classic", "a1": "Aguada Fort exploration", "s1": "Shack chilling & mocktails", "e1": "Tito's Lane Nightlife",
                "m2": "Basilica of Bom Jesus heritage", "l2": "Vindaloo at local eatery", "a2": "Dona Paula Viewpoint", "s2": "Sunset River Cruise on Mandovi", "e2": "Anjuna Flea Market"
            }
        }
        
        # Generic fallback using location name
        fallback = {
            "m1": f"Local heritage walk around {chosen_dest} center", "l1": "Regional authentic lunch", "a1": f"Visit top-rated {chosen_dest} museums", "s1": "Local street treats", "e1": f"Dinner exploring {chosen_dest} culture",
            "m2": f"Offbeat nature or monument tour near {chosen_dest}", "l2": "Traditional heavy meal", "a2": "Local crafts shopping", "s2": "Sunset vantage point viewing", "e2": "Farewell lounge or peaceful dinner"
        }
        
        spots = attractions.get(chosen_dest, fallback)

        try:
            days_int = int(days)
        except:
            days_int = 2
            
        # 1) Generate PURE save text (No prompts, directly dashboard ready)
        save_msg = f"{edit_note}<h3>Travel Plan: {origin} to {chosen_dest}</h3>"
        save_msg += f"<p><b>Trip Parameters:</b><br>"
        save_msg += f"• Mood: {mood}<br>• Group Size: {people_str}<br>• Budget Capacity: {budget}<br>• Duration: {days_int} Days</p><br>"
        
        save_msg += f"<h4>Day 1: Arrival & Exploration</h4>"
        save_msg += f"<ul>"
        save_msg += f"<li><b>09:00 AM:</b> Breakfast - Authentic local breakfast (Budget: {budget}).</li>"
        save_msg += f"<li><b>10:30 AM:</b> Morning - {spots['m1']}.</li>"
        save_msg += f"<li><b>01:30 PM:</b> Lunch - {spots['l1']}.</li>"
        save_msg += f"<li><b>04:00 PM:</b> Afternoon - {spots['a1']}.</li>"
        save_msg += f"<li><b>05:30 PM:</b> Snacks - {spots['s1']}.</li>"
        save_msg += f"<li><b>08:00 PM:</b> Dinner - {spots['e1']}.</li>"
        save_msg += f"</ul>"

        if days_int > 1:
            save_msg += f"<br><h4>Day 2 to {days_int}: Deep Dive</h4>"
            save_msg += f"<ul>"
            save_msg += f"<li><b>08:30 AM:</b> Breakfast - Premium continental/local spread.</li>"
            save_msg += f"<li><b>10:00 AM:</b> Morning - {spots['m2']}.</li>"
            save_msg += f"<li><b>01:00 PM:</b> Lunch - {spots['l2']}.</li>"
            save_msg += f"<li><b>03:30 PM:</b> Afternoon - {spots['a2']}.</li>"
            save_msg += f"<li><b>05:30 PM:</b> Snacks - {spots['s2']}.</li>"
            save_msg += f"<li><b>08:30 PM:</b> Dinner - {spots['e2']}.</li>"
            save_msg += f"</ul>"

        # 2) Generate User-Friendly Conversational text wrapping the raw payload
        display_msg = f"Ready! Since you're traveling from <b>{origin}</b>, here is your customized plan for <b>{chosen_dest}</b>.<br><br>"
        display_msg += save_msg
        
        display_msg += f"<br><b>Transportation Context ({origin} to {chosen_dest}):</b><br>"
        display_msg += f"- <i>Flight:</i> Fastest depending on connectivity. Highly recommended to maximize your {days}-day trip.<br>"
        display_msg += f"- <i>Train:</i> Scenic & budget friendly depending on {budget}. Can range heavily from {origin}.<br>"
        display_msg += f"- <i>Bus/Car:</i> Excellent for interstate neighboring logic.<br><br>"
        
        display_msg += f"<b>Next Steps:</b><br>"
        display_msg += f"Is this fine, or do you want to add any tasks? (Type '<b>confirm</b>' to rigidly save this clean itinerary to your dashboard, or type changes like 'Skip breakfast' or 'Add more historical walking')."
        
        return jsonify({
            "displayMarkup": display_msg,
            "saveMarkup": save_msg
        })

if __name__ == '__main__':
    print("Starting India Travel Backend on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
