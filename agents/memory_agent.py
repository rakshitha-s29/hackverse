import os
from agents.state import TravelState

def retrieve_memories(state: TravelState):
    """
    Elite Agent Node: Vectorized Memory retrieval
    Simulates RAG from SingleStore.
    """
    username = state.get("username") or "Traveler"
    interest = state.get("interest")
    
    print(f"DEBUG MEMORY: Searching long-term context for {username}")
    
    # Mock Vector results from SingleStore
    memories = [
        f"User previously enjoyed mountain trekking in Himachal.",
        "User prefers budget-friendly hotels under ₹3000.",
        "Historical context: Goa is busiest in December."
    ]
    
    # Progress the plan
    new_plan = state["task_plan"][1:] if state.get("task_plan") else []
    
    print(f"DEBUG MEMORY: Found {len(memories)} relevant trip memories.")
    return {
        "task_plan": new_plan,
        "memory_results": memories
    }
