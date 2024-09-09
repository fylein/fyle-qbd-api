import uuid
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.integration_helper.models import Conversation
from apps.integration_helper.openai_utils import get_openai_response
from apps.integration_helper.prompt import PROMPT
from fyle_accounting_mappings.models import DestinationAttribute


class ConversationViewSet(viewsets.ViewSet):
    """
    ViewSet for creating, retrieving, adding messages, and clearing conversations.
    """

    def create(self, request, *args, **kwargs):
        """
        Create a new conversation and get the first OpenAI response.
        """
        content = request.data.get('content')
        workspace_id = kwargs['workspace_id']

        if not content:
            return Response({"error": "content are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        conversation_id = str(uuid.uuid4())

        conversation = Conversation.objects.create(
            conversation_id=conversation_id, workspace_id=workspace_id, role='system', content=PROMPT
        )

        conversation = Conversation.objects.create(
            conversation_id=conversation_id, workspace_id=workspace_id, role='user', content=content
        )
        messages = [{"role": "system", "content": PROMPT}, {"role": "user", "content": content}]

        assistant_response = get_openai_response(messages)

        Conversation.objects.create(conversation_id=conversation_id, workspace_id=workspace_id, role="assistant", content=assistant_response)

        return Response({
            'conversation_id': conversation.conversation_id,
            'assistant_response': assistant_response
        }, status=status.HTTP_201_CREATED)
    

    @action(detail=True, methods=["post"])
    def add_message(self, request, pk=None, *args, **kwargs):
        """
        Add a new message to an existing conversation using conversation_id and get an OpenAI response.
        """
        content = request.data.get("content")
        conversation_id = pk
        workspace_id = kwargs['workspace_id']

        if not content:
            return Response(
                {"error": "content are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if not Conversation.objects.filter(conversation_id=pk).first():
            return Response(
                {"error": "Conversation id doesn't exists!"}
            )
        
        messages = list(Conversation.objects.filter(conversation_id=conversation_id, workspace_id=workspace_id).values("role", "content").order_by('created_at'))

        messages.append({"role": "user", "content": content})
        Conversation.objects.create(conversation_id=conversation_id, workspace_id=workspace_id, role="user", content=content)


        assistant_response = get_openai_response(messages)
        Conversation.objects.create(conversation_id=conversation_id, workspace_id=workspace_id, role="assistant", content=assistant_response)
        
        return Response(
            {"assistant_response": assistant_response}, status=status.HTTP_201_CREATED
        )
    

    @action(detail=True, methods=["delete"])
    def clear(self, request, pk=None, *args, **kwargs):
        """
        Clear the conversation history by deleting it using conversation_id.
        """
        workspace_id = kwargs['workspace_id']
        conversations = Conversation.objects.filter(conversation_id=pk, workspace_id=workspace_id)
        if conversations.exists():
            conversations.delete()
            return Response(
                {"message": "Conversation cleared"}, status=status.HTTP_200_OK
            )

        return Response(
            {"error": "Conversation not found"}, status=status.HTTP_404_NOT_FOUND
        )
