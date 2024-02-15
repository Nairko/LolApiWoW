from django.db import models

# Create your models here.
from django.db import models

class Player(models.Model):
    username = models.CharField(max_length=100)
    role = models.CharField(max_length=50)
    games_played = models.IntegerField()
    # Ajoutez d'autres champs selon vos besoins

    def __str__(self):
        return self.username



class Match(models.Model):
    match_id = models.CharField(max_length=100, primary_key=True)
    duration = models.FloatField(help_text="Durée du match en minutes")

    def __str__(self):
        return self.match_id

class Participant(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='participants')
    side = models.CharField(max_length=50)
    nom_player = models.CharField(max_length=100)
    role = models.CharField(max_length=50)
    champion_jouer = models.CharField(max_length=100)
    resultat = models.IntegerField()
    player_kills = models.IntegerField()
    player_assists = models.IntegerField()
    player_deaths = models.IntegerField()
    enemy_player_kills = models.IntegerField()
    enemy_player_assists = models.IntegerField()
    enemy_player_deaths = models.IntegerField()
    team_kills = models.IntegerField()
    team_assists = models.IntegerField()
    team_deaths = models.IntegerField()
    enemy_team_kills = models.IntegerField()
    enemy_team_assists = models.IntegerField()
    enemy_team_deaths = models.IntegerField()
    player_damages = models.IntegerField()
    enemy_player_damages = models.IntegerField()
    # Vous pouvez ajouter plus de champs selon vos besoins

    def __str__(self):
        return f"{self.nom_player} - {self.champion_jouer}"
