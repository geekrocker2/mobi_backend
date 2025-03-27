from django.shortcuts import render

# Create your views here.
# accounts/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import date, datetime
from django.core.mail import send_mail
from django.conf import settings
from .models import CustomUser
import uuid
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterView(APIView):
    def post(self, request):
        # Extract the data from the request body
        email = request.data.get("email")
        password = request.data.get("password")
        mobile_number = request.data.get("mobile_number")
        dob_str = request.data.get("date_of_birth")  # Expected format: YYYY-MM-DD

        # Validate that required fields are provided
        if not email or not password or not dob_str:
            return Response({"error": "Email, password, and date of birth are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Parse the date of birth
        try:
            dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Date of birth must be in YYYY-MM-DD format."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Calculate the age of the user
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if age < 13:
            return Response({"error": "You must be at least 13 years old to register."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Check if a user with the same email already exists
        if CustomUser.objects.filter(email=email).exists():
            return Response({"error": "A user with this email already exists."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Create the new user
        user = CustomUser(
            username=email,  # Use the email as username
            email=email,
            mobile_number=mobile_number,
            date_of_birth=dob,
            is_email_verified=True,  # User is verified by default
            is_active=True  # Ensure user is active
        )
        user.set_password(password)  # Hashes the password
        user.save()

        # Generate JWT tokens for immediate login
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "message": "Registration successful!",
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username
            }
        }, status=status.HTTP_201_CREATED)

# Keep this view for backward compatibility, but it's no longer needed
class VerifyEmailView(APIView):
    def get(self, request):
        return Response({"message": "Email verification is not required."}, status=status.HTTP_200_OK)
