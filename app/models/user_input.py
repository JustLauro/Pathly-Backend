from pydantic import BaseModel

class UserInput(BaseModel):
    start_point: str
    end_point: str
    user_prompt: str