import os
from openai import OpenAI
from apps.integration_helper.prompt import PROMPT
import json


# OpenAI API Key Setup

def get_openai_response(messages):
    """
    Send the conversation history (messages) to OpenAI and get a response.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(
        api_key=api_key
    )
    response = client.chat.completions.create(
        model="gpt-4o", 
        messages=messages,
        response_format={"type": "json_object"},
        max_tokens=1000,
        temperature=0,
    )

    return json.loads(response.choices[0].message.content)
