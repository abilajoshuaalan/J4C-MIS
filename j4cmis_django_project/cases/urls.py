from django.urls import path
from . import views

app_name = "cases"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
]
