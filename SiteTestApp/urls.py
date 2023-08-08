from django.urls import path
from . import views
from .views import run_test

urlpatterns = [
    path("", views.index, name="index"),
    path('run_test/', run_test, name='run_python_program'),
]