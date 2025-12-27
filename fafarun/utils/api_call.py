import asyncio
import random
import httpx
from django.conf import settings

API_KEY = settings.RIOT_API_KEY
MAX_RETRIES = 6

async def api_call(client: httpx.AsyncClient, url: str, sem=None):
    for attempt in range(MAX_RETRIES):
        # utiliser SEMAPHORE pour les appels multiples (tous les joueurs ou games)
        if sem:
            async with sem:
                response = await client.get(url)
        else:
            response = await client.get(url)
            
        # 200 : Requete ok
        if response.status_code == 200:
            return response.json()
        # 429 : Trop de requetes --> Retry-after donné par Riot ou random
        if response.status_code == 429:
            retryAfter = response.headers.get("Retry-After")
            wait = float(retryAfter) if retryAfter else (2 ** attempt) + random.random()
            await asyncio.sleep(wait)
            continue

        return None
    return None