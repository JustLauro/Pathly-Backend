import this

from pydantic import BaseModel

class Waypoint(BaseModel):
    id: int
    name: str
    address: str
    coordinates: str

class Route(BaseModel):
    name_of_route: str
    start_point: str
    end_point: str
    waypoints: list[Waypoint]



