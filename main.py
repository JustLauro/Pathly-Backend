from fastapi import FastAPI

from services.route_service import generate_route
from models.user_input import UserInput

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.post("apis/generate-route")
async def start_route_generation(user_input: UserInput):
    await generate_route(user_input)
    return user_input
