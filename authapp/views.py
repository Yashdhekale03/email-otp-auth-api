from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import User, OTP
from .serializers import RegisterSerializer, OTPRequestSerializer, OTPVerifySerializer
from rest_framework_simplejwt.tokens import RefreshToken
import random

# Helper: generate 6-digit OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# Helper: mock email function (just prints)
def send_mock_email(email, otp):
    print(f"[MOCK EMAIL] OTP for {email}: {otp}")

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Registration successful. Please verify your email."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RequestOTPView(APIView):
    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"error": "User not registered."}, status=404)

            otp_code = generate_otp()
            OTP.objects.create(user=user, code=otp_code)
            send_mock_email(email, otp_code)
            return Response({"message": "OTP sent to your email."})
        return Response(serializer.errors, status=400)

class VerifyOTPView(APIView):
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            try:
                user = User.objects.get(email=email)
                latest_otp = OTP.objects.filter(user=user).latest('created_at')

                # Check if OTP is correct and not expired (5 minutes)
                if latest_otp.code == otp and (timezone.now() - latest_otp.created_at).seconds < 300:
                    user.is_verified = True
                    user.save()

                    refresh = RefreshToken.for_user(user)
                    return Response({
                        "message": "Login successful.",
                        "token": str(refresh.access_token)
                    })
                else:
                    return Response({"error": "Invalid or expired OTP."}, status=400)
            except:
                return Response({"error": "OTP verification failed."}, status=400)
        return Response(serializer.errors, status=400)
