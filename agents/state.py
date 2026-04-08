from typing import TypedDict, List, Optional

class TravelState(TypedDict):
    messages: List[str]
    source: Optional[str]
    destination: Optional[str]
    duration: Optional[int]
    budget: Optional[int]
    preferences: Optional[List[str]]
    travel_mode: Optional[str]
    travel_date: Optional[str]
    weather: Optional[str]
    accommodations: Optional[List[dict]]
    flights: Optional[List[dict]]
    search_summary: Optional[str]
    alternative_suggestions: Optional[List[str]]
    itinerary_markup: Optional[str]
    ready_to_save: bool
    ready_to_proceed: bool
    last_asked_field: Optional[str]
    reasoning: Optional[str]
    next_action: Optional[str]
    task_plan: Optional[List[str]]
    current_task: Optional[str]
    memory_results: Optional[List[str]]
    hotel_results: Optional[List[dict]]
    flight_results: Optional[List[dict]]
    map_results: Optional[dict]
