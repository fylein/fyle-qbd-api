from django.urls import reverse
import pytest


@pytest.mark.django_db(databases=['default'])
def test_get_profile_view(api_client, test_connection):
    
    url = reverse('user-profile')
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format('Dummy.Access.Token'))

    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data['data']['user_id'] == 'usqywo0f3nBY'
