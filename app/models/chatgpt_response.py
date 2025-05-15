from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

class AliasModel(BaseModel):
    model_config = ConfigDict(
        alias_generator = to_camel,
        populate_by_name = True,
        from_attributes = True
    )

class Waypoint(AliasModel):
    id: int
    name: str
    address: str | None
    coordinates: str

class Route(AliasModel):
    name_of_the_route: str
    start_point: str
    end_point: str
    waypoints: list[Waypoint]



