import json
from django.http import JsonResponse
from django.db import transaction
from rest_framework import generics
import requests
from django_q.tasks import async_task

from apps.spotlight.models import Query
from apps.spotlight.serializers import QuerySerializer

from .service import ActionService, HelpService, QueryService
from apps.workspaces.models import FyleCredential
from apps.fyle.helpers import get_access_token

code_action_map = {
    "trigger_export": 'http://localhost:8000/api/workspaces/2/trigger_export/'
}

# Create your views here.
# class RecentQueryView(generics.ListAPIView):
#     serializer_class = QuerySerializer
#     # lookup_field = 'workspace_id'
#     # lookup_url_kwarg = 'workspace_id'

#     def get_queryset(self):
#         filters = {
#             # 'workspace_id': self.kwargs.get('workspace_id'),
#             # 'user': self.request.user,
#             'workspace_id': 1,
#             'user_id': 1,
#         }

#         return Query.objects.filter(
#             **filters
#         ).all().order_by("-created_at")[:5]


class RecentQueryView(generics.ListAPIView):
    serializer_class = QuerySerializer
    lookup_field = 'workspace_id'
    lookup_url_kwarg = 'workspace_id'

    def get(self, request, *args, **kwargs):
        filters = {
            'workspace_id': self.kwargs.get('workspace_id'),
            'user': self.request.user,
        }

        _recent_queries =  Query.objects.filter(
            **filters
        ).all().order_by("-created_at")[:5]

        # recent_queries = []
        # for query in _recent_queries:
        #     recent_queries.append({
        #         "query": query.query,
        #         "suggestions": query._llm_response["suggestions"]
        #     })
        recent_queries = [query.query for query in _recent_queries]
        return JsonResponse(data={"recent_queries": recent_queries}, safe=False)


class QueryView(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        workspace_id = self.kwargs.get('workspace_id')
        user = self.request.user
        with transaction.atomic():
            payload = json.loads(request.body)
            user_query = payload["query"]
            suggestions = QueryService.get_suggestions(user_query=user_query)

            Query.objects.create(
                query=user_query,
                workspace_id=workspace_id,
                _llm_response=suggestions,
                user_id=user.id
            )
        return JsonResponse(data=suggestions["suggestions"])


class HelpQueryView(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        payload = json.loads(request.body)
        user_query = payload["query"]
        support_response = HelpService.get_support_response(user_query=user_query)
        return JsonResponse(data={"message": support_response})


class ActionQueryView(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        workspace_id = self.kwargs.get('workspace_id')
        payload = json.loads(request.body)
        code = payload["code"]

        try:
            ActionService.action(code=code, workspace_id=workspace_id)
            return JsonResponse(data={"message": "Action triggered successfully"}, status=200)
        except Exception as e:
            print(e)
            return JsonResponse(data={"message": "Action failed"}, status=500)
