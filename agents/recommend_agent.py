import os
import json
from agents.state import TravelState
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

def recommend_itinerary(state: TravelState):
    dest = state.get("destination") or "Unknown Destination"
    days = state.get("duration") or 3
    source = state.get("source") or "your location"
    weather = state.get("weather") or "No weather data available."
    summary = state.get("search_summary") or "No search results available."
    interest = ", ".join(state.get("preferences")) if state.get("preferences") else "general sightseeing"
    
    # Initialize Groq LLM
    try:
        llm = ChatOpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url=os.getenv("GROQ_BASE_URL"),
            model=os.getenv("GROQ_MODEL"),
            temperature=0.7
        )
        
        prompt = ChatPromptTemplate.from_template("""
        You are VoyageVeda, a premium AI travel agent.
        Create a beautiful, detailed travel itinerary for {dest} for {days} days, starting from {source}.
        User interests: {interest}
        Current weather: {weather}
        Live research data: {summary}
        
        Flights Found: {flights}
        Hotels Found: {hotels}
        
        Format the response in HTML. 
        - Use <h2> for the title.
        - Use <div class='weather-badge'> for weather info.
        - Use <ul> and <li> for the daily plan.
        - Style specific flight/hotel info clearly.
        - ALWAYS end with a small section: "<p class='save-prompt'><b>Do you want me to save this itinerary for later? 📌</b> (Just say 'Yes' or 'Save it')</p>"
        """)
        
        flights = json.dumps(state.get("flight_results") or [], indent=2)
        hotels = json.dumps(state.get("hotel_results") or [], indent=2)
        
        chain = prompt | llm
        response = chain.invoke({
            "dest": dest,
            "source": source,
            "days": days,
            "weather": weather,
            "summary": summary,
            "interest": interest,
            "flights": flights,
            "hotels": hotels
        })
        
        markup = response.content
        
    except Exception as e:
        print(f"DEBUG: Recommendation Error: {e}")
        markup = f"<h2>VoyageVeda: Your {dest} Itinerary</h2>"
        markup += f"<p>Exploring {dest} for {days} days. Starting from {source}.</p>"
        markup += "<ul><li>Day 1: Arrival and local discovery.</li></ul>"

    state["itinerary_markup"] = markup
    state["ready_to_save"] = True
    return state
