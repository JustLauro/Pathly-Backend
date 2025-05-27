import sys

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from xml.etree import ElementTree as ET
import logging
from app.apis import openai
from app.services import route_service
from app.models.user_input import UserInput
from app.models.edit_input import EditedWaypointList
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from io import BytesIO

logging.basicConfig(
    handlers=[
        logging.FileHandler(filename="app.log", encoding="utf-8", mode="a"),
        logging.StreamHandler(stream=sys.stdout),
    ],
    level=logging.INFO,
 )

logger = logging.getLogger(__name__)
app = FastAPI(title="Pathly", version="1.0")

origins = [
    "http://localhost:5173",
    "http://localhost"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/api/generate-route")
async def start_route_generation(user_input: UserInput):
    logger.info("Route generation started")
    return JSONResponse(await route_service.generate_route(user_input))

@app.post("/api/edit-route")
async def edit_route(waypoints: EditedWaypointList):
    logger.info("Route edit started")
    return JSONResponse(await route_service.edit_route(waypoints))

@app.post("/api/convertgeojson")
async def convert_geojson_to_gpx(geojson_data: dict):
    logger.info("Convert GeoJSON to GPX")
    gpx_string = await route_service.convert_geojson_to_gpx(geojson_data)
    buffer = BytesIO()
    buffer.write(gpx_string.encode("utf-8"))
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/gpx+xml", headers={"Content-Disposition": "attachment; filename=route.gpx"})

@app.get("/api/test-generate-route")
async def test_route_generation():
    return JSONResponse(await route_service.test_generate_route())

@app.get("/api/test-chatgpt")
async def test_chatgpt():
    return openai.prompt_azure_ai("Naumburger Straße 38, 04229, Leipzig", "Hauptbahnhof Leipzig")





    
    
