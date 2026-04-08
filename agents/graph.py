from langgraph.graph import StateGraph, END
from agents.state import TravelState
from agents.weather_agent import fetch_weather
from agents.search_agent import live_search
from agents.recommend_agent import recommend_itinerary
from agents.intent_agent import extract_intent, ask_clarification
from agents.maps_agent import search_location_details
from agents.flight_agent import search_flights
from agents.hotel_agent import search_hotels

from agents.memory_agent import retrieve_memories

from agents.save_agent import save_itinerary_to_db

def task_router(state: TravelState):
    """
    Elite Autonomous Router: Directs the agent loop.
    """
    plan = state.get("task_plan") or []
    next_action = state.get("next_action")
    
    # Priority 1: Explicit Clarification
    if next_action == "CLARIFY" or (plan and "CLARIFY" in plan[0].upper()):
        return "clarify"
        
    # Priority 2: Empty plan means recommend
    if not plan:
        return "recommend"
        
    # Priority 3: Match tasks
    current_task = plan[0].upper()
    print(f"DEBUG ROUTER: Routing to {current_task}")
    
    if "MEMORY" in current_task: return "memory"
    if "MAP" in current_task: return "maps"
    if "FLIGHT" in current_task: return "flights"
    if "HOTEL" in current_task: return "hotels"
    if "WEATHER" in current_task: return "weather"
    if "SEARCH" in current_task: return "search"
    if "SAVE" in current_task: return "save"
    
    return "recommend"

def build_graph():
    builder = StateGraph(TravelState)
    
    # Define Nodes
    builder.add_node("intent", extract_intent)
    builder.add_node("memory", retrieve_memories)
    builder.add_node("clarify", ask_clarification)
    builder.add_node("weather", fetch_weather)
    builder.add_node("search", live_search)
    builder.add_node("maps", search_location_details)
    builder.add_node("flights", search_flights)
    builder.add_node("hotels", search_hotels)
    builder.add_node("recommend", recommend_itinerary)
    builder.add_node("save", save_itinerary_to_db)
    
    # Build Graph Logic
    builder.set_entry_point("intent")
    
    builder.add_conditional_edges(
        "intent",
        task_router,
        {
            "clarify": "clarify",
            "memory": "memory",
            "maps": "maps",
            "flights": "flights",
            "hotels": "hotels",
            "weather": "weather",
            "search": "search",
            "save": "save",
            "recommend": "recommend"
        }
    )
    
    tool_targets = {
        "memory": "memory", "maps": "maps", "flights": "flights", 
        "hotels": "hotels", "weather": "weather", "search": "search", 
        "save": "save", "recommend": "recommend"
    }
    
    builder.add_conditional_edges("memory", task_router, tool_targets)
    builder.add_conditional_edges("maps", task_router, tool_targets)
    builder.add_conditional_edges("flights", task_router, tool_targets)
    builder.add_conditional_edges("hotels", task_router, tool_targets)
    builder.add_conditional_edges("weather", task_router, tool_targets)
    builder.add_conditional_edges("search", task_router, tool_targets)
    
    # Termination points
    builder.add_edge("clarify", END)
    builder.add_edge("recommend", END)
    builder.add_edge("save", END)
    
    return builder.compile()
