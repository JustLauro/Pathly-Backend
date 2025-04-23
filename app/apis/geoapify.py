import httpx
from settings import settings


geoapify_api_key: str = ""

def build_request_url(waypoints: list[str]) -> str:
    waypoint_string: str = "|".join(waypoints)
    final_url: str = f'''https://api.geoapify.com/v1/routing?waypoints={waypoint_string}&mode=walk&units=metric&format=json&apiKey={geoapify_api_key}'''
    return final_url


async def call_geoapify_routes(waypoints: list[str]):
    async with httpx.AsyncClient as client:
        response = await client.get(build_request_url(waypoints))
        print(response)

