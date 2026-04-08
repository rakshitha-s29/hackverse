import sqlite3
import json
import os
from agents.state import TravelState

def save_itinerary_to_db(state: TravelState):
    """
    Elite Agent Node: Persistence
    Saves the final itinerary to the database (SingleStore/SQLite).
    """
    dest = state.get("destination")
    source = state.get("source")
    days = state.get("duration")
    markup = state.get("itinerary_markup")
    
    if not markup:
        state["reasoning"] = "I couldn't find an itinerary to save. Let's create one first!"
        return state

    try:
        # Using SQLite as the local simulator for SingleStore
        conn = sqlite3.connect("voyage_veda.db")
        cursor = conn.cursor()
        
        # Ensure table exists (redundancy check)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS itineraries (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                username TEXT,
                destination TEXT,
                source_location TEXT,
                days INTEGER,
                markup_content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            INSERT INTO itineraries (username, destination, source_location, days, markup_content)
            VALUES (?, ?, ?, ?, ?)
        """, ("Voyager", dest, source, days, markup))
        
        conn.commit()
        conn.close()
        
        state["itinerary_markup"] = f"<div class='success-banner'>✅ Itinerary for {dest} has been saved to your profile! You can access it anytime.</div>" + markup
        state["reasoning"] = f"Successfully saved the {dest} trip to the database."
        
    except Exception as e:
        print(f"DATABASE ERROR: {e}")
        state["itinerary_markup"] = f"<div class='error-banner'>❌ Sorry, I encountered a database glitch while saving. Please try again!</div>" + markup

    # After saving, we finish
    return {
        "task_plan": [],
        "ready_to_save": True
    }
