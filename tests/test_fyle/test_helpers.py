import json
from apps.fyle.helpers import post_request


def test_post_request(mocker):
    class MockResponse:
        def __init__(self, text, status_code):
            self.text = text
            self.status_code = status_code

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
    mocker.patch('requests.post', return_value=(MockResponse("""{"data": "Airline Posted"}""", 200)))
    post_request(url, body=body)
