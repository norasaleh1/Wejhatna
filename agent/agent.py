import json

from google import genai

from agent.config import GEMINI_API_KEY
from agent.prompts import SYSTEM_PROMPT
from agent.tools import (
    search_nearby_pois,
    search_events,
    check_place_open,
    get_prayer_times,
)


client = genai.Client(api_key=GEMINI_API_KEY)

MODEL_NAME = "gemini-2.5-flash"

TOOLS = [
    search_nearby_pois,
    search_events,
    check_place_open,
    get_prayer_times,
]


def create_itinerary(agent_input: dict) -> dict:
    """
    Create a Riyadh itinerary based on the user's preferences.
    """

    user_request = f"""
Create an itinerary using this user information:

{json.dumps(agent_input, indent=2)}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=user_request,
        config={
            "system_instruction": SYSTEM_PROMPT,
            "tools": TOOLS,
        },
    )

    result = response.text.strip()

    try:
        return json.loads(result)

    except json.JSONDecodeError:
        raise ValueError(
            "Gemini did not return valid JSON.\n\n"
            f"Gemini response:\n{result}"
        )



def replan_itinerary(replan_input: dict) -> dict:
    """
    Replan the remaining part of the user's day.

    Completed activities should remain unchanged.
    Only the remaining itinerary should be modified.
    """

    user_request = f"""
The user wants to REPLAN their current day.

Use the current trip information below.

Important:
- Keep completed activities unchanged.
- Do not schedule activities that have already been completed.
- Only modify the remaining part of the day.
- Consider the reason for the change.
- Use the available tools to get updated information.
- Return the complete updated itinerary in the required JSON format.

Current trip information:

{json.dumps(replan_input, indent=2)}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=user_request,
        config={
            "system_instruction": SYSTEM_PROMPT,
            "tools": TOOLS,
        },
    )

    result = response.text.strip()

    try:
        return json.loads(result)

    except json.JSONDecodeError:
        raise ValueError(
            "Gemini did not return valid JSON.\n\n"
            f"Gemini response:\n{result}"
        )




if __name__ == "__main__":

    replan_input = {
        "destination": "Riyadh",
        "date": "2026-08-11",
        "current_time": "14:30",
        "current_location": {
            "latitude": 24.6501,
            "longitude": 46.7123
        },
        "completed_activity_ids": [
            "poi_001"
        ],
        "current_itinerary": [
            {
                "activity_id": "poi_001",
                "place_id": "poi_001",
                "activity_name": "National Museum of Saudi Arabia",
                "activity_type": "museum",
                "latitude": 24.6478,
                "longitude": 46.7097,
                "start_time": "10:00",
                "end_time": "12:00",
                "duration_minutes": 120,
                "reason": "Indoor family activity."
            },
            {
                "activity_id": "poi_002",
                "place_id": "poi_002",
                "activity_name": "Kingdom Centre",
                "activity_type": "shopping",
                "latitude": 24.7111,
                "longitude": 46.6744,
                "start_time": "15:00",
                "end_time": "17:00",
                "duration_minutes": 120,
                "reason": "Shopping activity."
            }
        ],
        "change": {
            "type": "traffic",
            "description": "Heavy traffic around the next destination."
        }
    }

    itinerary = replan_itinerary(replan_input)

    print(
        json.dumps(
            itinerary,
            indent=2,
            ensure_ascii=False
        )
    )

