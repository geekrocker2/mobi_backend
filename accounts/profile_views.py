from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import CustomUser
from .serializers import ProfileSerializer

class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id=None):
        # If user_id is provided, we fetch that user's profile.
        # For simplicity, if not provided, we return the logged-in user's profile.
        if user_id:
            try:
                profile = CustomUser.objects.get(id=user_id)
                # TODO: You can add a check here to ensure that the current user is friends with the profile user
            except CustomUser.DoesNotExist:
                return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            profile = request.user

        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, user_id=None):
        # Allow users to update only their own profile
        if user_id and int(user_id) != request.user.id:
            return Response({"error": "You can only update your own profile."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
