from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import CheckIn, Interaction, CustomUser

@receiver(post_save, sender=CheckIn)
def log_in_person_interactions(sender, instance, created, **kwargs):
    if not created:
        return  # Only act on new check-ins

    print(f"Signal fired for CheckIn {instance.id} by user {instance.user.username}")

    user = instance.user
    time_window_start = instance.created_at - timezone.timedelta(hours=3)
    time_window_end = instance.created_at + timezone.timedelta(hours=3)
    print(f"Time window: {time_window_start} to {time_window_end}")

    for friend in user.friends.all():
        print(f"Checking friend: {friend.username}")
        friend_checkins = friend.checkins.filter(
            location_name=instance.location_name,
            created_at__range=(time_window_start, time_window_end)
        )
        print(f"Found {friend_checkins.count()} check-ins for {friend.username} at {instance.location_name}")
        if friend_checkins.exists():
            Interaction.objects.create(
                from_user=user,
                to_user=friend,
                interaction_type='in_person',
                points=10
            )
            Interaction.objects.create(
                from_user=friend,
                to_user=user,
                interaction_type='in_person',
                points=10
            )
            print(f"Created interactions between {user.username} and {friend.username}")
