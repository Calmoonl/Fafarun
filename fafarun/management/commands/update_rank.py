import asyncio
import random
import httpx
from asgiref.sync import sync_to_async

from django.core.management.base import BaseCommand
from django.conf import settings
from fafarun.models import Player
from fafarun.utils.api_call import api_call

# Constantes
API_KEY = settings.RIOT_API_KEY
MAX_CONCURRENCY = 8
# 2viter erreur 429
MAX_RETRIES = 6

@sync_to_async
def get_players():
    return list(Player.objects.all())

async def update_one_player(client, player: Player, sem):
    tier, rank, lp = "UNRANKED", "", 0
    wins, losses = 0, 0
    winrate = 0.0

    url = f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-puuid/{player.puuid}"
    results = await api_call(client, url, sem)

    if results:
        for result in results:
            if result.get("queueType") == "RANKED_SOLO_5x5":
                tier = result.get("tier", "UNRANKED")
                rank = result.get("rank", "")
                lp = int(result.get("leaguePoints", 0) or 0)
                wins = int(result.get("wins", 0) or 0)
                losses = int(result.get("losses", 0) or 0)
                break
    
        games = wins + losses
        winrate = (wins / games * 100.0)

    await sync_to_async(Player.objects.filter(pk=player.pk).update)(
        tierSolo=tier,
        rankSolo=rank,
        lpSolo=lp,
        winsSolo = wins,
        lossesSolo = losses,
        winrateSolo = winrate,
        nbGameSolo = games,
    )


async def runner():
    players = await get_players()
    sem = asyncio.Semaphore(MAX_CONCURRENCY)

    async with httpx.AsyncClient(timeout=15, headers={"X-Riot-Token": API_KEY}) as client:
        tasks = [update_one_player(client,player, sem) for player in players]
        await asyncio.gather(*tasks)
        
class Command(BaseCommand):
    help = "Met à jour les ranks SoloQ pour tous les joueurs."

    def handle(self, *args, **options):
        asyncio.run(runner())
        self.stdout.write(self.style.SUCCESS("Ranks mis à jour."))
