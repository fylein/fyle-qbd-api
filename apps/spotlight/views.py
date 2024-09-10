import json
from django.http import JsonResponse
from django.db import transaction
from rest_framework import generics

from apps.spotlight.models import Query
from apps.spotlight.serializers import QuerySerializer

from .service import QueryService


# Create your views here.
class RecentQueryView(generics.ListAPIView):
    serializer_class = QuerySerializer
    # lookup_field = 'workspace_id'
    # lookup_url_kwarg = 'workspace_id'

    def get_queryset(self):
        filters = {
            'workspace_id': self.kwargs.get('workspace_id'),
            'user': self.request.user,
        }

        return Query.objects.filter(
            # **filters
        ).all().order_by("-created_at")[:5]


class QueryView(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        with transaction.atomic():
            payload = json.loads(request.body)
            user_query = payload["query"]
            suggestions = QueryService.get_suggestions(user_query=user_query)

            # Query.objects.create(
            #     query=user_query,
            #     workspace_id=1,
            #     _llm_response=suggestions,
            #     user=request.user
            # )
        return JsonResponse(data=suggestions["suggestions"])
