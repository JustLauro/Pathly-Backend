from pydantic import BaseModel


class Waypoint(BaseModel):
    name: str
    coordinates: list[float]

class EditedWaypointList(BaseModel):
    waypoints: list[Waypoint]
    mode: str