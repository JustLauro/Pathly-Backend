from models.user_input import UserInput
from apis.openAI import prompt_azure_ai
from models.chatgpt_response import Route


def generate_route(user_input: UserInput):

    generated_route: Route = prompt_azure_ai(user_input.start_point, user_input.end_point, user_input.user_prompt)
    
