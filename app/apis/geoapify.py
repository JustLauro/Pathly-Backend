import asyncio
import json
from typing import Any, Coroutine

import httpx


from app.settings import settings


geoapify_api_key: str = settings.geoapify_api_key


def build_routes_request_url(waypoints: list[str]) -> str:
    waypoint_string: str = "|".join(waypoints)
    final_url: str = f"""https://api.geoapify.com/v1/routing?waypoints={waypoint_string}&mode=walk&units=metric&format=json&apiKey={geoapify_api_key}"""
    return final_url

async def call_geoapify_routes(waypoints: list[str]) -> str:
    client = httpx.AsyncClient()
    response = await client.get(build_routes_request_url(waypoints))
    return response.json()
    

async def start_batch_geocoding(waypoints: list[str]) -> str:
    client = httpx.AsyncClient()
    url = f"https://api.geoapify.com/v1/geocode/search?apiKey={geoapify_api_key}"
    response = await client.post(url, json=waypoints)
    job_id = response.json().get("id")
    batch_response = await poll_batch_geocoding(job_id)
    return batch_response


async def poll_batch_geocoding(job_id: int, max_wait: int = 30, interval: int = 2) -> Any | None:
    client = httpx.AsyncClient()
    url = f"https://api.geoapify.com/v1/batch/geocode/search?id={job_id}&apiKey={geoapify_api_key}&format=json"

    for _ in range(0, max_wait, 2):
        response = await client.get(url)
        if response.status_code == 200:
            data = response.json()
            return data
        await asyncio.sleep(interval)




