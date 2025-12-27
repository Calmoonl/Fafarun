from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('fafarun/', views.home, name='home'),
    path('fafarun/players_list/', views.players_list, name='players_list'),
    path('fafarun/players_list/<str:puuid>/', views.players_list, name='open_player'),
    path('fafarun/player_infos/<str:puuid>', views.player_infos, name='player_infos'),
    path('fafarun/edit_player/<str:puuid>', views.edit_player, name='edit_player'),
]
