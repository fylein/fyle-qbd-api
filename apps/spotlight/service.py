from dataclasses import dataclass
from typing import Callable, Dict
from django.db import transaction

import requests

from apps.fyle.helpers import get_access_token
from apps.workspaces.models import ExportSettings, FyleCredential
from .prompts.support_genie import PROMPT as SUPPORT_GENIE_PROMPT
from .prompts.spotlight_prompt import PROMPT as SPOTLIGHT_PROMPT

from . import llm

code_action_map = {
    "trigger_export": 'http://localhost:8000/api/workspaces/2/trigger_export/'
}


@dataclass
class ActionResponse:
    message: str = None
    is_success: bool = None


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
            "trigger_export": cls.trigger_export,
            "set_reimbursable_expenses_export_module_bill": cls.set_reimbursable_expenses_export_module_bill
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
    def set_reimbursable_expenses_export_module_bill(cls, *, workspace_id: int):
        with transaction.atomic():
            export_settings = ExportSettings.objects.filter(
                workspace_id=workspace_id
            ).first()
            if export_settings is None:
                return ActionResponse(message="Failed to set reimbursable expense export type set to Bill", is_success=False)
            else:
                export_settings.reimbursable_expenses_export_type = 'BILL'
                export_settings.save()
                return ActionResponse(message="Reimbursable expense export type set to Bill", is_success=True)

    @classmethod
    def trigger_export(cls, *, workspace_id: int):
        access_token = cls.get_access_token(workspace_id=workspace_id)
        headers = cls.get_headers(access_token=access_token)
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        url = f'http://localhost:8000/api/workspaces/{workspace_id}/trigger_export/'
        action_response = requests.post(url, json={}, headers=headers)
        if action_response.status_code == 200:
            return ActionResponse(message="Export triggered successfully", is_success=True)
        return ActionResponse(message="Export triggered failed", is_success=False)

    @classmethod
    def action(cls, *, code: str, workspace_id: str) -> ActionResponse:
        action_function = cls._get_action_function_from_code(code=code)
        return action_function(workspace_id=workspace_id)
