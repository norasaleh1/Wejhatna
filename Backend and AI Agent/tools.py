from cherrypy import response
import requests
import psycopg2
import json
from psycopg2.extras import RealDictCursor

from config import (
    DB_HOST,
    DB_PORT,
    DB_NAME,
    DB_USER,
    DB_PASSWORD,
)

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )



def search_nearby_pois(
    lat: float,
    lon: float,
    radius_m: int = 5000,
    type: str = "",
    limit: int = 10
) -> dict:

    conn = get_db_connection()

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:

            query = """
                SELECT
                    poi_id,
                    name_en AS name,
                    type,
                    opening_hours,
                    latitude,
                    longitude,
                    wheelchair_accessible
                FROM pois
                WHERE
                    ST_DWithin(
                        geom::geography,
                        ST_SetSRID(
                            ST_MakePoint(%s, %s),
                            4326
                        )::geography,
                        %s
                    )
            """

            params = [lon, lat, radius_m]

            if type:
                query += " AND LOWER(type) = LOWER(%s)"
                params.append(type)

            query += """
                ORDER BY
                    ST_Distance(
                        geom::geography,
                        ST_SetSRID(
                            ST_MakePoint(%s, %s),
                            4326
                        )::geography
                    )
                LIMIT %s
            """

            params.extend([lon, lat, limit])

            cur.execute(query, params)

            results = cur.fetchall()

            return {
                "results": [dict(row) for row in results]
            }

    finally:
        conn.close()


def search_events(
    date: str,
    lat: float,
    lon: float,
    radius_m: int = 10000,
    event_type: str = "",
    limit: int = 10
) -> dict:

    conn = get_db_connection()

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:

            query = """
                SELECT
                    event_id,
                    event_name AS name,
                    event_type,
                    venue_name,
                    start_date,
                    end_date,
                    opening_time AS start_time,
                    closing_time AS end_time,
                    ST_Y(geom) AS latitude,
                    ST_X(geom) AS longitude
                FROM events
                WHERE
                    %s::date BETWEEN start_date AND end_date
                    AND ST_DWithin(
                        geom::geography,
                        ST_SetSRID(
                            ST_MakePoint(%s, %s),
                            4326
                        )::geography,
                        %s
                    )
            """

            params = [date, lon, lat, radius_m]

            if event_type:
                query += " AND LOWER(event_type) = LOWER(%s)"
                params.append(event_type)

            query += """
                ORDER BY
                    ST_Distance(
                        geom::geography,
                        ST_SetSRID(
                            ST_MakePoint(%s, %s),
                            4326
                        )::geography
                    )
                LIMIT %s
            """

            params.extend([lon, lat, limit])

            cur.execute(query, params)
            results = cur.fetchall()

            return {
                "results": [dict(row) for row in results]
            }

    finally:
        conn.close()

def check_place_open(
    poi_id: str,
    requested_datetime: str
) -> dict:

    conn = get_db_connection()

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT
                    poi_id,
                    opening_hours
                FROM pois
                WHERE poi_id = %s
                """,
                (poi_id,)
            )

            row = cur.fetchone()

            if not row:
                return {
                    "poi_id": poi_id,
                    "requested_datetime": requested_datetime,
                    "is_open": None,
                    "status": "Unknown"
                }

            opening_hours = row["opening_hours"]

            if opening_hours is None or str(opening_hours).strip() == "":
                status = "Unknown"
                is_open = None

            elif str(opening_hours).strip().lower() == "24/7":
                status = "Open"
                is_open = True

            else:
                status = "Unknown"
                is_open = None

            return {
                "poi_id": poi_id,
                "requested_datetime": requested_datetime,
                "opening_hours": opening_hours,
                "is_open": is_open,
                "status": status
            }

    finally:
        conn.close()

def get_prayer_times(date: str) -> dict:

    conn = get_db_connection()

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT
                    date,
                    location,
                    fajr,
                    dhuhr,
                    asr,
                    maghrib,
                    isha
                FROM prayer_times
                WHERE date = %s::date
                LIMIT 1
                """,
                (date,)
            )

            row = cur.fetchone()

            if not row:
                return {
                    "date": date,
                    "city": "Riyadh",
                    "prayer_times": None,
                    "status": "Not found"
                }

            return {
                "date": str(row["date"]),
                "city": row["location"],
                "prayer_times": {
                    "fajr": str(row["fajr"]),
                    "dhuhr": str(row["dhuhr"]),
                    "asr": str(row["asr"]),
                    "maghrib": str(row["maghrib"]),
                    "isha": str(row["isha"])
                }
            }

    finally:
        conn.close()


