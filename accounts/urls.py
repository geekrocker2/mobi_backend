from django.urls import path
from .views import RegisterView, VerifyEmailView
from .friend_requests import (
    send_friend_request,
    respond_friend_request,
    list_friend_requests
)
from .checkin_views import (
    CreateCheckInView,
    ListMyCheckInsView
)
from .feed_views import FeedView  # Import the FeedView
from .profile_views import ProfileView  # Import the ProfileView from profile_views.py
from .dm_views import DirectMessageView
from .social_graph_views import SocialGraphView
from .phone_call_views import LogPhoneCallView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),

    # Friend request endpoints
    path('friend-request/', send_friend_request, name='send_friend_request'),
    path('friend-request/<int:request_id>/', respond_friend_request, name='respond_friend_request'),
    path('friend-requests/', list_friend_requests, name='list_friend_requests'),

    # Check-In endpoints
    path('checkins/', CreateCheckInView.as_view(), name='create_checkin'),
    path('my-checkins/', ListMyCheckInsView.as_view(), name='list_my_checkins'),

    # Feed endpoint
    path('feed/', FeedView.as_view(), name='feed'),

    # Profile endpoints
    path('profile/', ProfileView.as_view(), name='profile'),  # For the current user's profile (GET and PUT)
    path('profile/<int:user_id>/', ProfileView.as_view(), name='profile_detail'),  # To view a specific user's profile
    # DM endpoints: For conversation with a specific user
    path('dms/<int:user_id>/', DirectMessageView.as_view(), name='direct_messages'),

    # Direct Message endpoints:
    path('dms/', DirectMessageView.as_view(), name='send_direct_message'),
    path('dms/<int:user_id>/', DirectMessageView.as_view(), name='direct_messages'),

    # Social Graph endpoints:
    path('social-graph/', SocialGraphView.as_view(), name='social_graph'),

    # Phone Call endpoints:
    path('phone-call/', LogPhoneCallView.as_view(), name='log_phone_call'),

]
