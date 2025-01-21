import base64
import json

import requests

from django.conf import settings
from fyle.platform import Platform
from rest_framework.exceptions import ValidationError

from apps.workspaces.models import Workspace, FyleCredential


def post_request(url, body, refresh_token=None):
    """
    Create a HTTP post request.
    """
    access_token = None
    api_headers = {
        'Content-Type': 'application/json',
    }
    if refresh_token:
        access_token = get_access_token(refresh_token)
        api_headers['Authorization'] = 'Bearer {0}'.format(access_token)

    response = requests.post(
        url,
        headers=api_headers,
        data=body
    )

    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise Exception(response.text)


def get_access_token(refresh_token: str) -> str:
    """
    Get access token from fyle
    """
    api_data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': settings.FYLE_CLIENT_ID,
        'client_secret': settings.FYLE_CLIENT_SECRET
    }

    return post_request(settings.FYLE_TOKEN_URI, body=json.dumps(api_data))['access_token']


def get_cluster_domain(refresh_token: str) -> str:
    """
    Get cluster domain name from fyle
    :param refresh_token: (str)
    :return: cluster_domain (str)
    """
    cluster_api_url = '{0}/oauth/cluster/'.format(settings.FYLE_BASE_URL)

    return post_request(cluster_api_url, {}, refresh_token)['cluster_domain']


def upload_iif_to_fyle(file_path: str, workspace_id: int):
    """
    Upload file to fyle
    :param file_path: (str)
    :param workspace_id: (int)
    :return: (dict)
    """
    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    
    platform = Platform(
        server_url='{}/platform/v1beta'.format(fyle_credentials.cluster_domain),
        token_url=settings.FYLE_TOKEN_URI,
        client_id=settings.FYLE_CLIENT_ID,
        client_secret=settings.FYLE_CLIENT_SECRET,
        refresh_token=fyle_credentials.refresh_token,
     )

    user_id = platform.v1beta.spender.my_profile.get()['data']['user']['id']

    file_payload = {
        'data': {
            'name': file_path.split('/')[-1],
            'type': 'INTEGRATION',
            'password': '',
            'user_id': user_id
        }
    }

    file = platform.v1beta.admin.files.create_file(file_payload)['data']

    bulk_generate_file_urls_payload = {
        'data': [
            {
                'id': file['id']
            }
        ]
    }

    upload_url = platform.v1beta.admin.files.bulk_generate_file_urls(
        bulk_generate_file_urls_payload
    )['data'][0]['upload_url']

    file_data = open(file_path, 'rb')
    file_data = base64.b64encode(file_data.read())

    platform.v1beta.admin.files.upload_file_to_aws(
        content_type='application/vnd.shana.informed.interchange', # Took the content type from Postman
        url=upload_url,
        data=file_data
    )

    return file


def download_iif_file(file_id: str, workspace_id: int):
    """
    Download file from fyle
    :param file_id: (str)
    :param workspace_id: (int)
    :return: (dict)
    """
    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    
    platform = Platform(
        server_url='{}/platform/v1beta'.format(fyle_credentials.cluster_domain),
        token_url=settings.FYLE_TOKEN_URI,
        client_id=settings.FYLE_CLIENT_ID,
        client_secret=settings.FYLE_CLIENT_SECRET,
        refresh_token=fyle_credentials.refresh_token,
     )

    bulk_generate_file_urls_payload = {
        'data': [
            {
                'id': file_id
            }
        ]
    }

    download_url = platform.v1beta.admin.files.bulk_generate_file_urls(
        bulk_generate_file_urls_payload
    )['data'][0]['download_url']

    return download_url


def assert_valid_request(workspace_id:int, org_id:str):
    """
    Assert if the request is valid by checking
    the url_workspace_id and fyle_org_id workspace
    """
    workspace = Workspace.objects.get(org_id=org_id)
    if workspace.id != workspace_id:
        raise ValidationError('Workspace mismatch')


def validate_webhook_request(org_id: str, action: str):
    """
    Validate the webhook request by checking the fyle_org_id workspace.
    """
    if not org_id:
        raise ValidationError('Org Id not found')

    if not action:
        raise ValidationError('Action not found in the webhook callback payload')
