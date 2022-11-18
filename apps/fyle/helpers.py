from django.conf import settings

from fyle.platform import Platform


class PlatformConnector:
    """
    Fyle Platform utility functions
    """

    def __init__(self, refresh_token: str, cluster_domain: str):
        server_url = '{}/platform/v1'.format(cluster_domain)

        self.connection = Platform(
            server_url=server_url,
            token_url=settings.FYLE_TOKEN_URI,
            client_id=settings.FYLE_CLIENT_ID,
            client_secret=settings.FYLE_CLIENT_SECRET,
            refresh_token=refresh_token
        )
