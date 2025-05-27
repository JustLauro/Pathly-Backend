from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

class AliasModel(BaseModel):
    class Config:
        allow_population_by_field_name = True

class TravelMode(Enum):
    WALK = "walk"
    BIKE = "bike"
    DRIVE = "drive"


class UserInput(AliasModel):
    start_point: str = Field(..., alias = "start")
    end_point: str | None = Field(..., alias = "ziel")
    distance: float | None = Field(..., alias = "entfernung")
    user_prompt: str | None = Field(..., alias = "optionen")
    roundtrip: bool = Field(..., alias = "rundreise")
    mode: TravelMode