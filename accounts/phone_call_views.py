from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from .models import CustomUser, Interaction

class LogPhoneCallView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Logs a phone call interaction between the authenticated user and a friend.
        Expects JSON payload with 'to_user_id'.
        """
        to_user_id = request.data.get("to_user_id")
        if not to_user_id:
            return Response({"error": "to_user_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        friend = get_object_or_404(CustomUser, id=to_user_id)
        
        # Create phone call interaction records for both directions.
        Interaction.objects.create(
            from_user=request.user,
            to_user=friend,
            interaction_type='phone_call',
            points=5  # Base points for a phone call
        )
        Interaction.objects.create(
            from_user=friend,
            to_user=request.user,
            interaction_type='phone_call',
            points=5
        )
        
        return Response({"message": "Phone call logged successfully."}, status=status.HTTP_201_CREATED)
