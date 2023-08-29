import logging

from django.conf import settings
from fyle.platform import Platform

from apps.workspaces.models import FyleCredential

from .models import QBDMapping

logger = logging.getLogger(__name__)

def sync_card(workspace_id: int):
    try:
        fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
        platform = Platform(
	        server_url='{}/platform/v1beta'.format(fyle_credentials.cluster_domain),
	        token_url=settings.FYLE_TOKEN_URI,
		    client_id=settings.FYLE_CLIENT_ID,
		    client_secret=settings.FYLE_CLIENT_SECRET,
	        refresh_token=fyle_credentials.refresh_token,
        )
        query = {
	        'order': 'updated_at.desc',
	    }
        generator = platform.v1beta.admin.corporate_cards.list_all(query)
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
                QBDMapping.update_or_create_mapping_objects(card_attributes, workspace_id)

    except FyleCredential.DoesNotExist:
        logger.info('Fyle credentials not found %s', workspace_id)

    except Exception:
        logger.exception('Something unexpected happened workspace_id: %s', workspace_id)

