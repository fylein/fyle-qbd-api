from django.conf import settings
from fyle.platform import Platform

from apps.workspaces.models import FyleCredential

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
