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
        
    puuid = models.CharField(max_length=255,unique=True)
    gameName = models.CharField(max_length=255)
    gameTag = models.CharField(max_length=5)
    team = models.CharField(max_length=6,choices=Team.choices,null=True)
    
    def __str__(self):
        return f"{self.gameName} #{self.gameTag}"