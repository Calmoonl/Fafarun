from django.urls import path
from . import views

urlpatterns = [
    path('fafarun/', views.home, name='home'),
]
