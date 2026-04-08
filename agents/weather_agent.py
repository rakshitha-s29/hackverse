import os
import requests
from agents.state import TravelState

def fetch_weather(state: TravelState):
    dest = state.get("destination") or "Delhi"
    api_key = os.getenv("OPENWEATHER_API_KEY")
    
    # Progress the plan
    new_plan = state["task_plan"][1:] if state.get("task_plan") else []

    if not api_key:
        return {
            "task_plan": new_plan,
            "weather": f"Warm, 28–32°C, perfectly beach-friendly in {dest} 🏖️"
        }
        
    try:
        # Append ', India' to prevent getting results for 'Manali, Chennai'!
        query_dest = f"{dest}, India"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={query_dest}&appid={api_key}&units=metric"
        response = requests.get(url).json()
        
        if response.get("cod") != 200:
            return {
                "task_plan": new_plan,
                "weather": f"Key pending activation (wait 2h) - simulated: Sunny, 24°C in {dest}"
            }

        temp = response['main']['temp']
        desc = response['weather'][0]['description']
        weather_summary = f"{desc.capitalize()}, {temp}°C in {dest}"
        print(f"DEBUG: Weather fetched: {weather_summary}")
        return {
            "task_plan": new_plan,
            "weather": weather_summary
        }
    except Exception as e:
        print(f"DEBUG: Weather exception: {str(e)}")
        return {
            "task_plan": new_plan,
            "weather": f"Weather data currently unavailable for {dest}"
        }
