from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Q
from django.utils import timezone
from .models import CustomUser, Interaction, DirectMessage  # Adjust if needed

class SocialGraphView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        now = timezone.now()
        social_data = []

        for friend in user.friends.all():
            # Retrieve interactions between the user and this friend
            interactions = Interaction.objects.filter(
                Q(from_user=user, to_user=friend) | Q(from_user=friend, to_user=user)
            )
            interaction_points = sum(interaction.effective_points() for interaction in interactions)

            # Retrieve DMs exchanged in the last 180 days
            dms = DirectMessage.objects.filter(
                Q(sender=user, receiver=friend) | Q(sender=friend, receiver=user),
                created_at__gte=now - timezone.timedelta(days=180)
            )
            dm_points = sum(0.1 * max(0, (180 - (now - dm.created_at).days)) / 180 for dm in dms)

            total_points = interaction_points + dm_points
            social_data.append({
                'friend_id': friend.id,
                'username': friend.username,
                'profile_photo': friend.profile_photo.url if friend.profile_photo else None,
                'closeness': round(total_points, 2)
            })

        return Response(social_data, status=status.HTTP_200_OK)
