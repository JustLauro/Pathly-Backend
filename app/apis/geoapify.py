import asyncio
import os

import httpx

from app.models.user_input import TravelMode
from app.config.settings import get_settings


#geoapify_api_key: str = os.getenv("GEOAPIFY_API_KEY")


def build_routes_request_url(waypoints: list[str], travel_mode: TravelMode) -> str:
    settings = get_settings()
    geoapify_api_key: str = settings.geoapify_api_key

    mode = {
        TravelMode.DRIVE: "drive",
        TravelMode.BIKE: "bicycle",
        TravelMode.WALK: "hike"
    }.get(travel_mode)


    waypoint_string: str = "|".join(waypoints)
    final_url: str = f"""https://api.geoapify.com/v1/routing?waypoints={waypoint_string}&mode={mode}&units=metric&format=geojson&apiKey={geoapify_api_key}"""
    return final_url

async def call_geoapify_routes(waypoints: list[str], mode: TravelMode) -> dict:
    client = httpx.AsyncClient()
    response = await client.get(build_routes_request_url(waypoints, mode))
    return response.json()
    

async def start_batch_geocoding(waypoints: list[str]) -> str:
    settings = get_settings()
    geoapify_api_key: str = settings.geoapify_api_key

    client = httpx.AsyncClient()
    url = f"https://api.geoapify.com/v1/batch/geocode/search?&apiKey={geoapify_api_key}"
    response = await client.post(url, json=waypoints)
    if response.status_code != 200:
        error = response.json()
    job_id: str = response.json().get("id")
    return job_id


async def poll_batch_geocoding(job_id: str, max_wait: int = 20, interval: int = 1) -> dict | None:
    settings = get_settings()
    geoapify_api_key: str = settings.geoapify_api_key

    client = httpx.AsyncClient()
    url = f"https://api.geoapify.com/v1/batch/geocode/search?id={job_id}&apiKey={geoapify_api_key}&format=json"

    for i in range(1, max_wait + 1, 1):
        print("Poll Nr.: " + str(i))
        response = await client.get(url)
        if response.status_code == 200:
            data = response.json()
            return data
        await asyncio.sleep(interval)

    return None




