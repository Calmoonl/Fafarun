from django.shortcuts import render
from django.conf import settings
import requests
from .models import Player

API_KEY = settings.RIOT_API_KEY

def home(request):
    
    players = Player.objects.all()
    
    if request.method == 'POST':
      
        gameName = request.POST.get('gameName')
        gameTag = request.POST.get('gameTag')
        
        if gameName and gameTag :
            
            try :
                r = requests.get(f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName}/{gameTag}?api_key={API_KEY}")
                print(f"Utilisateur : {gameName}, Tag : {gameTag}")
                r = r.json()
            
                player = Player.objects.filter(puuid = r.get("puuid"))
                
                if player :
                    print("Joueur existant")
                else :
                    print("Nouveau joueur")
                    Player.objects.create(
                        puuid = r.get("puuid"),
                        gameName= gameName,
                        gameTag = gameTag,
                    )
                    
            except Exception as e:
                print(f'Erreur : {e}')
                return e
        
        else :
            return "Y'a pas wesh"
    
    return render(request, 'home.html',{'players':players})