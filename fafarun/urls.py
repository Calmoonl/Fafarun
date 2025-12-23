from django.urls import path
from . import views

urlpatterns = [
    path('fafarun/', views.home, name='home'),
    path('fafarun/edit/', views.edit_player, name='edit_player'),
]
