import os
from agents.state import TravelState
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

try:
    from langchain_community.tools import DuckDuckGoSearchRun
    search = DuckDuckGoSearchRun()
except ImportError:
    search = None

def live_search(state: TravelState):
    dest = state.get("destination")
    interest = state.get("preferences")[0] if state.get("preferences") else "travel destinations"
    days = state.get("duration") or 3
    
    # Autonomous behavior: If no destination, search for recommendations!
    is_discovering = dest is None
    
    try:
        llm = ChatOpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url=os.getenv("GROQ_BASE_URL"),
            model=os.getenv("GROQ_MODEL"),
            temperature=0.4
        )
        
        if is_discovering:
            query = f"Best {interest} travel destinations for a {days} day trip"
        else:
            query_prompt = ChatPromptTemplate.from_template(
                "Generate a concise search query to find the best {interest} spots in {dest} for a {days} day trip."
            )
            query_chain = query_prompt | llm
            query = query_chain.invoke({"interest": interest, "dest": dest, "days": days}).content.strip().strip('"')
            
    except Exception as e:
        query = f"{interest} spots in {dest or 'India'}"

    try:
        if search:
            print(f"DEBUG SEARCH: Finding '{query}'")
            results = search.run(query)
            
            summary_prompt = ChatPromptTemplate.from_template(
                "Summarize these search results for a traveler interested in {interest}. "
                "Context: {context}. Results: {results}. "
                "If multiple destinations are found, list the top 3 as suggestions."
            )
            summary_chain = summary_prompt | llm
            summary = summary_chain.invoke({
                "interest": interest, 
                "context": f"Destination is {dest}" if dest else "Looking for new destinations",
                "results": results
            }).content
            
            state["search_summary"] = summary
            
            # If we were searching for destinations, the brain will pick one in the next turn
            if is_discovering:
                state["messages"].append(f"VoyageVeda research: I found some great options for {interest}!")
        else:
            state["search_summary"] = "Search tool offline. Suggesting popular spots."
        
        # Progress the plan
        if state.get("task_plan"):
            state["task_plan"].pop(0)

    except Exception as e:
        print(f"DEBUG: Search error: {e}")
        state["search_summary"] = "Could not reach live search services."
        
    return state
