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
            is_email_verified=False
        )
        user.set_password(password)  # Hashes the password

        # Optionally generate a new token here; our save() method does this, but we'll do it explicitly too.
        user.email_verification_token = str(uuid.uuid4())
        user.save()

        # Construct the verification link (adjust the domain as needed)
        verification_link = f"http://127.0.0.1:8000/api/verify-email/?token={user.email_verification_token}"

        # Send the verification email (this will print to the console)
        subject = "Verify Your Email Address"
        message = f"Hi, please verify your email address by clicking the following link: {verification_link}"
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com")
        recipient_list = [email]
        send_mail(subject, message, from_email, recipient_list)

        return Response({"message": "Registration successful. Please check your email to verify your account."},
                        status=status.HTTP_201_CREATED)

class VerifyEmailView(APIView):
    def get(self, request):
        token = request.GET.get("token")
        if not token:
            return Response({"error": "Token is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = CustomUser.objects.get(email_verification_token=token)
        except CustomUser.DoesNotExist:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

        # Mark the user as verified and clear the token
        user.is_email_verified = True
        user.email_verification_token = ""
        user.save()

        return Response({"message": "Email verified successfully."}, status=status.HTTP_200_OK)
