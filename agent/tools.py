
"""
Mock tools for the Smart Accessible Trip Agent.

These functions currently return mock data so the Agent can be developed
and tested before connecting to the real backend/database.
"""


def search_nearby_pois(
    lat: float,
    lon: float,
    radius_m: int = 5000,
    type: str = "",
    limit: int = 10
) -> dict:
    """Return mock POIs near Riyadh."""

    pois = [
        {
            "poi_id": "poi_001",
            "name": "National Museum of Saudi Arabia",
            "type": "museum",
            "latitude": 24.6478,
            "longitude": 46.7097,
            "accessibility": ["wheelchair", "stroller"],
            "indoor": True,
            "average_visit_minutes": 120,
            "price_sar": 0
        },
        {
            "poi_id": "poi_002",
            "name": "Kingdom Centre",
            "type": "shopping",
            "latitude": 24.7111,
            "longitude": 46.6744,
            "accessibility": ["wheelchair", "stroller"],
            "indoor": True,
            "average_visit_minutes": 120,
            "price_sar": 100
        },
        {
            "poi_id": "poi_003",
            "name": "Al Bujairi Heritage Park",
            "type": "park",
            "latitude": 24.7333,
            "longitude": 46.5744,
            "accessibility": ["wheelchair"],
            "indoor": False,
            "average_visit_minutes": 90,
            "price_sar": 0
        },
        {
            "poi_id": "poi_004",
            "name": "Riyadh Park",
            "type": "shopping",
            "latitude": 24.7578,
            "longitude": 46.6272,
            "accessibility": ["wheelchair", "stroller"],
            "indoor": True,
            "average_visit_minutes": 150,
            "price_sar": 0
        }
    ]

    if type:
        pois = [
            poi for poi in pois
            if poi["type"].lower() == type.lower()
        ]

    return {
        "results": pois[:limit]
    }


def search_events(
    date: str,
    lat: float,
    lon: float,
    radius_m: int = 10000,
    event_type: str = "",
    limit: int = 10
) -> dict:
    """Return mock Riyadh events."""

    events = [
        {
            "event_id": "event_001",
            "name": "Riyadh Cultural Event",
            "event_type": "cultural",
            "date": date,
            "latitude": 24.6900,
            "longitude": 46.7100,
            "start_time": "18:00",
            "end_time": "21:00",
            "indoor": True
        },
        {
            "event_id": "event_002",
            "name": "Family Entertainment Event",
            "event_type": "family",
            "date": date,
            "latitude": 24.7200,
            "longitude": 46.6800,
            "start_time": "17:00",
            "end_time": "22:00",
            "indoor": True
        }
    ]

    if event_type:
        events = [
            event for event in events
            if event["event_type"].lower() == event_type.lower()
        ]

    return {
        "results": events[:limit]
    }


def check_place_open(
    poi_id: str,
    requested_datetime: str
) -> dict:
    """Return mock opening-hour information."""

    return {
        "poi_id": poi_id,
        "requested_datetime": requested_datetime,
        "is_open": True
    }


def get_prayer_times(date: str) -> dict:
    """Return mock prayer times for Riyadh."""

    return {
        "date": date,
        "city": "Riyadh",
        "prayer_times": {
            "fajr": "04:10",
            "dhuhr": "12:00",
            "asr": "15:25",
            "maghrib": "18:35",
            "isha": "20:05"
        }
    }


def get_nearby_services(
    lat: float,
    lon: float,
    limit: int = 10
) -> dict:
    """Return mock nearby services."""

    return {
        "results": [
            {
                "service_id": "service_001",
                "name": "Example Family Restaurant",
                "type": "restaurant",
                "latitude": 24.6501,
                "longitude": 46.7123
            },
            {
                "service_id": "service_002",
                "name": "Example Cafe",
                "type": "cafe",
                "latitude": 24.6550,
                "longitude": 46.7150
            }
        ][:limit]
    }


def get_nearest_transit(
    lat: float,
    lon: float,
    limit: int = 5
) -> dict:
    """Return mock public transportation information."""

    return {
        "results": [
            {
                "transit_id": "transit_001",
                "name": "Riyadh Metro Station",
                "type": "metro",
                "latitude": 24.7000,
                "longitude": 46.6800
            }
        ][:limit]
    }