def get_nearby_services(
    lat: float,
    lon: float,
    limit: int = 10
) -> dict:

    conn = get_db_connection()

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:

            cur.execute(
                """
                SELECT
                    poi_id AS service_id,
                    COALESCE(name_en, name) AS name,
                    type,
                    latitude,
                    longitude,
                    wheelchair_accessible
                FROM pois
                WHERE
                    LOWER(type) IN ('attraction', 'heritage', 'mosque', 'museum', 'park')
                    AND ST_DWithin(
                        geom::geography,
                        ST_SetSRID(
                            ST_MakePoint(%s, %s),
                            4326
                        )::geography,
                        5000
                    )
                ORDER BY
                    ST_Distance(
                        geom::geography,
                        ST_SetSRID(
                            ST_MakePoint(%s, %s),
                            4326
                        )::geography
                    )
                LIMIT %s
                """,
                (lon, lat, lon, lat, limit)
            )

            results = cur.fetchall()

            return {
                "results": [dict(row) for row in results]
            }

    finally:
        conn.close()

def get_nearest_transit(
    lat: float,
    lon: float,
    limit: int = 5
) -> dict:

    conn = get_db_connection()

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:

            query = """
                SELECT *
                FROM (
                    SELECT
                        ms.station_id::text AS transit_id,
                        COALESCE(ms.station_name_en, ms.station_name_ar) AS name,
                        'metro' AS type,
                        ST_Y(msl.geom) AS latitude,
                        ST_X(msl.geom) AS longitude,
                        ST_Distance(
                            msl.geom::geography,
                            ST_SetSRID(
                                ST_MakePoint(%s, %s),
                                4326
                            )::geography
                        ) AS distance_m
                    FROM metro_station_lines msl
                    JOIN metro_stations ms
                        ON ms.station_id = msl.station_id
                    WHERE msl.geom IS NOT NULL

                    UNION ALL

                    SELECT
                        bs.stop_id::text AS transit_id,
                        bs.stop_name AS name,
                        'bus' AS type,
                        ST_Y(bs.geom) AS latitude,
                        ST_X(bs.geom) AS longitude,
                        ST_Distance(
                            bs.geom::geography,
                            ST_SetSRID(
                                ST_MakePoint(%s, %s),
                                4326
                            )::geography
                        ) AS distance_m
                    FROM bus_stops bs
                    WHERE bs.geom IS NOT NULL
                ) AS transit
                ORDER BY distance_m
                LIMIT %s
            """

            cur.execute(
                query,
                (lon, lat, lon, lat, limit)
            )

            results = cur.fetchall()

            return {
                "results": [dict(row) for row in results]
            }

    finally:
        conn.close()

