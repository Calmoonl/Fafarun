from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
import requests
from .models import Player

API_KEY = settings.RIOT_API_KEY

def home(request):
    
    players = Player.objects.all()
    
    if players:
        player_list = []
    
        for player in players:
            url = f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-puuid/{player.puuid}?api_key={API_KEY}"
            response = requests.get(url)
    
            tier_solo = "UNRANKED"
            rank_solo = ""
            lp_solo = 0
            
            if response.status_code == 200:
                data = response.json()
                
                for raw in data:
                    if raw.get('queueType') == "RANKED_SOLO_5x5":
                        tier_solo = raw.get('tier')
                        rank_solo = raw.get('rank')
                        lp_solo = raw.get('leaguePoints')
                        break 
            
            # On crée le dictionnaire propre
            player_dict = {
                'gameName': player.gameName,
                'gameTag': player.gameTag,
                'tierSolo': tier_solo,
                'rankSolo': rank_solo,
                'lp': lp_solo
            }
            
            # On l'ajoute correctement à la liste
            player_list.append(player_dict)
        
    
        
    return render(request, 'home.html',{'player_list':player_list})

def edit_player(request):

    players = Player.objects.all()
    
    if request.method == 'POST':
      
        gameName = request.POST.get('gameName')
        gameTag = request.POST.get('gameTag')
        
        if gameName and gameTag :
            
            try :
                url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName}/{gameTag}?api_key={API_KEY}"
                response = requests.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    puuid = data.get("puuid")
                    
                    if puuid :
                        player = Player.objects.filter(puuid = puuid)
                        
                        if player :
                            print("Joueur existant")
                        else :        
                            Player.objects.create(
                                puuid = puuid,
                                gameName= gameName,
                                gameTag = gameTag,
                            )
                    else :
                        return HttpResponse("Erreur: PUUID introuvable dans la réponse API.")
                    
                else:
                    print(f"Erreur API: {response.status_code}")
                    return HttpResponse(f"Erreur Riot API: {response.status_code} - {response.text}")
                
            except Exception as e:
                print(f'Erreur : {e}')
                return HttpResponse(e)
        
        else :
            return "Aucun user renseigné"
    
    return render(request, 'edit_player.html',{'player_list':players})