from django.urls import path
from .views import RegisterView, RequestOTPView, VerifyOTPView

urlpatterns = [
    path('register', RegisterView.as_view()),
    path('request-otp', RequestOTPView.as_view()),
    path('verify-otp', VerifyOTPView.as_view()),
]
