from typing import Callable, Dict

import requests

from apps.fyle.helpers import get_access_token
from apps.workspaces.models import FyleCredential
from .prompts.support_genie import PROMPT as SUPPORT_GENIE_PROMPT
from .prompts.spotlight_prompt import PROMPT as SPOTLIGHT_PROMPT

from . import llm

code_action_map = {
    "trigger_export": 'http://localhost:8000/api/workspaces/2/trigger_export/'
}


class HelpService:
    @classmethod
    def extract_citations(cls, *, citations: list) -> list:
        urls = set()
        for citation in citations:
            for reference in citation["retrievedReferences"]:
                urls.add(reference['location']['webLocation']['url'])
        return list(urls)

    @classmethod
    def format_response(cls, *, response: Dict) -> str:
        # Extract citations
        citations = cls.extract_citations(citations=response["citations"])

        # Format response
        formatted_response = response["output"]["text"]
        if citations:
            formatted_response = formatted_response + "\n\n*Sources:*\n" + "\n".join(citations)

        return formatted_response

    @classmethod
    def get_support_response(cls, *, user_query: str) -> str:
        response = llm.get_support_response_from_bedrock(
            prompt_template=SUPPORT_GENIE_PROMPT,
            input_message=user_query
        )

        return cls.format_response(response=response)


class QueryService:
    @classmethod
    def get_suggestions(cls, *, user_query: str) -> str:
        formatted_prompt = SPOTLIGHT_PROMPT.format(
            user_query=user_query
        )
        return llm.get_openai_response(system_prompt=formatted_prompt)


class ActionService:

    @classmethod
    def _get_action_function_from_code(cls, *, code: str) -> Callable:
        code_to_function_map = {
            "trigger_export": cls.trigger_export
        }
        return code_to_function_map[code]

    @classmethod
    def get_headers(cls, *, access_token: str) -> Dict:
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

    @classmethod
    def get_access_token(cls, *, workspace_id: int) -> str:
        creds = FyleCredential.objects.get(workspace_id=workspace_id)
        return get_access_token(creds.refresh_token)

    @classmethod
    def trigger_export(cls, *, workspace_id: int):
        access_token = cls.get_access_token(workspace_id=workspace_id)
        headers = cls.get_headers(access_token=access_token)
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        url = 'http://localhost:8000/api/workspaces/2/trigger_export/'
        action_response = requests.post(url, json={}, headers=headers)

    @classmethod
    def action(cls, *, code: str, workspace_id: str):
        action_function = cls._get_action_function_from_code(code=code)
        action_function(workspace_id=workspace_id)
