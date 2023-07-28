from django.urls import path

from . import views
from .views import calculate_ttfb

urlpatterns = [
    path("", views.index, name="index"),
    path('ttfb/', calculate_ttfb, name='ttfb'),
]