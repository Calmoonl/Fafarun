from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('fafarun/', views.home, name='home'),
    path('fafarun/edit/', views.edit_player, name='edit_player'),
    path('fafarun/player_infos/<str:puuid>', views.player_infos, name='player_infos'),
]
