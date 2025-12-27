from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
#import requests
from .models import Player
import httpx
import asyncio
from asgiref.sync import sync_to_async
from fafarun.utils.api_call import api_call

API_KEY = settings.RIOT_API_KEY
MAX_CONCURRENCY = 8
MATCH_COUNT_DEFAULT = 20

@sync_to_async
def get_players():
    return list(Player.objects.all())

@sync_to_async
def create_player(puuid: str, gameName: str, gameTag: str, team: str):
    Player.objects.create(
        puuid=puuid,
        gameName=gameName.strip(),
        gameTag=gameTag.strip(),
        team=team,
    )
    
@sync_to_async
def player_exists(puuid: str) -> bool:
    return Player.objects.filter(puuid=puuid).exists()

async def home(request):

    player_list = await get_players()
    return render(request, "home.html", {"player_list": player_list})

async def players_list(request):

    players = await get_players()
    
    if request.method == 'POST':
        print(request.POST)
        gameName = request.POST.get('gameName')
        gameTag = request.POST.get('gameTag')
        team = request.POST.get('team')
        
        if gameName and gameTag :
            
            try :
                url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName}/{gameTag}"
                
                async with httpx.AsyncClient(timeout=10,headers={"X-Riot-Token": API_KEY}) as client:
                    data = await api_call(client, url)
                
                if data:
                    puuid = data.get("puuid")
                    
                    if puuid :
                    
                        if await player_exists(puuid): 
                            print("Joueur existant")
                        else :        
                            await create_player(puuid, gameName, gameTag, team)
                            players = await get_players()
                            return render(request,"partials/players_list/player_list.html",{"player_list": players})
                    else :
                        return HttpResponse("Erreur: PUUID introuvable dans la réponse API.")
                    
                else:
                    print(f"Erreur API : Aucune joueur trouvé")
                
            except Exception as e:
                print(f'Erreur : {e}')
                return HttpResponse(e)
        
        else :
            return HttpResponse("Aucun user renseigné", status=400)
    
    return render(request, 'players_list.html',{'player_list':players})

async def player_infos(request, puuid:str):
    # puuid = celui cliqué
    print(f"PUUID : {puuid}")
    player = await sync_to_async(Player.objects.get)(puuid=puuid)
    return render(request,"partials/players_list/player_infos.html",{"player": player})

async def edit_player(request, puuid:str):
    print(f"PUUID : {puuid}")
    team = request.POST.get("editTeam")
    lane = request.POST.get("editLane")
    
    try :
    
        player = await sync_to_async(Player.objects.get)(puuid=puuid)
        
        player.team = team
        player.lane = lane
        await sync_to_async(player.save)()

        player = await sync_to_async(Player.objects.get)(puuid=puuid)
        
        return render(request,"partials/players_list/player_infos.html",{"player": player})

    except Exception as e:
        print(f'Erreur : {e}')
        return HttpResponse(e)
