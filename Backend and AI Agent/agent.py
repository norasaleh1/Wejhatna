import json
from google.genai import types
from google import genai

from config import GEMINI_API_KEY
from prompts import SYSTEM_PROMPT
from tools import (
    search_nearby_pois,
    search_events,
    check_place_open,
    get_prayer_times,
    get_weather,
    get_route_traffic,
    get_waze_jams,
    search_live_web,
)


client = genai.Client(api_key=GEMINI_API_KEY)

MODEL_NAME = "gemini-3.1-flash-lite"

TOOLS = [
    search_nearby_pois,
    search_events,
    check_place_open,
    get_prayer_times,
    get_weather,
    get_route_traffic,
    get_waze_jams,
    search_live_web,
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
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=TOOLS,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                maximum_remote_calls=8
            ),
        ),
    )

    if not response.text:
        raise ValueError(
            "Gemini did not return a final text response after tool calls."
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
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=TOOLS,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                maximum_remote_calls=15
            ),
        ),
    )

    if not response.text:
        raise ValueError(
            "Gemini did not return a final text response after tool calls."
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

    print("\n===================================")
    print("      WEJHATNA AI TRIP PLANNER")
    print("===================================\n")

    print("Hi! I will help you plan your trip in Riyadh.\n")

    date = input("Trip date (YYYY-MM-DD): ")

    days = int(input("Number of days: "))

    people = int(input("Number of people: "))

    children_input = input("Are there children? (yes/no): ").strip().lower()
    children = children_input == "yes"

    elderly_input = input("Are there elderly people? (yes/no): ").strip().lower()
    elderly = elderly_input == "yes"

    accessibility = input(
        "Accessibility requirements (or type none): "
    )

    budget = input(
        "Budget (low / medium / high): "
    )

    interests = input(
        "Interests (example: museums, parks, heritage, shopping): "
    )

    start_time = input(
        "Preferred start time (HH:MM): "
    )

    end_time = input(
        "Preferred end time (HH:MM): "
    )

    agent_input = {
        "destination": "Riyadh",
        "date": date,
        "number_of_days": days,
        "number_of_people": people,
        "children": children,
        "elderly": elderly,
        "accessibility_requirements": accessibility,
        "budget": budget,
        "interests": interests,
        "preferred_start_time": start_time,
        "preferred_end_time": end_time
    }

    print("\nCreating your smart itinerary...\n")

    try:

        itinerary = create_itinerary(agent_input)

        print(
            json.dumps(
                itinerary,
                indent=2,
                ensure_ascii=False
            )
        )

    except Exception as e:

        print("\nERROR:")
        print(e)

