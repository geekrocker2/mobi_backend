from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.conf import settings
from django.utils import timezone
import requests
import os

# --- Geocoding Helper Function ---

def geocode_location(location_name):
    api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
    if not api_key:
        print("Google Maps API key not found in environment variables.")
        return None, None

    # URL-encode the location name and build the URL.
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={requests.utils.quote(location_name)}&key={api_key}"
    print("Geocode URL:", url)  # Debug: Show the URL being called

    response = requests.get(url)
    print("Geocode response status:", response.status_code)  # Debug: Show response status

    if response.status_code == 200:
        data = response.json()
        print("Geocode data:", data)  # Debug: Show full API response
        if data['results']:
            location = data['results'][0]['geometry']['location']
            print("Found coordinates:", location)  # Debug: Show the coordinates found
            return location['lat'], location['lng']
        else:
            print("No geocoding results for:", location_name)
    else:
        print("Error contacting Google Maps API.")
    return None, None

# --- Models ---

class CustomUser(AbstractUser):
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    is_email_verified = models.BooleanField(default=True)
    email_verification_token = models.CharField(max_length=255, blank=True, null=True)

    # Optional: Track accepted friendships
    friends = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='my_friends'
    )
    
    # New fields for the profile page:
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    interests = models.TextField(blank=True, null=True)
    theme_song = models.CharField(max_length=255, blank=True, null=True)  # Could store a URL or song ID
    top_friends = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='top_friend_of'
    )

    def save(self, *args, **kwargs):
        if not self.email_verification_token:
            self.email_verification_token = str(uuid.uuid4())
        super().save(*args, **kwargs)

class FriendRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )

    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='friend_requests_sent'
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='friend_requests_received'
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.from_user} -> {self.to_user} ({self.status})"

def user_checkin_photo_path(instance, filename):
    # Organize photos by user ID and check-in ID
    return f"checkin_photos/user_{instance.user.id}/checkin_{instance.id}/{filename}"

class CheckIn(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='checkins'
    )
    location_name = models.CharField(max_length=255)
    # New geolocation fields
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    caption = models.CharField(max_length=120, blank=True, null=True)
    rating = models.PositiveSmallIntegerField()  # expect a value from 1 to 5
    photo = models.ImageField(upload_to=user_checkin_photo_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # If coordinates aren't provided, try to auto-populate from location_name
        if (self.latitude is None or self.longitude is None) and self.location_name:
            print("Calling geocode_location for:", self.location_name)  # Debug message
            lat, lng = geocode_location(self.location_name)
            if lat is not None and lng is not None:
                self.latitude = lat
                self.longitude = lng
                print(f"Coordinates set to: {lat}, {lng}")  # Debug message
            else:
                print("Geocoding failed for:", self.location_name)  # Debug message
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(hours=24)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} at {self.location_name}"

class DirectMessage(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_dms'
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_dms'
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"DM from {self.sender.username} to {self.receiver.username} at {self.created_at}"

class Interaction(models.Model):
    INTERACTION_CHOICES = (
        ('in_person', 'In Person'),
        ('phone_call', 'Phone Call'),
        ('direct_message', 'Direct Message'),
    )

    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='interactions_sent'
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='interactions_received'
    )
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_CHOICES)
    points = models.FloatField(help_text="Base points for this interaction")
    created_at = models.DateTimeField(auto_now_add=True)

    def effective_points(self):
        """
        Calculate effective points with a linear decay over 180 days.
        Points decay to 0 after 180 days.
        """
        age_days = (timezone.now() - self.created_at).days
        decay_factor = max(0, (180 - age_days)) / 180  # 1 when new, 0 after 180 days
        return self.points * decay_factor

    def __str__(self):
        return f"Interaction from {self.from_user} to {self.to_user} ({self.interaction_type})"
