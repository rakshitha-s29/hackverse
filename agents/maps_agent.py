import os
from agents.state import TravelState

def search_location_details(state: TravelState):
    """
    Elite Agent Node: Maps and Location Reasoning
    Evaluates geographical context and routes.
    """
    source = state.get("source")
    dest = state.get("destination")
    
    if not source or not dest:
        state["map_results"] = {"error": "Insufficient location data for mapping."}
        return state

    print(f"DEBUG MAPS: Calculating context between {source} and {dest}")
    
    # Simulation of Maps API (Google/Mapbox)
    # In a real-world hackathon, use 'googlemaps' python library
    distance_km = 650 # Mock value
    travel_time = "8h 30m"
    
    results = {
        "distance": f"{distance_km} km",
        "travel_time_drive": travel_time,
        "source": source,
        "destination": dest,
        "route_summary": f"Direct route via major highways from {source} to {dest}."
    }
    
    return {
        "task_plan": state["task_plan"][1:] if state.get("task_plan") else [],
        "map_results": results
    }
