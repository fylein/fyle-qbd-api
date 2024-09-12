import uuid
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.integration_helper.models import Conversation
from apps.integration_helper.openai_utils import get_openai_response
from apps.integration_helper.prompt import PROMPT


class CoversationsView(generics.CreateAPIView, generics.DestroyAPIView):
    """
    View for creating and deleting conversations.
    """

    def create(self, request, *args, **kwargs):
        """
        Create a new conversation and get the first OpenAI response.
        """
        content = request.data.get('content')
        conversation_id = request.data.get('conversation_id')
        workspace_id = kwargs['workspace_id']

        if not content:
            return Response(
                {'error': 'content are required'}, status=status.HTTP_400_BAD_REQUEST
            )

        if not conversation_id:
            conversation_id = str(uuid.uuid4())

        Conversation.objects.update_or_create(
            defaults={'content': PROMPT},
            conversation_id=conversation_id,
            workspace_id=workspace_id,
            role='system'
        )

        conversation = Conversation.objects.create(
            conversation_id=conversation_id,
            workspace_id=workspace_id,
            role='user',
            content=content
        )

        messages = list(
            Conversation.objects.filter(
                conversation_id=conversation_id,
                workspace_id=workspace_id
            ).values('role', 'content').order_by('created_at'))

        assistant_response = get_openai_response(messages)

        Conversation.objects.create(
            conversation_id=conversation_id,
            workspace_id=workspace_id,
            role='assistant',
            content=assistant_response,
        )

        return Response(
            {
                'conversation_id': conversation.conversation_id,
                'content': assistant_response,
            },
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request, *args, **kwargs):
        """
        Clear the conversation history by deleting it using conversation_id.
        """
        workspace_id = kwargs['workspace_id']
        conversation_id = request.data.get('conversation_id')
        if not conversation_id:
            return Response(
                {
                    'error': 'conversation_id is required'
                }, status=status.HTTP_400_BAD_REQUEST
            )

        conversations = Conversation.objects.filter(
            conversation_id=conversation_id,
            workspace_id=workspace_id
        )

        if conversations.exists():
            conversations.delete()
        
        return Response(
            {
                'message': 'Conversation cleared'
            }, status=status.HTTP_200_OK
        )
