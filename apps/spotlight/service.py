from dataclasses import dataclass
from typing import Callable, Dict
from django.db import transaction
import json

import requests

from apps.fyle.helpers import get_access_token
from apps.spotlight.models import CopyExportSettings
from apps.workspaces.models import ExportSettings, FyleCredential
from .prompts.support_genie import PROMPT as SUPPORT_GENIE_PROMPT
from .prompts.spotlight_prompt import PROMPT as SPOTLIGHT_PROMPT
from .prompts.suggestion_context_page_prompt import SUGGESTION_PROMPT

from . import llm


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

class SuggestionService:
    @classmethod
    def get_suggestions(cls, *, user_query: str) -> str:
        formatted_prompt = SUGGESTION_PROMPT.format(
            user_query=user_query
        )

        return llm.get_openai_response(system_prompt=formatted_prompt)

class ActionService:

    @classmethod
    def _get_action_function_from_code(cls, *, code: str) -> Callable:
        code_to_function_map = {
            "trigger_export": cls.trigger_export,
            "set_reimbursable_expenses_export_module_bill": cls.set_reimbursable_expenses_export_module_bill,
            "set_reimbursable_expenses_export_module_journal_entry": cls.set_reimbursable_expenses_export_module_journal_entry,
            "set_reimbursable_expenses_export_grouping_expense": cls.set_reimbursable_expenses_export_grouping_expense,
            "set_reimbursable_expenses_export_grouping_report": cls.set_reimbursable_expenses_export_grouping_report,
            "set_reimbursable_expenses_export_state_processing": cls.set_reimbursable_expenses_export_state_processing,
            "set_reimbursable_expenses_export_state_paid": cls.set_reimbursable_expenses_export_state_paid,
            "set_customer_field_mapping_to_project": cls.set_customer_field_mapping_to_project,
            "set_customer_field_mapping_to_cost_center": cls.set_customer_field_mapping_to_cost_center,
            "set_class_field_mapping_to_project": cls.set_class_field_mapping_to_project,
            "set_class_field_mapping_to_cost_center": cls.set_class_field_mapping_to_cost_center,
            "set_corporate_credit_card_expenses_export_credit_card_purchase": cls.set_cc_export_to_corporate_card_purchase,
            "set_corporate_credit_card_expenses_export_journal_entry": cls.set_cc_export_to_journal_entry,
            "set_corporate_credit_card_expenses_export_grouping_report": cls.set_cc_grouping_to_report,
            "set_corporate_credit_card_expenses_export_grouping_expense": cls.set_cc_grouping_to_expense,
            "disable_reimbursable_expenses_export": cls.disable_reimbursable_expenses_export,
            "enable_reimbursable_expenses_export": cls.enable_reimbursable_expenses_export,
            "disable_corporate_card_expenses_export": cls.disable_corporate_card_expenses_export,
            "enable_corporate_card_expenses_export": cls.enable_corporate_card_expenses_export
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
    def set_reimbursable_expenses_export_module_journal_entry(cls, *, workspace_id: int):
        with transaction.atomic():
            export_settings = ExportSettings.objects.filter(
                workspace_id=workspace_id
            ).first()
            if export_settings is None:
                return ActionResponse(message="Failed to set reimbursable expense export type set to Journal Entry", is_success=False)
            else:
                export_settings.reimbursable_expenses_export_type = 'JOURNAL_ENTRY'
                export_settings.save()
                return ActionResponse(message="Reimbursable expense export type set to Journal Entry", is_success=True)

    @classmethod
    def set_reimbursable_expenses_export_grouping_expense(cls, *, workspace_id: int):
        with transaction.atomic():
            export_settings = ExportSettings.objects.filter(
                workspace_id=workspace_id
            ).first()
            if export_settings is None:
                return ActionResponse(message="Failed to set reimbursable expense export grouping to Expenses", is_success=False)
            else:
                export_settings.reimbursable_expense_grouped_by = 'EXPENSE'
                export_settings.save()
                return ActionResponse(message="Reimbursable expense export group set to Expenses", is_success=True)

    @classmethod
    def set_reimbursable_expenses_export_grouping_report(cls, *, workspace_id: int):
        with transaction.atomic():
            export_settings = ExportSettings.objects.filter(
                workspace_id=workspace_id
            ).first()
            if export_settings is None:
                return ActionResponse(message="Failed to set reimbursable expense export grouping to Report", is_success=False)
            else:
                export_settings.reimbursable_expense_grouped_by = 'REPORT'
                export_settings.save()
                return ActionResponse(message="Reimbursable expense export group set to Report", is_success=True)

    @classmethod
    def set_reimbursable_expenses_export_state_processing(cls, *, workspace_id: int):
        with transaction.atomic():
            export_settings = ExportSettings.objects.filter(
                workspace_id=workspace_id
            ).first()
            if export_settings is None:
                return ActionResponse(message="Failed to set reimbursable expense export state to Processing", is_success=False)
            else:
                export_settings.reimbursable_expense_state = 'PAYMENT_PROCESSING'
                export_settings.save()
                return ActionResponse(message="Reimbursable expense export state set to Processing", is_success=True)

    @classmethod
    def set_reimbursable_expenses_export_state_paid(cls, *, workspace_id: int):
        with transaction.atomic():
            export_settings = ExportSettings.objects.filter(
                workspace_id=workspace_id
            ).first()
            if export_settings is None:
                return ActionResponse(message="Failed to set reimbursable expense export state to Paid", is_success=False)
            else:
                export_settings.reimbursable_expense_state = 'PAID'
                export_settings.save()
                return ActionResponse(message="Reimbursable expense export state set to Paid", is_success=True)

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
    def set_cc_export_to_corporate_card_purchase(cls, *, workspace_id: int):
        with transaction.atomic():
            export_settings = ExportSettings.objects.filter(workspace_id=workspace_id).first()
            if export_settings:
                export_settings.credit_card_expense_export_type = 'CREDIT_CARD_PURCHASE'
                export_settings.save()
                return ActionResponse(message="Successfully set corporate card expense as Credit Card Purchase", is_success=True)
            
            return ActionResponse(message="Export settings doesn't exists!", is_success=False)


    @classmethod
    def set_cc_export_to_journal_entry(cls, *, workspace_id: int):
        with transaction.atomic():
            export_settings = ExportSettings.objects.filter(workspace_id=workspace_id).first()
            if export_settings:
                export_settings.credit_card_expense_export_type = 'JOURNAL_ENTRY'
                export_settings.save()
                return ActionResponse(message="Successfully set corporate card expense as JOURNAL ENTRY", is_success=True)
            
            return ActionResponse(message="Export settings doesn't exists!", is_success=False)

    @classmethod
    def set_cc_grouping_to_report(cls, *, workspace_id: int):
        with transaction.atomic():
            export_settings = ExportSettings.objects.filter(workspace_id=workspace_id).first()
            if export_settings:
                if export_settings.credit_card_expense_export_type == 'CREDIT_CARD_PURCHASE':
                    return ActionResponse(message='For Corporate Credit Purchase Export type expenses cannot be grouped by report', is_success=False)
                else:
                    export_settings.credit_card_expense_grouped_by = 'REPORT'
                    export_settings.save()
                    return ActionResponse(message='Succesfully set corporate card group by to Report', is_success=True)
            
            return ActionResponse(message="Export settings doesn't exists!", is_success=False)


    @classmethod
    def set_cc_grouping_to_expense(cls, *, workspace_id: int):
        with transaction.atomic():
            export_settings = ExportSettings.objects.filter(workspace_id=workspace_id).first()
            if export_settings:
                if export_settings.credit_card_expense_export_type == 'CREDIT_CARD_PURCHASE':
                    return ActionResponse(message='Already set to expense', is_success=True)
                else:
                    export_settings.credit_card_expense_grouped_by = 'EXPENSE'
                    export_settings.save()
                    return ActionResponse(message='Succesfully set corporate card group by to EXPENSE', is_success=True)
            
            return ActionResponse(message="Export settings doesn't exists!", is_success=False)


    @classmethod
    def set_customer_field_mapping_to_project(cls, *, workspace_id: int):
        access_token = cls.get_access_token(workspace_id=workspace_id)
        headers = cls.get_headers(access_token=access_token)
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        url = f'http://localhost:8000/api/workspaces/{workspace_id}/field_mappings/'
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        action_response = requests.get(url, headers=headers)
        action_response= action_response.json()
        if action_response.get('project_type') != 'PROJECT' and action_response.get('class_type') != 'COST_CENTER':
            action_response['project_type'] = 'PROJECT'
            post_response = requests.post(url, headers=headers, data=json.dumps(action_response))
            return ActionResponse(message="Field mapping updated successfully", is_success=True)
        return ActionResponse(message="Field mapping already exists", is_success=False)
    
    @classmethod
    def set_customer_field_mapping_to_cost_center(cls, *, workspace_id: int):
        access_token = cls.get_access_token(workspace_id=workspace_id)
        headers = cls.get_headers(access_token=access_token)
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        url = f'http://localhost:8000/api/workspaces/{workspace_id}/field_mappings/'

        action_response = requests.get(url, headers=headers)
        action_response= action_response.json()
        if action_response.get('project_type') != 'COST_CENTER' and action_response.get('class_type') != 'PROJECT':
            action_response['project_type'] = 'COST_CENTER'
            post_response = requests.post(url, headers=headers, data=json.dumps(action_response))
            return ActionResponse(message="Field mapping updated successfully", is_success=True)
        return ActionResponse(message="Field mapping already exists", is_success=False)
    
    @classmethod
    def set_class_field_mapping_to_project(cls, *, workspace_id: int):
        access_token = cls.get_access_token(workspace_id=workspace_id)
        headers = cls.get_headers(access_token=access_token)
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        url = f'http://localhost:8000/api/workspaces/{workspace_id}/field_mappings/'

        action_response = requests.get(url, headers=headers)
        action_response= action_response.json()
        if action_response.get('project_type') != 'PROJECT' and action_response.get('class_type') != 'COST_CENTER':
            action_response['class_type'] = 'PROJECT'
            post_response = requests.post(url, headers=headers, data=json.dumps(action_response))
            return ActionResponse(message="Field mapping updated successfully", is_success=True)
        return ActionResponse(message="Field mapping already exists", is_success=False)
    
    @classmethod
    def set_class_field_mapping_to_cost_center(cls, *, workspace_id: int):
        access_token = cls.get_access_token(workspace_id=workspace_id)
        headers = cls.get_headers(access_token=access_token)
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        url = f'http://localhost:8000/api/workspaces/{workspace_id}/field_mappings/'

        action_response = requests.get(url, headers=headers)
        action_response= action_response.json()
        if action_response.get('project_type') != 'COST_CENTER' and action_response.get('class_type') != 'PROJECT':
            action_response['class_type'] = 'COST_CENTER'
            post_response = requests.post(url, headers=headers, data=json.dumps(action_response))
            return ActionResponse(message="Field mapping updated successfully", is_success=True)
        return ActionResponse(message="Field mapping already exists", is_success=False)

    @classmethod
    def enable_reimbursable_expenses_export(cls, *, workspace_id: int):
        fields_for_reimbursable = ['reimbursable_expenses_export_type', 'reimbursable_expense_state', 'reimbursable_expense_date', 
                                'reimbursable_expense_grouped_by', 'bank_account_name']
        
        with transaction.atomic():
            export_settings = ExportSettings.objects.filter(workspace_id=workspace_id).first()
            if export_settings:
                if export_settings.reimbursable_expenses_export_type is None:
                    copied_export_settings = CopyExportSettings.objects.filter(workspace_id=workspace_id).first()
                    if copied_export_settings:
                        for field in fields_for_reimbursable:
                            setattr(export_settings, field, copied_export_settings.reimbursable_export_setting[field])

                        export_settings.save()
                        return ActionResponse(message='Successfully enabled reimbursable expense', is_success=True)
                else:
                    return ActionResponse(message='Reimbursable Expense is already enabled', is_success=True)
            
            return ActionResponse(message="Export settings doesn't exists", is_success=False)

    @classmethod
    def disable_reimbursable_expenses_export(cls, *, workspace_id: int):
        fields_for_reimbursable = ['reimbursable_expenses_export_type', 'reimbursable_expense_state', 'reimbursable_expense_date', 
                                'reimbursable_expense_grouped_by', 'bank_account_name']
        with transaction.atomic():
            export_settings = ExportSettings.objects.filter(workspace_id=workspace_id).first()
            if export_settings:
                if export_settings.reimbursable_expenses_export_type is not None:
                    copied_export_settings, _  = CopyExportSettings.objects.get_or_create(workspace_id=workspace_id,
                                                            defaults={'reimbursable_export_setting': {}, 'ccc_export_setting': {}})
                    reimbursable_export_setting = copied_export_settings.reimbursable_export_setting or {}

                    for field in fields_for_reimbursable:
                        reimbursable_export_setting[field] = getattr(export_settings, field, None)
                        setattr(export_settings, field, None)
                    
                    copied_export_settings.reimbursable_export_setting = reimbursable_export_setting
                    
                    export_settings.save()
                    copied_export_settings.save()

                    return ActionResponse(message='Reimbursable Expense successfully disabled!', is_success=True)

                else:
                    return ActionResponse(message='Reimbursable Expense is already disabled', is_success=True)
            
            return ActionResponse(message="Export settings doesn't exists", is_success=False)
    
    @classmethod
    def enable_corporate_card_expenses_export(cls, *, workspace_id: int):
        fields_for_ccc = ['credit_card_expense_export_type', 'credit_card_expense_state', 'credit_card_entity_name_preference', 
                                'credit_card_account_name', 'credit_card_expense_grouped_by', 'credit_card_expense_date']
        
        with transaction.atomic():
            export_settings = ExportSettings.objects.filter(workspace_id=workspace_id).first()
            if export_settings:
                if export_settings.credit_card_expense_export_type is None:
                    copied_export_settings = CopyExportSettings.objects.filter(workspace_id=workspace_id).first()
                    if copied_export_settings:
                        for field in fields_for_ccc:
                            setattr(export_settings, field, copied_export_settings.ccc_export_setting[field])

                        export_settings.save()
                        return ActionResponse(message='Successfully enabled Corporate expense', is_success=True)
                else:
                    return ActionResponse(message='Corporate Expense is already enabled', is_success=True)
            
            return ActionResponse(message="Export settings doesn't exists", is_success=False)
    
    @classmethod
    def disable_corporate_card_expenses_export(cls, *, workspace_id: int):
        fields_for_ccc = ['credit_card_expense_export_type', 'credit_card_expense_state', 'credit_card_entity_name_preference', 
                                'credit_card_account_name', 'credit_card_expense_grouped_by', 'credit_card_expense_date']
        with transaction.atomic():
            export_settings = ExportSettings.objects.filter(workspace_id=workspace_id).first()
            if export_settings:
                if export_settings.credit_card_expense_export_type is not None:
                    copied_export_settings, _  = CopyExportSettings.objects.get_or_create(workspace_id=workspace_id,
                                                            defaults={'reimbursable_export_setting': {}, 'ccc_export_setting': {}})
                    ccc_export_setting = copied_export_settings.ccc_export_setting or {}

                    for field in fields_for_ccc:
                        ccc_export_setting[field] = getattr(export_settings, field, None)
                        setattr(export_settings, field, None)
                    
                    copied_export_settings.ccc_export_setting = ccc_export_setting
                    
                    export_settings.save()
                    copied_export_settings.save()

                    return ActionResponse(message='Corporate Expense successfully disabled!', is_success=True)

                else:
                    return ActionResponse(message='Corporate Expense is already disabled', is_success=True)
            
            return ActionResponse(message="Export settings doesn't exists", is_success=False)

    @classmethod
    def action(cls, *, code: str, workspace_id: str):
        action_function = cls._get_action_function_from_code(code=code)
        return action_function(workspace_id=workspace_id)
