import os
from agents.state import TravelState

def search_hotels(state: TravelState):
    """
    Elite Agent Node: Hotel Discovery
    """
    dest = state.get("destination")
    
    if not dest:
        return state

    print(f"DEBUG HOTELS: Investigating accommodations in {dest}")
    
    results = [
        {"name": f"Elite {dest} Stay", "rating": "5★", "price_per_night": "₹3,000", "type": "Mid-range"},
        {"name": f"{dest} Budget Inn", "rating": "3★", "price_per_night": "₹1,500", "type": "Budget"},
        {"name": "Luxury Residency", "rating": "5★", "price_per_night": "₹6,000", "type": "Luxury"}
    ]
    
    print(f"DEBUG HOTELS: Providing {len(results)} elite options.")
    return {
        "task_plan": state["task_plan"][1:] if state.get("task_plan") else [],
        "hotel_results": results
    }
