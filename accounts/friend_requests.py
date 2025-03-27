# accounts/friend_requests.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import CustomUser, FriendRequest

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_friend_request(request):
    to_user_id = request.data.get("to_user_id")
    if not to_user_id:
        return Response({"error": "to_user_id is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        to_user = CustomUser.objects.get(id=to_user_id)
    except CustomUser.DoesNotExist:
        return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)

    from_user = request.user

    # Check if there's already a friend request pending
    if FriendRequest.objects.filter(from_user=from_user, to_user=to_user, status='pending').exists():
        return Response({"error": "Friend request already sent."}, status=status.HTTP_400_BAD_REQUEST)

    # Check if they're already friends
    if to_user in from_user.friends.all():
        return Response({"error": "You are already friends."}, status=status.HTTP_400_BAD_REQUEST)

    # Create a new friend request
    friend_request = FriendRequest.objects.create(from_user=from_user, to_user=to_user)
    return Response({"message": "Friend request sent.", "request_id": friend_request.id}, status=status.HTTP_201_CREATED)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def respond_friend_request(request, request_id):
    action = request.data.get("action")  # "accept" or "reject"

    try:
        friend_request = FriendRequest.objects.get(id=request_id, to_user=request.user)
    except FriendRequest.DoesNotExist:
        return Response({"error": "Friend request not found."}, status=status.HTTP_404_NOT_FOUND)

    if friend_request.status != 'pending':
        return Response({"error": f"Cannot {action} a request that is {friend_request.status}."},
                        status=status.HTTP_400_BAD_REQUEST)

    if action == "accept":
        # Check the 100-friend limit for both users
        if friend_request.to_user.friends.count() >= 100:
            return Response({"error": "You already have 100 friends."}, status=status.HTTP_400_BAD_REQUEST)
        if friend_request.from_user.friends.count() >= 100:
            return Response({"error": "The sender already has 100 friends."}, status=status.HTTP_400_BAD_REQUEST)

        # Update friend relationships
        friend_request.to_user.friends.add(friend_request.from_user)
        friend_request.from_user.friends.add(friend_request.to_user)
        friend_request.status = 'accepted'
        friend_request.save()
        return Response({"message": "Friend request accepted."}, status=status.HTTP_200_OK)

    elif action == "reject":
        friend_request.status = 'rejected'
        friend_request.save()
        return Response({"message": "Friend request rejected."}, status=status.HTTP_200_OK)

    else:
        return Response({"error": "Invalid action. Must be 'accept' or 'reject'."},
                        status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_friend_requests(request):
    incoming = FriendRequest.objects.filter(to_user=request.user, status='pending')
    outgoing = FriendRequest.objects.filter(from_user=request.user, status='pending')

    incoming_data = [
        {
            "request_id": fr.id,
            "from_user_id": fr.from_user.id,
            "from_user_email": fr.from_user.email,
            "created_at": fr.created_at
        }
        for fr in incoming
    ]

    outgoing_data = [
        {
            "request_id": fr.id,
            "to_user_id": fr.to_user.id,
            "to_user_email": fr.to_user.email,
            "created_at": fr.created_at
        }
        for fr in outgoing
    ]

    return Response({
        "incoming_requests": incoming_data,
        "outgoing_requests": outgoing_data
    }, status=status.HTTP_200_OK)
