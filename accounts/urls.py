from django.urls import path
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenRefreshView,
)

from accounts.views import LoginView, MeView, RegisterView


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("me/", MeView.as_view(), name="me"),
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("logout/", TokenBlacklistView.as_view(), name="logout"),
]
