import os
import json
import re
from agents.state import TravelState
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

def search_flights(state: TravelState):
    """
    Elite Agent Node: Live Flight Search
    Uses DuckDuckGo and LLM to find and extract real-time flight prices.
    """
    source = state.get("source")
    dest = state.get("destination")
    date = state.get("travel_date") or "nearest available date"
    
    if not source or not dest:
        return state

    print(f"DEBUG FLIGHTS: Performing live research for {source} to {dest} on {date}")
    
    try:
        # 1. Perform Web Search
        search = DuckDuckGoSearchRun()
        query = f"cheapest flights from {source} to {dest} on {date} India price"
        search_results = search.run(query)
        
        # 2. Extract Structured Data using LLM
        llm = ChatOpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url=os.getenv("GROQ_BASE_URL"),
            model=os.getenv("GROQ_MODEL"),
            temperature=0
        )
        
        prompt = ChatPromptTemplate.from_template("""
        Extract flight options from these search results for {source} to {dest} on {date}.
        Search Results: {results}
        
        Return ONLY a JSON list of objects:
        [{{ "airline": "string", "flight_no": "string or 'TBD'", "price": "₹XXXX", "duration": "XH XM", "status": "short insight" }}]
        
        If no clear info found, return NO JSON, just an empty list [].
        Limit to top 3 cheapest or best options.
        """)
        
        chain = prompt | llm
        response = chain.invoke({"source": source, "dest": dest, "date": date, "results": search_results})
        
        # Parse JSON
        content = re.sub(r'```json|```', '', response.content).strip()
        flights_found = json.loads(content)
        
        # Fallback if LLM failed or found nothing
        if not flights_found:
            raise Exception("No specific flights extracted from search.")
            
        print(f"DEBUG FLIGHTS: Extracted {len(flights_found)} live flight options.")
        
    except Exception as e:
        print(f"DEBUG FLIGHTS: Real-time search failed/limited ({e}). Using Elite Fallbacks.")
        # Elite Fallback Data (Safety Net)
        flights_found = [
            {"airline": "IndiGo", "flight_no": "6E-504", "price": "₹4,800", "duration": "2h 10m", "status": f"Typical Value (Live unavailable)"},
            {"airline": "Air India", "flight_no": "AI-102", "price": "₹5,400", "duration": "2h 15m", "status": f"Market Rate (Live unavailable)"}
        ]
    
    return {
        "task_plan": state["task_plan"][1:] if state.get("task_plan") else [],
        "flight_results": flights_found
    }
