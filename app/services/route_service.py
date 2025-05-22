import json

from pydantic import ValidationError
from app.models.user_input import UserInput
from app.apis import openai
from app.models.chatgpt_response import Route
from app.apis import geoapify
from app.models.user_input import TravelMode


async def generate_route(user_input: UserInput):

    start_point: str = user_input.start_point
    if user_input.roundtrip:
        end_point: str = start_point
    else:
        end_point: str = user_input.end_point
    distance: str = user_input.distance
    user_prompt = user_input.user_prompt
    mode: TravelMode = user_input.mode

    generated_route_string = openai.prompt_azure_ai(
        start_point, user_input.end_point, user_input.user_prompt
    )
    print(generated_route_string)

    generated_route: Route | None = None

    try:
        generated_route: Route = Route.model_validate_json(generated_route_string)
    except ValidationError as e:
        print(e)

    addresses_array: list[str] = [wp.address if wp.address else wp.name for wp in generated_route.waypoints]
    geocoding_id = await geoapify.start_batch_geocoding(addresses_array)
    geocoding_result = await geoapify.poll_batch_geocoding(geocoding_id)
    print(geocoding_result)

    waypoints: list[str] = [f"{entry['lat']},{entry['lon']}" for entry in geocoding_result if
                            'lon' in entry and 'lat' in entry]
    print(waypoints)

    route = await geoapify.call_geoapify_routes(waypoints)
    return route

# async def test_generate_route() -> list[dict]:
#     generated_route_string: str = """{
#   "nameOfTheRoute": "Leipzig Stadtwanderung: Von Naumburger Straße zum Goerdelerring",
#   "startPoint": "Naumburger Straße 38, 04229 Leipzig, Deutschland",
#   "endPoint": "Goerdelerring, 04109 Leipzig, Deutschland",
#   "waypoints": [
#     {
#       "id": 1,
#       "name": "Volkspark Kleinzschocher, Leipzig, Deutschland",
#       "address": "Kleiststraße 52, 04229 Leipzig, Deutschland",
#       "coordinates": "51.3136, 12.3197"
#     },
#     {
#       "id": 2,
#       "name": "Anton-Bruckner-Allee, Schleußig, Leipzig, Deutschland",
#       "address": "Anton-Bruckner-Allee, 04229 Leipzig, Deutschland",
#       "coordinates": "51.3211, 12.3312"
#     },
#     {
#       "id": 3,
#       "name": "Palmengarten, Leipzig, Deutschland",
#       "address": "Karl-Tauchnitz-Straße 25, 04107 Leipzig, Deutschland",
#       "coordinates": "51.3265, 12.3490"
#     },
#     {
#       "id": 4,
#       "name": "Clara-Zetkin-Park, Leipzig, Deutschland",
#       "address": "Anton-Bruckner-Allee 1, 04107 Leipzig, Deutschland",
#       "coordinates": "51.3278, 12.3483"
#     },
#     {
#       "id": 5,
#       "name": "Musikpavillon im Clara-Zetkin-Park, Leipzig, Deutschland",
#       "address": null,
#       "coordinates": "51.3270, 12.3465"
#     },
#     {
#       "id": 6,
#       "name": "Sachsenbrücke, Leipzig, Deutschland",
#       "address": "Anton-Bruckner-Allee, 04107 Leipzig, Deutschland",
#       "coordinates": "51.3273, 12.3450"
#     },
#     {
#       "id": 7,
#       "name": "Richard-Wagner-Hain, Leipzig, Deutschland",
#       "address": "Karl-Tauchnitz-Straße 1, 04107 Leipzig, Deutschland",
#       "coordinates": "51.3285, 12.3457"
#     },
#     {
#       "id": 8,
#       "name": "Dittrichring, Leipzig, Deutschland",
#       "address": "Dittrichring, 04109 Leipzig, Deutschland",
#       "coordinates": "51.3405, 12.3702"
#     },
#     {
#       "id": 9,
#       "name": "Thomaskirche, Leipzig, Deutschland",
#       "address": "Thomaskirchhof 18, 04109 Leipzig, Deutschland",
#       "coordinates": "51.3396, 12.3724"
#     },
#     {
#       "id": 10,
#       "name": "Bach-Museum Leipzig, Deutschland",
#       "address": "Thomaskirchhof 15/16, 04109 Leipzig, Deutschland",
#       "coordinates": "51.3397, 12.3721"
#     },
#     {
#       "id": 11,
#       "name": "Barfußgäßchen, Leipzig, Deutschland",
#       "address": "Barfußgäßchen, 04109 Leipzig, Deutschland",
#       "coordinates": "51.3409, 12.3736"
#     },
#     {
#       "id": 12,
#       "name": "Zum Arabischen Coffe Baum, Leipzig, Deutschland",
#       "address": "Kleine Fleischergasse 4, 04109 Leipzig, Deutschland",
#       "coordinates": "51.3408, 12.3732"
#     },
#     {
#       "id": 13,
#       "name": "Mädler-Passage, Leipzig, Deutschland",
#       "address": "Grimmaische Straße 2-4, 04109 Leipzig, Deutschland",
#       "coordinates": "51.3405, 12.3748"
#     },
#     {
#       "id": 14,
#       "name": "Auerbachs Keller, Leipzig, Deutschland",
#       "address": "Grimmaische Straße 2-4, 04109 Leipzig, Deutschland",
#       "coordinates": "51.3405, 12.3748"
#     },
#     {
#       "id": 15,
#       "name": "Nikolaikirche, Leipzig, Deutschland",
#       "address": "Nikolaikirchhof 3, 04109 Leipzig, Deutschland",
#       "coordinates": "51.3403, 12.3761"
#     },
#     {
#       "id": 16,
#       "name": "Goerdelerring, Leipzig, Deutschland",
#       "address": "Goerdelerring, 04109 Leipzig, Deutschland",
#       "coordinates": "51.3420, 12.3710"
#     }
#   ]
# }"""
#     generated_route: Route | None = None
#
#     try:
#         generated_route: Route = Route.model_validate_json(generated_route_string)
#     except ValidationError as e:
#         print(e)
#
#     addresses_array: list[str] = [wp.address if wp.address else wp.name for wp in generated_route.waypoints]
#     geocoding_id = await geoapify.start_batch_geocoding(addresses_array)
#     geocoding_result = await geoapify.poll_batch_geocoding(geocoding_id)
#     print(geocoding_result)
#
#     waypoints: list[str] = [f"{entry['lat']},{entry['lon']}" for entry in geocoding_result if 'lon' in entry and 'lat' in entry]
#     print(waypoints)
#
#     route = await geoapify.call_geoapify_routes(waypoints)
#     return route





    
