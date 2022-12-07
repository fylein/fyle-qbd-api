from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from fyle_rest_auth.models import AuthToken

from fyle_integrations_platform_connector import PlatformConnector

from apps.workspaces.models import FyleCredential
from apps.fyle.helpers import get_cluster_domain


class UserProfileView(generics.RetrieveAPIView):
    """
    Get Fyle User Profile of the logged in user
    """
    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request, *args, **kwargs):
        """
        Get User Details
        """
        refresh_token = AuthToken.objects.get(user__user_id=request.user).refresh_token

        cluster_domain = get_cluster_domain(refresh_token)

        fyle_credentials = FyleCredential(
            cluster_domain=cluster_domain,
            refresh_token=refresh_token
        )

        platform = PlatformConnector(fyle_credentials)

        employee_profile = platform.connection.v1beta.spender.my_profile.get()

        return Response(
            data=employee_profile,
            status=status.HTTP_200_OK
        )