def get_weather(
    lat: float,
    lon: float,
    date: str
) -> dict:
    """
    Get hourly weather forecast for a location and date.
    """

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,apparent_temperature,weather_code",
        "timezone": "Asia/Riyadh",
        "start_date": date,
        "end_date": date,
    }

    response = requests.get(
        url,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

    return {
        "latitude": data.get("latitude"),
        "longitude": data.get("longitude"),
        "timezone": data.get("timezone"),
        "hourly": data.get("hourly", {})
    }



def get_route_traffic(
    origin_lat: float,
    origin_lon: float,
    destination_lat: float,
    destination_lon: float
) -> dict:
    """
    Get driving route, travel time, and traffic information using TomTom.
    """

    from config import TOMTOM_API_KEY

    url = (
        f"https://api.tomtom.com/maps/orbis/routing/calculateRoute/"
        f"{origin_lat},{origin_lon}:"
        f"{destination_lat},{destination_lon}/json"
    )

    params = {
        "key": "uZtFQxub2u3f3mIh6zCM3Kj35xXs3Vyx",
        "apiVersion": 2,
        "traffic": "live",
        "travelMode": "car",
        "routeType": "fast"
    }

    response = requests.get(
        url,
        params=params,
        timeout=20
    )

    response.raise_for_status()

    data = response.json()

    # Temporary: show the real TomTom response
    # print("\nTOMTOM RAW RESPONSE:")
    # print(json.dumps(data, indent=2))

    route = data["routes"][0]
    summary = route["summary"]

    travel_time = summary.get("travelTimeInSeconds", 0)
    no_traffic_time = summary.get("noTrafficTravelTimeInSeconds", 0)
    traffic_delay = summary.get("trafficDelayInSeconds", 0)
    distance = summary.get("lengthInMeters", 0)

    if traffic_delay >= 900:
        traffic_level = "heavy"
    elif traffic_delay >= 300:
        traffic_level = "moderate"
    else:
        traffic_level = "light"

    return {
        "distance_m": distance,
        "travel_time_minutes": round(travel_time / 60, 1),
        "no_traffic_time_minutes": round(no_traffic_time / 60, 1),
        "traffic_delay_minutes": round(traffic_delay / 60, 1),
        "traffic_level": traffic_level
    }

def get_traffic_flow(
    lat: float,
    lon: float
) -> dict:
    """
    Get live traffic information near a location using TomTom.
    """

    from config import TOMTOM_API_KEY

    url = (
        "https://api.tomtom.com/maps/orbis/traffic/flowSegmentData/"
        "absolute/10/json"
    )

    headers = {
        "TomTom-Api-Key": TOMTOM_API_KEY
    }

    params = {
        "point": f"{lat},{lon}",
        "unit": "kmph"
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=20
    )

    response.raise_for_status()

    data = response.json()

    current_speed = data.get("currentSpeed")
    free_flow_speed = data.get("freeFlowSpeed")

    if current_speed is None or not free_flow_speed:
        traffic_level = "unknown"
    else:
        ratio = current_speed / free_flow_speed

        if ratio >= 0.8:
            traffic_level = "light"
        elif ratio >= 0.5:
            traffic_level = "moderate"
        else:
            traffic_level = "heavy"

    return {
        "current_speed_kmh": current_speed,
        "free_flow_speed_kmh": free_flow_speed,
        "current_travel_time_seconds": data.get("currentTravelTime"),
        "free_flow_travel_time_seconds": data.get("freeFlowTravelTime"),
        "confidence": data.get("confidence"),
        "road_closed": data.get("roadClosure", False),
        "traffic_level": traffic_level
    }




def get_waze_jams(
    lat: float,
    lon: float,
    radius_deg: float = 0.03
) -> dict:
    """
    Get live traffic jams around a location using WazeAPI.
    """

    from config import WAZE_API_KEY

    url = "https://api.wazeapi.com/v1/alerts/jams"

    bottom_left = f"{lat - radius_deg},{lon - radius_deg}"
    top_right = f"{lat + radius_deg},{lon + radius_deg}"

    headers = {
        "X-API-Key": WAZE_API_KEY
    }

    params = {
        "bottom-left": bottom_left,
        "top-right": top_right
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=20
    )

    response.raise_for_status()

    data = response.json()

    if isinstance(data, list):
        jams = data
    else:
        jams = data.get("jams", [])

    if not jams:
        traffic_level = "light"
        max_level = 0
    else:
        levels = []

        for jam in jams:
            if isinstance(jam, dict):
                level = jam.get("level")

                if level is not None:
                    levels.append(level)

        max_level = max(levels) if levels else 0

        if max_level >= 4:
            traffic_level = "heavy"
        elif max_level >= 2:
            traffic_level = "moderate"
        else:
            traffic_level = "light"

    return {
        "jam_count": len(jams),
        "max_jam_level": max_level,
        "traffic_level": traffic_level,
        "jams": jams
    }





from tavily import TavilyClient
from config import TAVILY_API_KEY

tavily_client = TavilyClient(api_key=TAVILY_API_KEY)


def search_live_web(query: str) -> dict:
    """
    Search the live web for current information related to a Riyadh trip.

    Use this tool when database information is missing, outdated, or when
    current information is needed, such as:
    - places and attractions
    - opening hours
    - events
    - weather
    - traffic conditions
    - prayer times
    - accessibility information

    The local database should be used when useful, but it is not the only
    source of information.
    """

    try:
        response = tavily_client.search(
            query=query,
            search_depth="advanced",
            max_results=5,
            include_answer=True
        )

        return {
            "answer": response.get("answer"),
            "results": response.get("results", [])
        }

    except Exception as e:
        return {
            "error": str(e),
            "answer": None,
            "results": []
        }







if __name__ == "__main__":
    try:
        print("1. Database:")
        conn = get_db_connection()
        print("Database connection successful!")
        conn.close()

        print("\n2. POIs:")
        print(search_nearby_pois(
            lat=24.7136,
            lon=46.6753,
            radius_m=5000,
            limit=3
        ))

        print("\n3. Events:")
        print(search_events(
            date="2026-10-15",
            lat=24.7136,
            lon=46.6753,
            radius_m=20000,
            limit=3
        ))

        print("\n4. Prayer Times:")
        print(get_prayer_times("2026-08-11"))

        print("\n5. Nearby Services:")
        print(get_nearby_services(
            lat=24.7136,
            lon=46.6753,
            limit=3
        ))

        print("\n6. Nearest Transit:")
        print(get_nearest_transit(
            lat=24.7136,
            lon=46.6753,
            limit=5
        ))

        print("\n7. Weather:")
        print(get_weather(
            lat=24.7136,
            lon=46.6753,
            date="2026-08-11"
        ))

        print("\n8. Route Traffic:")
        print(get_route_traffic(
            origin_lat=24.7136,
            origin_lon=46.6753,
            destination_lat=24.7708,
            destination_lon=46.5985
        ))
        print("\n9. Waze Traffic:")
        print(get_waze_jams(
           lat=24.7136,
           lon=46.6753
        ))

        print("\n10. Tavily Search:")
        print(tavily_search(query=
            "What is the capital of France?"
        ))

    except Exception as e:
        print("\nERROR:")
        print(e)

        