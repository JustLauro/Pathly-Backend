from openai import AzureOpenAI
from app.models.chatgpt_response import Route
from app.models.user_input import TravelMode
from app.settings import settings

openai_api_key: str = settings.openai_api_key
azureai_endpoint: str = settings.azureai_endpoint



def build_prompt(
        start_point: str,
        end_point: str | None,
        distance: str | None,
        mode: TravelMode,
        user_prompt: str | None = None,
        roundtrip: bool = False
) -> str:

    travel_mode_description = {
        TravelMode.WALK: "eine Wandertour",
        TravelMode.BIKE: "eine Fahrradtour",
        TravelMode.DRIVE: "eine Autofahrt"
    }.get(mode)


    if roundtrip:
        start_end_info: str = f'Die Route sollte ein Rundweg sein. Start- und Endpunkt sind bei "{start_point}"'
    else:
        start_end_info: str = f'Der Startpunkt ist bei "{start_point}" und der Endpunkt ist bei "{end_point}"'


    generated_prompt: str = f"""Deine Aufgabe ist es eine "Wanderroute" zu erstellen. 
                            {start_end_info}.
                            Die Route soll {distance} Kilometer lang sein.
                            Die Route sollte geeignet sein für {travel_mode_description}.
                            Berücksichtige bei deiner Berechnung bitte folgenden Userprompt: "{user_prompt}".
                            Ermittele zuerst eine Route. Ermittele ausreichend Wegpunkte entlang der Route. 
                            Ermittel für diese Wegpunkte einen Eindeutigen Namen (inklusive Land und Stadt, mit dem der Punkt in Google Maps eindeutig identifizierbar ist),
                            sowie Adresse oder Koordinaten wenn es keine Adresse gibt. Gebe NUR eine JSON Datei zurück die wie folgt aufgebaut ist:
                            {{
                                "nameOfTheRoute": "", 
                                "startPoint": "", 
                                "endPoint": "",
                                "waypoints": 
                                    [
                                        {{
                                            "id": 1, 
                                            "name": "", 
                                            "address": "", 
                                            "coordinates": ""
                                        }}, 
                                        {{
                                            "id": 2, 
                                            "name": "", 
                                            "address": "", 
                                            "coordinates": ""
                                        }}
                                    ]
                            }}.
                            Die Id soll bei jedem waypoint um 1 erhöht werden und einzigartig sein. Füge für jeden Wegpunkt ein Element "waypoint" mit den gesuchten Attributen 
                            hinzu und zähle dabei die Zahl am ende der Variable hoch. Setze Werte die du nicht findest (also z.b. die zu denen du keine Adresse findest) auf "null". 
                            Bitte gib ausschließlich den JSON-String zurück, ohne ein vorrangestelltes 'json' oder Anführungsstriche"""

    return generated_prompt


def prompt_azure_ai(
        start_point: str,
        end_point: str | None,
        distance: str | None,
        mode: TravelMode,
        user_prompt: str | None = None,
        roundtrip: bool = False
) -> str:
    built_prompt = build_prompt(start_point, end_point, distance, mode, user_prompt, roundtrip)

    client = AzureOpenAI(
        azure_endpoint = azureai_endpoint,
        api_key = openai_api_key,
        api_version = "2024-04-01-preview",
        azure_deployment = "mapsAiChatbot-gpt4o"
    )

    response = client.chat.completions.create(
        model = "gpt-4o",
        messages = [
            {"role": "user", "content": built_prompt}
        ]
    )

    # response = client.responses.create(
    #     model="gpt-4o",
    #     instructions = "",
    #     input = built_prompt
    #
    # )

    return response.choices[0].message.content
