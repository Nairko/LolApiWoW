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
    player_kills = models.IntegerField(default=0)
    player_assists = models.IntegerField(default=0)
    player_deaths = models.IntegerField(default=0)
    enemy_player_kills = models.IntegerField(default=0)
    enemy_player_assists = models.IntegerField(default=0)
    enemy_player_deaths = models.IntegerField(default=0)
    team_kills = models.IntegerField(default=0)
    team_assists = models.IntegerField(default=0)
    team_deaths = models.IntegerField(default=0)
    enemy_team_kills = models.IntegerField(default=0)
    enemy_team_assists = models.IntegerField(default=0)
    enemy_team_deaths = models.IntegerField(default=0)
    player_cs = models.IntegerField(default=0)
    enemy_player_cs = models.IntegerField(default=0)
    team_cs = models.IntegerField(default=0)
    enemy_team_cs = models.IntegerField(default=0)
    player_damages = models.IntegerField(default=0)
    enemy_player_damages = models.IntegerField(default=0)
    team_damages = models.IntegerField(default=0)
    enemy_team_damages = models.IntegerField(default=0)
    player_damage_taken = models.IntegerField(default=0)
    enemy_player_damage_taken = models.IntegerField(default=0)
    team_damage_taken = models.IntegerField(default=0)
    enemy_team_damage_taken = models.IntegerField(default=0)
    player_damage_mitigated = models.IntegerField(default=0)
    player_gold_earned = models.IntegerField(default=0)
    enemy_player_gold_earned = models.IntegerField(default=0)
    team_gold_earned = models.IntegerField(default=0)
    enemy_team_gold_earned = models.IntegerField(default=0)
    player_total_wards_placed = models.IntegerField(default=0)
    enemy_player_total_wards_placed = models.IntegerField(default=0)
    team_total_wards_placed = models.IntegerField(default=0)
    enemy_team_total_wards_placed = models.IntegerField(default=0)
    player_wards_killed = models.IntegerField(default=0)
    enemy_players_wards_killed = models.IntegerField(default=0)
    team_wards_killeds = models.IntegerField(default=0)
    enemy_team_wards_killed = models.IntegerField(default=0)
    player_total_heal = models.IntegerField(default=0)
    enemy_player_total_heal = models.IntegerField(default=0)
    team_total_heals = models.IntegerField(default=0)
    enemy_team_total_heals = models.IntegerField(default=0)
    # Vous pouvez ajouter plus de champs selon vos besoins

    def __str__(self):
        return f"{self.nom_player} - {self.champion_jouer}"
