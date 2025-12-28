from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
#import requests
from .models import Player,Team,Lane
import httpx
import asyncio
from asgiref.sync import sync_to_async
from fafarun.utils.api_call import api_call
import json
from collections import defaultdict

API_KEY = settings.RIOT_API_KEY
MAX_CONCURRENCY = 8
MATCH_COUNT_DEFAULT = 20

@sync_to_async
def get_players():
    return list(Player.objects.all().order_by('-rankScore'))

@sync_to_async
def get_players_by_teams(team:str):
    return list(Player.objects.filter(team=team).order_by('-rankScore'))

@sync_to_async
def get_teams():
    players = Player.objects.exclude(team="").order_by('-rankScore')

    teams = defaultdict(lambda: {"players": [], "points": 0})
    
    for global_position, player in enumerate(players, start=1):
        player.globalRank = global_position

    for player in players:
        teams[player.team]["players"].append(player)
        teams[player.team]["points"] += player.pointsGained

    for data in teams.values():
        data["players"].sort(key=lambda p: p.rankScore, reverse=True)
    
    return sorted(
        teams.items(),
        key=lambda item: item[1]["points"],
        reverse=True
    )

@sync_to_async
def create_player(puuid: str, gameName: str, gameTag: str, team: str,capitaine:bool,lane:str):
    Player.objects.create(
        puuid=puuid,
        gameName=gameName.strip(),
        gameTag=gameTag.strip(),
        team=team,
        capitaine=capitaine,
        lane=lane
    )
    
@sync_to_async
def player_exists(puuid: str) -> bool:
    return Player.objects.filter(puuid=puuid).exists()

# Page Leaderboard
async def leaderboard(request):
    
    team = request.GET.get("team", "").strip()
    if request.headers.get("HX-Request") == "true":
        if team and team != "TOUTES":
            player_list = await get_players_by_teams(team)
            resp = render(request, "partials/leaderboard/leaderboard_content.html", {"player_list": player_list})
            resp["HX-Trigger"] = json.dumps({"toast": {"type": "success", "message": f"Leaderboard filtré sur l'équipe {team}." , "timeout": 3000}})
            return resp
        
        player_list = await get_players()
        return render(request, "partials/leaderboard/leaderboard_content.html", {"player_list": player_list})
        
    player_list = await get_players()
    return render(request, "leaderboard.html", {"player_list": player_list})

# Page player list
async def players_list(request):

    players = await get_players()
    
    if request.method == 'POST':
        print(request.POST)
        gameName = request.POST.get('gameName')
        gameTag = request.POST.get('gameTag')
        team = request.POST.get('team')
        lane = request.POST.get('lane')
        capitaine = True if request.POST.get('capitaine') == "on" else False
        
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
                            await create_player(puuid, gameName, gameTag, team,capitaine,lane)
                            players = await get_players()
                            resp = render(request, "partials/players_list/player_list.html", {"player_list": players})
                            resp["HX-Trigger"] = json.dumps({"toast": {"type": "success", "message": "Joueur ajouté ✅", "timeout": 3000}})
                            return resp
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

# Route supplémentaires player_list
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
        
        resp = render(request,"partials/players_list/player_infos.html",{"player": player})
        resp["HX-Trigger"] = json.dumps({"toast": {"type": "success", "message": "Joueur modifié avec succès ✅", "timeout": 10000}})
        return resp

    except Exception as e:
        print(f'Erreur : {e}')
        return HttpResponse(e)

# Page Team
async def teams(request):
    teams = await get_teams()
    return render(request, "teams.html", {"teams": teams, "Team": Team})
