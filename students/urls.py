from django.urls import path
from .views import LoginView, ProfileView, ChangePasswordView
from uuid import UUID

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("profile/<uuid:user_id>/", ProfileView.as_view(), name="profile"),  # <-- cambiar int a uuid
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
]
