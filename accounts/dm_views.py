from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import DirectMessage, CustomUser
from .serializers import DirectMessageSerializer

class DirectMessageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Send a DM from the authenticated user to another user.
        Expect JSON with 'receiver' (ID) and 'message'.
        """
        serializer = DirectMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(sender=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, user_id):
        """
        Retrieve the conversation between the authenticated user and another user (user_id).
        """
        other_user = get_object_or_404(CustomUser, id=user_id)
        messages = DirectMessage.objects.filter(
            Q(sender=request.user, receiver=other_user) | Q(sender=other_user, receiver=request.user)
        ).order_by('created_at')
        serializer = DirectMessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
