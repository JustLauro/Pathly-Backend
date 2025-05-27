import json

from xml.etree import ElementTree as ET

from datetime import datetime

from pydantic import ValidationError
from fastapi import HTTPException 
from starlette import status

from app.models.edit_input import EditedWaypointList
from app.models.user_input import UserInput
from app.apis import openai
from app.models.chatgpt_response import Route
from app.apis import geoapify
from app.models.user_input import TravelMode

def combine_waypoints_and_geojson(waypoints: list[str], geojson: dict) -> dict:
    return {
        "geojson": geojson,
        "waypoints": waypoints
    }


async def edit_route(edited_waypoints: EditedWaypointList):

    coordinates: list[str] = []
    waypoint_names: list[str] = []
    travel_mode: str = edited_waypoints.mode

    for wp in edited_waypoints.waypoints:
        reversed_coords = wp.coordinates[::-1]
        waypoints_string = ",".join(map(str, reversed_coords))

        coordinates.append(waypoints_string)
        waypoint_names.append(wp.name)

    mode = {
        "drive": TravelMode.DRIVE,
        "bicycle": TravelMode.BIKE,
        "hike": TravelMode.WALK
    }.get(travel_mode)

    geojson = await geoapify.call_geoapify_routes(coordinates, mode)

    return combine_waypoints_and_geojson(waypoint_names, geojson)


async def generate_route(user_input: UserInput):

    start_point: str = user_input.start_point
    end_point: str = user_input.end_point
    distance: float = user_input.distance
    mode: TravelMode = user_input.mode
    user_prompt: str = user_input.user_prompt
    roundtrip: bool = user_input.roundtrip

    generated_route_string = openai.prompt_azure_ai(start_point, end_point, distance, mode, user_prompt, roundtrip)
    print(generated_route_string)

    generated_route: Route | None = None

    try:
        generated_route: Route = Route.model_validate_json(generated_route_string)
    except ValidationError as e:
        print(e)

    addresses_array: list[str] = [wp.address if wp.address else wp.name for wp in generated_route.waypoints]
    waypoint_names: list[str] = [wp.name for wp in generated_route.waypoints]
    geocoding_id = await geoapify.start_batch_geocoding(addresses_array)
    geocoding_result = await geoapify.poll_batch_geocoding(geocoding_id)
    print(geocoding_result)

    waypoints: list[str] = [f"{entry['lat']},{entry['lon']}" for entry in geocoding_result if
                            'lon' in entry and 'lat' in entry]
    print(waypoints)

    geojson = await geoapify.call_geoapify_routes(waypoints, mode)

    return combine_waypoints_and_geojson(waypoint_names, geojson)


async def convert_geojson_to_gpx(geojson_data: dict) -> str:
    print("start conversion process")
    all_coords = []
    route_name = "Unbenannte Route"
    route_description = ""

    # GeoJSON parsen
    if geojson_data.get("type") == "FeatureCollection":
        for feature in geojson_data.get("features", []):
            geometry = feature.get("geometry")
            properties = feature.get("properties", {})

            if geometry and geometry.get("type") == "LineString":
                all_coords.extend(geometry["coordinates"])
            elif geometry and geometry.get("type") == "MultiLineString":
                for line in geometry["coordinates"]:
                    all_coords.extend(line)

            route_name = properties.get("name", route_name)
            route_description = properties.get("description", route_description)

    elif geojson_data.get("type") == "Feature":
        geometry = geojson_data.get("geometry")
        properties = geojson_data.get("properties", {})
        if geometry.get("type") == "LineString":
            all_coords.extend(geometry["coordinates"])
        elif geometry.get("type") == "MultiLineString":
            for line in geometry["coordinates"]:
                all_coords.extend(line)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ungültiges GeoJSON-Format: Erwartet LineString oder MultiLineString."
            )

        route_name = properties.get("name", route_name)
        route_description = properties.get("description", route_description)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ungültiges GeoJSON-Format: Feature oder FeatureCollection erwartet."
        )

    if not all_coords:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Keine Koordinaten gefunden."
        )

    # GPX-Struktur aufbauen
    ET.register_namespace('', "http://www.topografix.com/GPX/1/1")
    ET.register_namespace('xsi', "http://www.w3.org/2001/XMLSchema-instance")

    gpx = ET.Element("gpx", {
        "version": "1.1",
        "creator": "Pathly",
        "xmlns": "http://www.topografix.com/GPX/1/1",
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xsi:schemaLocation": "http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd"
    })

    metadata = ET.SubElement(gpx, "metadata")
    ET.SubElement(metadata, "time").text = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    trk = ET.SubElement(gpx, "trk")
    ET.SubElement(trk, "name").text = route_name

    trkseg = ET.SubElement(trk, "trkseg")

    for coord in all_coords:
        lat, lon = coord[1], coord[0]
        trkpt = ET.SubElement(trkseg, "trkpt", {
            "lat": str(lat),
            "lon": str(lon)
        })
        if len(coord) > 2:
            ET.SubElement(trkpt, "ele").text = str(coord[2])

    try:
        ET.indent(gpx, space="  ")
    except AttributeError:
        pass

    gpx_bytes = ET.tostring(gpx, encoding="utf-8", xml_declaration=True)
    gpx_string = gpx_bytes.decode("utf-8")

    print("finished conversion process")
    return gpx_string

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





    
