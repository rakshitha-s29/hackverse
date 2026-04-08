import os
import json
import re
from agents.state import TravelState
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

def sanitize_value(val):
    """
    Helper to prevent LLM hallucinations like "None" or "Unknown" from entering the state.
    """
    if val is None:
        return None
    if isinstance(val, str):
        s = val.lower().strip()
        # Filter out common hallucinated placeholders
        if s in ["none", "null", "unknown", "n/a", "undefined", "anywhere", "unspecified"]:
            return None
        # Use simple regex to ensure it's not just punctuation
        if not re.search(r'[a-zA-Z0-9]', s):
            return None
    return val

def extract_intent(state: TravelState):
    """
    Agent node to orchestrate the travel planning process autonomously.
    """
    messages = state.get("messages") or []
    if not messages:
        state["next_action"] = "CLARIFY"
        return state
        
    last_message = messages[-1]
    
    llm = ChatOpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url=os.getenv("GROQ_BASE_URL"),
        model=os.getenv("GROQ_MODEL"),
        temperature=0.2
    )
    
    prompt = ChatPromptTemplate.from_template("""
    You are the VoyageVeda Elite Orchestrator, a SMART TRAVEL AGENT (not a chatbot).
    
    Current State: 
    - Source: {source}
    - Destination: {dest}
    - Duration: {duration}
    - Travel Date: {travel_date}
    - Budget: {budget}
    - Preferences: {prefs}
    
    Context:
    - Last Asked: {last_asked}
    - Recent Messages: {history}
    
    User says: "{user_msg}"
    
    AGENT RULES:
    1. ALWAYS acknowledge the user naturally. 
    2. If info is missing (source, dest, duration), set task_plan = ["CLARIFY"].
    3. If all core info is ready, task_plan = ["MEMORY", "MAPS", "FLIGHTS", "HOTELS", "WEATHER", "RECOMMEND"].
    4. If the user says "Yes", "Save", "Submit" in response to saving an itinerary, set task_plan = ["SAVE"].
    
    Logic:
    - Extract from single words (e.g., if we asked 'Where to?' and they say 'Goa', set destination='Goa').
    - If APIs fail, we use elite fallback data.
    
    Return ONLY JSON:
    {{
      "thought": "Internal reasoning (Observe -> Think -> Act)",
      "reasoning": "User-friendly acknowledgement",
      "task_plan": ["TASK1", ...],
      "source": "city or null",
      "destination": "city or null",
      "duration": int or null,
      "travel_date": "date string or null",
      "budget": int or null,
      "preferences": ["string"],
      "travel_mode": "flight | car | null"
    }}
    """)
    
    try:
        # Provide the last 3 messages for context
        history = "\n".join(messages[-3:-1]) if len(messages) > 1 else "No history yet."
        
        response = llm.invoke(prompt.format(
            user_msg=last_message,
            source=state.get("source"),
            dest=state.get("destination"),
            duration=state.get("duration"),
            travel_date=state.get("travel_date"),
            budget=state.get("budget"),
            prefs=state.get("preferences"),
            last_asked=state.get("last_asked_field") or "Nothing",
            history=history
        ))
        
        content = re.sub(r'```json|```', '', response.content).strip()
        data = json.loads(content)
        
        # Apply strict sanitization
        state["thought"] = data.get("thought") or "Analyzing user intent..."
        state["reasoning"] = data.get("reasoning")
        
        # Flexibly extract integers for duration and budget
        def to_int(v):
            if v is None: return None
            try: return int(re.sub(r'[^0-9]', '', str(v)))
            except: return None

        new_source = sanitize_value(data.get("source"))
        new_dest = sanitize_value(data.get("destination"))
        new_duration = to_int(data.get("duration"))
        new_budget = to_int(data.get("budget"))
        new_prefs = data.get("preferences") if isinstance(data.get("preferences"), list) else state.get("preferences")
        new_mode = sanitize_value(data.get("travel_mode"))
        new_date = sanitize_value(data.get("travel_date"))
        
        if new_source: state["source"] = new_source
        if new_dest: state["destination"] = new_dest
        if new_duration: state["duration"] = new_duration
        if new_budget: state["budget"] = new_budget
        if new_prefs: state["preferences"] = new_prefs
        if new_mode: state["travel_mode"] = new_mode
        if new_date: state["travel_date"] = new_date
        
        # Update Task Plan from LLM
        if data.get("task_plan"):
            state["task_plan"] = [t.upper() for t in data.get("task_plan")]
        
        # Determine next action
        plan = state.get("task_plan") or []
        if not state.get("source") or not state.get("destination") or not state.get("duration") or not state.get("travel_date"):
            state["next_action"] = "CLARIFY"
            if not plan or plan[0] != "CLARIFY":
                state["task_plan"] = ["CLARIFY"]
        else:
            state["next_action"] = "SEARCH" if plan else "RECOMMEND"
            
        print(f"DEBUG BRAIN: FinalState={state.get('source')} to {state.get('destination')} | Action={state.get('next_action')} | Plan={state.get('task_plan')}")
        
    except Exception as e:
        print(f"DEBUG: Orchestration Error: {e}")
        state["next_action"] = "CLARIFY"
        
    return state

def ask_clarification(state: TravelState):
    """
    Node to politely ask for missing information in a conversational way.
    """
    source = state.get("source")
    dest = state.get("destination")
    duration = state.get("duration")
    travel_date = state.get("travel_date")
    reasoning = state.get("reasoning") or "I'm helping you plan the perfect trip."
    
    markup = f"<div class='clarification-card'><p class='reasoning-text'><i>{reasoning}</i></p>"
    
    if not source:
        state["last_asked_field"] = "source"
        markup += "<h2>Where are you starting from? 🛫</h2>"
        markup += "<div class='suggestion-pills'><span>Delhi</span>, <span>Mumbai</span>, <span>Bangalore</span></div>"
    elif not dest:
        state["last_asked_field"] = "destination"
        markup += f"<h2>Fantastic! Starting from {source}. Where to? 🌍</h2>"
        markup += "<div class='suggestion-pills'><span>Goa</span>, <span>Leh</span>, <span>Paris</span></div>"
    elif not duration:
        state["last_asked_field"] = "duration"
        markup += f"<h2>Great choice! How many days in {dest}? ⏳</h2>"
        markup += "<div class='suggestion-pills'><span>3 Days</span>, <span>5 Days</span>, <span>7 Days</span></div>"
    elif not travel_date:
        state["last_asked_field"] = "travel_date"
        markup += "<h2>When are you planning to fly? 🗓️</h2>"
        markup += "<div class='suggestion-pills'><span>Next Friday</span>, <span>May 10th</span>, <span>June 1st</span></div>"
    
    markup += "</div>"
    
    state["itinerary_markup"] = markup
    state["ready_to_save"] = False
    return state
