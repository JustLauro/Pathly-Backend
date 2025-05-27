import sys

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import logging
from app.apis import openai
from app.services import route_service
from app.models.user_input import UserInput
from app.models.edit_input import EditedWaypointList
from fastapi.middleware.cors import CORSMiddleware

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


@app.get("/api/test-generate-route")
async def test_route_generation():
    return JSONResponse(await route_service.test_generate_route())

@app.get("/api/test-chatgpt")
async def test_chatgpt():
    return openai.prompt_azure_ai("Naumburger Straße 38, 04229, Leipzig", "Hauptbahnhof Leipzig")





    
    
