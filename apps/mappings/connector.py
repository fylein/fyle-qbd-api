from django.conf import settings
from fyle.platform import Platform

from apps.workspaces.models import FieldMapping, FyleCredential

from .models import QBDMapping


class PlatformConnector:

    def __init__(self, workspace_id: int):

        fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    
        self.platform = Platform(
            server_url='{}/platform/v1beta'.format(fyle_credentials.cluster_domain),
            token_url=settings.FYLE_TOKEN_URI,
            client_id=settings.FYLE_CLIENT_ID,
            client_secret=settings.FYLE_CLIENT_SECRET,
            refresh_token=fyle_credentials.refresh_token,
        )

        self.workspace_id = workspace_id

    def sync_corporate_card(self):
        """
        Sync Cards will sync the corporate cards details from fyle to qbd db
        """

        query = {
            'order': 'updated_at.desc',
        }

        generator = self.platform.v1beta.admin.corporate_cards.list_all(query)

        for items in generator:
            card_attributes = []
            unique_card_numbers = []
            for card in items['data']:
                value = '{} - {}'.format(
                    card['bank_name'],
                    card['card_number'][-6:].replace('-', '')
                )

                if value not in unique_card_numbers:
                    unique_card_numbers.append(value)
                    card_attributes.append({
                        'attribute_type': 'CORPORATE_CARD',
                        'value': value,
                        'source_id': card['id'],                 
                    })

            if len(card_attributes) > 0:
                QBDMapping.update_or_create_mapping_objects(card_attributes, self.workspace_id)

    def sync_custom_field(
            self,
            field_mapping: FieldMapping,
            source_type: str = None,
            sync_expense_custom_field_names: bool = False
    ):
        """ 
        Sync custom fields that are mapped to the Item in the FieldMapping
        :source_type: The Custom Field Items is mapped to
        :field_mapping: FieldMapping instance
        :sync_custom_field_options: bool, when set to true, we create the QBDMapping 
                    else only update the values of custom_fields in field_mapping table
        """

        query = {
        'order': 'updated_at.desc',
        'is_custom': 'eq.true',
        'type': 'eq.SELECT',
        'is_enabled': 'eq.true'
        }
        custom_field_gen = self.platform.v1beta.admin.expense_fields.list_all(query)
        if source_type:
            query = QBDMapping.objects.filter(workspace_id=self.workspace_id, attribute_type=source_type)
            existing_source_attributes = query.values_list('source_value', flat=True)
        
        distinct_custom_fields = []
        source_values = []
        
        for custom_fields in custom_field_gen:
            for custom_field in custom_fields.get('data'):
                distinct_custom_fields.append(custom_field['field_name'])
                if source_type and source_type == custom_field['field_name']:
                    source_values.extend(custom_field['options'])

        if distinct_custom_fields and sync_expense_custom_field_names:
            field_mapping.custom_fields = distinct_custom_fields
            field_mapping.save()
            
        if sync_expense_custom_field_names:
            source_attributes = []
            for source_value in source_values:
                if source_value not in existing_source_attributes:
                    source_attributes.append({
                        'attribute_type': source_type,
                        'value': source_value,
                        'source_id': source_value
                    })
            if source_attributes:
                QBDMapping.update_or_create_mapping_objects(source_attributes, self.workspace_id)

    def sync_projects(self, source_type: str):
        """ 
        Sync PROJECT as Item
        """
        
        query = {
        'order': 'updated_at.desc'
        }
        projects_generator = self.platform.v1beta.admin.projects.list_all(query)
        existing_projects = QBDMapping.objects.filter(workspace_id=self.workspace_id, attribute_type=source_type)
        
        source_attributes = []
        
        for projects in projects_generator:
            for project in projects.get('data'):
                if project['sub_project']:
                    project['name'] = '{0} / {1}'.format(project['name'], project['sub_project'])
                    if project['name'] not in existing_projects:
                        source_attributes.append({
                            'attribute_type': source_type,
                            'value': project['name'],
                            'source_id': project['id']
                        })
                        
                        
        if source_attributes:
            QBDMapping.update_or_create_mapping_objects(source_attributes, self.workspace_id)

    def sync_cost_center(self, source_type: str):
        """ 
        Sync COST CENTER as Item
        """
        
        query = {
        'order': 'updated_at.desc'
        }
        cost_center_generator = self.platform.v1beta.admin.cost_centers.list_all(query)
        existing_cost_centers = QBDMapping.objects.filter(workspace_id=self.workspace_id, attribute_type=source_type)
        
        source_attributes = []
        
        for cost_centers in cost_center_generator:
            for cost_center in cost_centers.get('data'):
                if cost_center not in existing_cost_centers:
                        source_attributes.append({
                            'attribute_type': source_type,
                            'value': cost_center,
                            'source_id': cost_center
                        })
                        
                        
        if source_attributes:
            QBDMapping.update_or_create_mapping_objects(source_attributes, self.workspace_id)