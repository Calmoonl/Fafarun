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
N = 10
# 2viter erreur 429
MAX_CONCURRENCY_MATCH = 2
MAX_RETRIES = 6

@sync_to_async
def get_players():
    return list(Player.objects.all())

# Récupères les N derniers matchs
async def get_match_ids(client, puuid: str, count: int = N):
    url = f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?queue=420&start=0&count={count}"
    return await api_call(client, url)

# Récupères les infos des N matchs ID et récupérer win/loose
async def get_match_win(client, match_id: str, puuid: str, sem):
    url = f"https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}"
    data = await api_call(client, url, sem)
    if not data:
        return None
    me = next((p for p in data.get("info", {}).get("participants", []) if p.get("puuid") == puuid), None)
    return None if me is None else bool(me.get("win"))

async def update_one_player(client, player: Player, sem):
    match_ids = await get_match_ids(client, player.puuid, count=N)
    if not match_ids:
        return

    tasks = [get_match_win(client, mid, player.puuid, sem) for mid in match_ids]
    games = await asyncio.gather(*tasks)

    last_ten_games = [bool(game) if game is not None else False for game in games]

    await sync_to_async(Player.objects.filter(pk=player.pk).update)(lastTenGames=last_ten_games)

async def runner():
    sem = asyncio.Semaphore(MAX_CONCURRENCY_MATCH)
    players = await get_players()

    async with httpx.AsyncClient(timeout=15, headers={"X-Riot-Token": API_KEY}) as client:
        # batch avec for pour éviter Erreur 429
        for player in players:
            await update_one_player(client, player, sem)

class Command(BaseCommand):
    help = "Met à jour les 10 derniers résultats (win/lose) pour tous les joueurs."

    def handle(self, *args, **options):
        asyncio.run(runner())
        self.stdout.write(self.style.SUCCESS("Last10 mis à jour."))
