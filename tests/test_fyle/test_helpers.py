import json
from apps.fyle.helpers import post_request
from unittest import mock


def test_post_request(mocker):
    url = 'https://api.instantwebtools.net/v1/airlines'
    
    body = {
        'name': 'Sri Lankan Airways',
        'country': 'Sri Lanka',
        'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/9/9b/Qatar_Airways_Logo.svg/sri_lanka.png',
        'slogan': 'From Sri Lanka',
        'head_quaters': 'Katunayake, Sri Lanka',
        'website': 'www.srilankaairways.com',
        'established': '1990'
    }
    mocker.patch('apps.fyle.helpers.post_request', return_value=[])
    post_request(url, body=json.dumps(body))
