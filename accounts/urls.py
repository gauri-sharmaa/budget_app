from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="accounts.register"),
    path("create-user-profile/", views.create_user_profile, name="accounts.create_user_profile"),
    path("login/", views.login, name="accounts.login"),
    path("logout/", views.logout, name="accounts.logout"),
]