from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.utils import timezone
from .models import CheckIn
from .checkin_serializers import CheckInSerializer

class CreateCheckInView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CheckInSerializer(data=request.data)
        if serializer.is_valid():
            # Automatically assign the logged-in user to the check-in
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ListMyCheckInsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        my_checkins = CheckIn.objects.filter(user=request.user, expires_at__gt=now)
        serializer = CheckInSerializer(my_checkins, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
