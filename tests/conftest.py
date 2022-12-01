"""
Fixture configuration for all the tests
"""
from unittest import mock
import pytest
from rest_framework.test import APIClient

from .test_fyle.fixtures import fixtures as fyle_fixtures


@pytest.fixture
def api_client():
    """
    API Client to help test views
    """
    return APIClient()

@pytest.fixture(scope="session", autouse=True)
def default_session_fixture(request):
    patched_1 = mock.patch(
        'fyle_rest_auth.authentication.get_fyle_admin',
        return_value=fyle_fixtures['get_my_profile']
    )
    patched_1.__enter__()

    patched_2 = mock.patch(
        'fyle.platform.internals.auth.Auth.update_access_token',
        return_value='asnfalsnkflanskflansfklsan'
    )
    patched_2.__enter__()

    patched_3 = mock.patch(
        'apps.fyle.helpers.post_request',
        return_value={
            'access_token': 'easnfkjo12233.asnfaosnfa.absfjoabsfjk',
            'cluster_domain': 'https://staging.fyle.tech'
        }
    )
    patched_3.__enter__()

    patched_4 = mock.patch(
        'fyle.platform.apis.v1beta.spender.MyProfile.get',
        return_value=fyle_fixtures['get_my_profile']
    )
    patched_4.__enter__()

    def unpatch():
        patched_1.__exit__()
        patched_2.__exit__()
        patched_3.__exit__()
        patched_4.__exit__()

    request.addfinalizer(unpatch)
