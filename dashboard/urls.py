from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="dashboard.index"),
    path("dashboard/", views.dashboard, name="dashboard.dashboard"),
    path("add-expense/", views.add_expense, name="dashboard.add_expense"),
]