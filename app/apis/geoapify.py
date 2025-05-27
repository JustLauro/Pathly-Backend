import asyncio
import json
from typing import Any, Coroutine
import httpx

from app.models.user_input import TravelMode
from app.settings import settings


geoapify_api_key: str = settings.geoapify_api_key


def build_routes_request_url(waypoints: list[str], travel_mode: TravelMode) -> str:

    mode = {
        TravelMode.DRIVE: "drive",
        TravelMode.BIKE: "bicycle",
        TravelMode.WALK: "hike"
    }.get(travel_mode)

    waypoint_string: str = "|".join(waypoints)
    final_url: str = f"""https://api.geoapify.com/v1/routing?waypoints={waypoint_string}&mode={mode}&units=metric&format=geojson&apiKey={geoapify_api_key}"""
    return final_url

async def call_geoapify_routes(waypoints: list[str], mode: TravelMode) -> dict:
    print ("Wegpunkte: " + '\n'.join(waypoints))
    client = httpx.AsyncClient()
    response = await client.get(build_routes_request_url(waypoints, mode))
    return response.json()
    

async def start_batch_geocoding(waypoints: list[str]) -> str:
    client = httpx.AsyncClient()
    url = f"https://api.geoapify.com/v1/batch/geocode/search?&apiKey={geoapify_api_key}"
    response = await client.post(url, json=waypoints)
    if response.status_code != 200:
        error = response.json()
        print(response.json().get("message"))
    job_id: str = response.json().get("id")
    return job_id


async def poll_batch_geocoding(job_id: str, max_wait: int = 30, interval: int = 2) -> dict | None:
    client = httpx.AsyncClient()
    url = f"https://api.geoapify.com/v1/batch/geocode/search?id={job_id}&apiKey={geoapify_api_key}&format=json"

    for i in range(0, max_wait, 2):
        print("Poll Nr.: " + str(i / 2 + 1))
        response = await client.get(url)
        if response.status_code == 200:
            data = response.json()
            return data
        await asyncio.sleep(interval)

    return None




