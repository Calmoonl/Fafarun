from django.db import models

# Create your models here.
class User(models.Model):
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    
class Player(models.Model):
    puuid = models.CharField(max_length=255)
    gameName = models.CharField(max_length=255)
    gameTag = models.CharField(max_length=5)