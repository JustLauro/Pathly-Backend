from pydantic import BaseModel


class Waypoint(BaseModel):
    name: str
    coordinates: str

class EditedWaypointList(BaseModel):
    waypoints: list[Waypoint]
    mode: str