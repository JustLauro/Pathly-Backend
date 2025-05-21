from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

class AliasModel(BaseModel):
    class Config:
        allow_population_by_field_name = True


class UserInput(AliasModel):
    start_point: str = Field(..., alias = "start")
    end_point: str = Field(..., alias = "ziel")
    distance: str = Field(..., alias = "entfernung")
    user_prompt: str = Field(..., alias = "optionen")
    roundtrip: bool = Field(..., alias = "rundreise")
    mode: str