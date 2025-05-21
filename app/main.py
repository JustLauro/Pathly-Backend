from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.apis import openai
from app.services import route_service
from app.models.user_input import UserInput
from app.apis.geoapify import call_geoapify_routes

app = FastAPI()

@app.post("/api/generate-route")
async def start_route_generation(user_input: UserInput):
    print(user_input)
    return JSONResponse(await route_service.generate_route(user_input))

@app.get("/api/test-generate-route")
async def test_route_generation():
    return JSONResponse(await route_service.test_generate_route())

@app.get("/api/test-chatgpt")
async def test_chatgpt():
    return openai.prompt_azure_ai("Naumburger Straße 38, 04229, Leipzig", "Hauptbahnhof Leipzig")





    
    
