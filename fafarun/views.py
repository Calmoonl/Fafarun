from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
#import requests
from .models import Player
import httpx
import asyncio
from asgiref.sync import sync_to_async

API_KEY = settings.RIOT_API_KEY
MAX_CONCURRENCY = 8

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

async def api_call(client: httpx.AsyncClient, url: str,sem: asyncio.Semaphore | None = None):
    try:
        if sem :
            async with sem:  
                response = await client.get(url)
        else : 
            response = await client.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erreur API {response.status_code}: {url}")
            return None
    except Exception as e:
        print(f"Erreur : {e}")
        return None

async def home(request):

    players = await get_players()
    player_list = []

    if players:
        
        sem = asyncio.Semaphore(MAX_CONCURRENCY)
        
        async with httpx.AsyncClient(timeout=10, headers={"X-Riot-Token": API_KEY}) as client:
            
            tasks = []
            
            for player in players:
                url = f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-puuid/{player.puuid}"
                tasks.append(api_call(client, url, sem))
            
            results = await asyncio.gather(*tasks)

        for player, data in zip(players, results):
                tier_solo = "UNRANKED"
                rank_solo = ""
                lp_solo = 0

                if data:
                    for raw in data:
                        if raw.get("queueType") == "RANKED_SOLO_5x5":
                            tier_solo = raw.get("tier")
                            rank_solo = raw.get("rank")
                            lp_solo = raw.get("leaguePoints")
                            break

                player_list.append({
                    "puuid": player.puuid,
                    "gameName": player.gameName,
                    "gameTag": player.gameTag,
                    "team": player.team,
                    "tierSolo": tier_solo,
                    "rankSolo": rank_solo,
                    "lp": lp_solo,
                })

    return render(request, "home.html", {"player_list": player_list})

async def edit_player(request):

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
                            return render(request,"partials/edit_player/player_list.html",{"player_list": players})
                    else :
                        return HttpResponse("Erreur: PUUID introuvable dans la réponse API.")
                    
                else:
                    print(f"Erreur API : Aucune joueur trouvé")
                
            except Exception as e:
                print(f'Erreur : {e}')
                return HttpResponse(e)
        
        else :
            return "Aucun user renseigné"
    
    return render(request, 'edit_player.html',{'player_list':players})

async def player_infos(request, puuid):
    # puuid = celui cliqué
    print(f"PUUID : {puuid}")
    player = await sync_to_async(Player.objects.get)(puuid=puuid)
    return HttpResponse(f"Joueur : {player.gameName}")