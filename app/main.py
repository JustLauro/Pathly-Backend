from fastapi import FastAPI
from app.services import route_service
from app.models.user_input import UserInput
from app.apis.geoapify import call_geoapify_routes

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.post("api/generate-route")
async def start_route_generation(user_input: UserInput):
    await route_service.generate_route(user_input)
    return user_input

@app.get("/api/test-generate-route")
async def test_route_generation():
    return await route_service.test_generate_route()





    
    
