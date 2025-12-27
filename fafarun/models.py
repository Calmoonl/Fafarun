from django.db import models

# Create your models here.
class User(models.Model):
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    
class Player(models.Model):
    
    class Team(models.TextChoices):
        RAYANE = 'RAYANE', 'Rayane'
        ERWAN = 'ERWAN', 'Erwan'
        NEFF = 'NEFF', 'Neff'
        ZIZOU = 'ZIZOU', 'Zizou'
        
    class Lane(models.TextChoices):
        TOP = "TOP", "Top"
        JUNGLE = "JUNGLE", "Jungle"
        MID = "MID", "Mid"
        ADC = "ADC", "ADC"
        SUPPORT = "SUPPORT", "Support"

    puuid = models.CharField(max_length=255, unique=True, db_index=True)
    gameName = models.CharField(max_length=255)
    gameTag = models.CharField(max_length=5)

    team = models.CharField(max_length=6, choices=Team.choices, null=True, blank=True)
    lane = models.CharField(max_length=7, choices=Lane.choices, null=True, blank=True)

    capitaine = models.BooleanField(default=False)

    lastTenGames = models.JSONField(default=list, blank=True)

    tierSolo = models.CharField(max_length=11, default="UNRANKED", blank=True)
    rankSolo = models.CharField(max_length=3, default="", blank=True)
    lpSolo = models.IntegerField(default=0)

    winsSolo = models.IntegerField(default=0)
    lossesSolo = models.IntegerField(default=0)
    nbGameSolo = models.IntegerField(default=0)
    winrateSolo = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    rankScore = models.IntegerField(default=0)
    
    icon = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.gameName}#{self.gameTag}"