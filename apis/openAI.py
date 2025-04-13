from openai import AzureOpenAI

def build_prompt(start_point: str, end_point: str, user_prompt: str | None = None) -> str:

    generated_prompt: str = f'''Deine Aufgabe ist es eine "Wanderroute" zu erstellen. Der Startpunkt ist bei "{start_point}".
                            Der Endpunkt ist bei "{end_point}".
                            Berücksichtige bei deiner Berechnung bitte folgenden Userprompt: "{user_prompt}".
                            Ermittele zuerst eine Wanderroute. Ermittele ausreichend Wegpunkte entlang der Route. 
                            Ermittel für diese Wegpunkte einen Eindeutigen Namen (inklusive Land und Stadt, mit dem der Punkt in Google Maps eindeutig identifizierbar ist),
                            sowie Adresse oder Koordinaten wenn es keine Adresse gibt. Gebe NUR eine JSON Datei zurück die wie folgt aufgebaut ist:
                            {{
                                "nameOfTheRoute": "", 
                                "startPoint": "", 
                                "waypoints": 
                                    [
                                        {{
                                            "id": 1, 
                                            "name": "", 
                                            "adress": "", 
                                            "coordinates": ""
                                        }}, 
                                        {{
                                            "id": 2, 
                                            "name": "", 
                                            "adress": "", 
                                            "coordinates": ""
                                        }}
                                    ]
                            }}.
                            Die Id soll bei jedem waypoint um 1 erhöht werden und einzigartig sein. Füge für jeden Wegpunkt ein Element "waypoint" mit den gesuchten Attributen 
                            hinzu und zähle dabei die Zahl am ende der Variable hoch. Setze Werte die du nicht findest (also z.b. die zu denen du keine Adresse findest) auf "null".'''

    return generated_prompt

def prompt_azure_ai(start_point: str, end_point: str, user_prompt: str | None = None) -> str:

    user_prompt = build_prompt(start_point, end_point, user_prompt)

    client = AzureOpenAI(
        azure_endpoint = "" # Hier muss der Endpunkt bei Azure rein
    )

    response = client.chat.completions.create(
        model = "",  # Hier muss das AzureAI Model rein
        messages = [
            {
                "role": "developer",
                "content": "Du bist ein erfahrener Wanderroutenersteller.",
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
    )
    return response.to_json()