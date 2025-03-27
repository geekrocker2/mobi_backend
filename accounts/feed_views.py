from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.utils import timezone
from .models import CheckIn
from .checkin_serializers import CheckInSerializer

class FeedView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Get the current logged-in user
        user = request.user
        now = timezone.now()

        # Get the friends of the current user
        # This assumes you have a ManyToManyField 'friends' in your CustomUser model
        friends = user.friends.all()

        # Retrieve check-ins from these friends that haven't expired yet (i.e. expires_at is in the future)
        checkins = CheckIn.objects.filter(user__in=friends, expires_at__gt=now).order_by('-created_at')

        # Serialize the check-in objects into JSON format
        serializer = CheckInSerializer(checkins, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
