from django_cassiopeia import cassiopeia as cass
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from .models import Match, Participant
from django.conf import settings
from collections import Counter


class SummonerView(View):
    def get(self, request, *args, **kwargs):
        # Affiche simplement la page avec le formulaire pour entrer le nom du joueur
        return render(request, 'index.html')


class LastGamesView(View):
    def get(self, request, summoner_name):
        summoner = cass.Summoner(name=summoner_name, region="EUW")
        match_history = summoner.match_history[:5]  # Prendre les 5 derniers matchs

        if len(match_history) == 0:
            return render(request, 'last5games.html', {'error': "Aucune partie récente trouvée"})

        total_kills = total_deaths = total_assists = total_cs = total_gold = total_time_played = 0

        games_data = []

        for match in match_history:
            participants = match.participants
            participant = next((p for p in participants if p.summoner.id == summoner.id), None)
            time_played_seconds = participant.stats.time_played
            time_played_minutes = time_played_seconds / 60
            summoner_is_winner = None

            if participant:
                is_winner = participant.team.win
                kills = participant.stats.kills
                deaths = participant.stats.deaths
                assists = participant.stats.assists
                cs = participant.stats.total_minions_killed + participant.stats.neutral_minions_killed
                gold = participant.stats.gold_earned

                total_kills += kills
                total_deaths += deaths
                total_assists += assists
                total_cs += cs
                total_gold += gold
                total_time_played += time_played_minutes

                champion_image_url = participant.champion.image.url

                games_data.append({
                    'is_winner': is_winner,
                    "champion": participant.champion.name,
                    "champion_image_url": champion_image_url,
                    "kda": f"{kills}/{deaths}/{assists}",
                    "cs": cs,
                    "gold": gold,
                    "GameLenght": round(time_played_minutes, 3),
                })

        num_games = len(match_history)
        average_kda = f"{total_kills/num_games}/{total_deaths/num_games}/{total_assists/num_games}"
        average_cs = total_cs / num_games
        average_gold = total_gold / num_games
        average_time_played = round(total_time_played  / num_games, 3)

        context = {
            'summoner_name': summoner_name,
            'games_data': games_data,
            'average_kda': average_kda,
            'average_cs': average_cs,
            'average_gold': average_gold,
            'average_time_played': average_time_played
        }

        return render(request, 'last5games.html', context)

class DetailedStatsView(View):
    def get(self, request, summoner_name):
        summoner = cass.Summoner(name=summoner_name, region="EUW")
        match_history = summoner.match_history[:5]  # Analyser les 5 derniers matchs

        if len(match_history) == 0:
            return render(request, 'index.html', {'error': "Aucune partie récente trouvée"})

        matches_info = []

        for match in match_history:
            blue_team = []
            red_team = []
            match_duration_minutes = match.duration.total_seconds() / 60  # Convertir la durée en minutes
            summoner_is_winner = None

            for participant in match.participants:
                # Collecte des statistiques pour chaque participant
                kills = participant.stats.kills
                deaths = participant.stats.deaths
                assists = participant.stats.assists
                cs = participant.stats.total_minions_killed + participant.stats.neutral_minions_killed
                gold = participant.stats.gold_earned
                is_winner = participant.team.win

                if participant.summoner.id == summoner.id:
                    summoner_is_winner = is_winner

                participant_info = {
                    'summoner_name': participant.summoner.name,
                    'is_winner': is_winner,
                    'champion_image_url': participant.champion.image.url,
                    'champion_name': participant.champion.name,
                    'kda': f"{kills}/{deaths}/{assists}",
                    'cs': cs,
                    'gold': gold,
                }

                # Assignation à l'équipe bleue ou rouge
                if participant.team.side == cass.Side.blue:
                    blue_team.append(participant_info)
                elif participant.team.side == cass.Side.red:
                    red_team.append(participant_info)


            # Ajout des informations de chaque match
            matches_info.append({
                'match_id': match.id,
                'match_duration': round(match_duration_minutes, 2),
                'blue_team': blue_team,
                'red_team': red_team,
                'summoner_is_winner': summoner_is_winner,
            })

        # Contexte à passer au template
        context = {
            'summoner_name': summoner_name,
            'matches_info': matches_info,
        }

        return render(request, 'stats.html', context)



class DetailedDataView(View):
    def get(self, request, summoner_name):
        summoner = cass.Summoner(name=summoner_name, region="EUW")
        for match in summoner.match_history:
            try:
                # Vérifier si le match est en ranked solo et n'est pas un remake
                if match.queue == cass.Queue.ranked_solo_fives and match.duration.seconds >= 300:
                    # Ce match est le dernier match classé solo non-remake
                    break
            except KeyError:
                # Ignorer les matchs avec un ID de queue non reconnu
                continue
        else:
            # Aucun match valide trouvé
            return HttpResponse("Aucune partie récente trouvée en Ranked Solo/Duo ou non-remake.", status=404)

        # Collecter les données
        match_duration_minutes = match.duration.total_seconds() / 60
        team_total_heal = {team.side.name: 0 for team in [match.red_team, match.blue_team]}
        team_wards_placed_totals = {team.side.name: 0 for team in [match.red_team, match.blue_team]}
        team_total_cs = {team.side.name: 0 for team in [match.red_team, match.blue_team]}

        for participant in match.participants:
            team_total_heal[participant.team.side.name] += participant.stats.total_heal + participant.stats.total_heals_on_teammates
            team_wards_placed_totals[participant.team.side.name] += participant.stats.wards_placed + participant.stats.vision_wards_placed
            team_total_cs[participant.team.side.name] += participant.stats.total_minions_killed + participant.stats.neutral_minions_killed
        match_data = {
            'match_id': match.id,
            'match_duration': match_duration_minutes,
            'team_total_heal': team_total_heal[match.blue_team.side.name],
            'enemy_team_total_heal': team_total_heal[match.red_team.side.name],
            'participants': []
        }
        print(match_data)
        for participant in match.participants:
            # Identifier l'équipe adverse
            enemy_team = match.red_team if participant.team == match.blue_team else match.blue_team
            enemy_participant = None
            p_total_heal = participant.stats.total_heal + participant.stats.total_heals_on_teammates
            p_total_wards_placed = participant.stats.wards_placed +  participant.stats.vision_wards_placed
            p_cs = participant.stats.total_minions_killed + participant.stats.neutral_minions_killed
            enemy_total_heal = 0
            for ep in enemy_team.participants:
                if ep.lane == participant.lane:  # Comparaison simplifiée
                    enemy_participant = ep
                    enemy_total_heal = ep.stats.total_heal + ep.stats.total_heals_on_teammates
                    enemy_total_wards_placed = ep.stats.wards_placed + ep.stats.vision_wards_placed
                    enemy_cs = ep.stats.total_minions_killed + ep.stats.neutral_minions_killed
                    break
            
            participant_team_total_heal = team_total_heal[participant.team.side.name]
            participant_enemy_team_total_heal = team_total_heal[enemy_team.side.name]
            participant_team_total_wards_placed = team_wards_placed_totals[participant.team.side.name]
            participant_enemy_team_total_wards_placed = team_wards_placed_totals[enemy_team.side.name]
            participant_team_total_cs = team_total_cs[participant.team.side.name]
            participant_enemy_team_total_cs= team_total_cs[enemy_team.side.name]
            


            participant_data = {
                'side': participant.team.side.name.lower(),
                'NomPlayer': participant.summoner.name,
                'Role': participant.lane,
                'ChampionJouer': participant.champion.name,
                'Resultat': 1 if participant.team.win else 0,
                'playerKills': participant.stats.kills,
                'playerAssists': participant.stats.assists,
                'playerDeath': participant.stats.deaths,
                'EnemyPlayerKills': enemy_participant.stats.kills,
                'EnemyPlayerAssists': enemy_participant.stats.assists,
                'EnemyPlayerDeath': enemy_participant.stats.deaths,
                'TeamKills': sum(p.stats.kills for p in participant.team.participants),
                'TeamAssist': sum(p.stats.assists for p in participant.team.participants),
                'TeamDeath': sum(p.stats.deaths for p in participant.team.participants),
                'enemyTeamKills': sum(p.stats.kills for p in enemy_team.participants),
                'EnemyTeamAssist': sum(p.stats.assists for p in enemy_team.participants),
                'EnnemyTeamDeath': sum(p.stats.deaths for p in enemy_team.participants),
                'PlayerCS':p_cs,
                'EnemyPlayerCS':enemy_cs,
                'TeamTotalCS':participant_team_total_cs,
                'EnemyTeamTotalCS':participant_enemy_team_total_cs,
                'PlayerDamages': participant.stats.total_damage_dealt_to_champions,
                'EnemyPlayerDamages': enemy_participant.stats.total_damage_dealt_to_champions,
                'TeamDamages': sum(p.stats.total_damage_dealt_to_champions for p in participant.team.participants),
                'EnemyTeamDamages': sum(p.stats.total_damage_dealt_to_champions for p in enemy_team.participants),
                'PlayerDamageTaken': participant.stats.total_damage_taken,
                'EnemyPlayerDamageTaken': enemy_participant.stats.total_damage_taken,
                'TeamDamageTaken': sum(p.stats.total_damage_taken for p in participant.team.participants),
                'EnemyTeamDamageTaken': sum(p.stats.total_damage_taken for p in enemy_team.participants),
                'PlayerDamageMitigated': participant.stats.damage_self_mitigated,
                'PlayerGoldEarned': participant.stats.gold_earned,
                'EnemyPlayerGoldEarned': enemy_participant.stats.gold_earned,
                'TeamGoldEarned': sum(p.stats.gold_earned for p in participant.team.participants),
                'EnemyTeamGoldEarned': sum(p.stats.gold_earned for p in enemy_team.participants),
                'PlayerTotalWardsPlaced':p_total_wards_placed,
                'EnemyPlayerTotalWardsPlaced':enemy_total_wards_placed,
                'TeamTotalWardsPlaced': participant_team_total_wards_placed,
                'EnemyTeamTotalWardsPlaced':participant_enemy_team_total_wards_placed,
                'PlayerWardsKilled': participant.stats.wards_killed,
                'EnemyPlayerWardsKilled': enemy_participant.stats.wards_killed,
                'TeamWardsKilled': sum(p.stats.wards_killed for p in participant.team.participants),
                'EnemyTeamWardsKilled': sum(p.stats.wards_killed for p in enemy_team.participants),
                'PlayerTotalHeal': p_total_heal,
                'EnemyPlayerTotalHeal': enemy_total_heal,
                'TeamTotalHeal': participant_team_total_heal,
                'EnemyTeamTotalHeal':participant_enemy_team_total_heal,
                

                # ... Continuer avec les autres statistiques
            }

            match_data['participants'].append(participant_data)
        match, created = Match.objects.get_or_create(
            match_id=match_data['match_id'],
            defaults={'duration': match_data['match_duration']}
        )
        
        # Pour chaque participant dans match_data, créer une instance de Participant
        for participant_data in match_data['participants']:
            participant, created = Participant.objects.update_or_create(
                match=match,
                nom_player=participant_data['NomPlayer'],
                defaults={
                    'side': participant_data['side'],
                    'role': participant_data['Role'],
                    'champion_jouer': participant_data['ChampionJouer'],
                    'resultat': participant_data['Resultat'],
                    'player_kills': participant_data['playerKills'],
                    'player_assists': participant_data['playerAssists'],
                    'player_deaths': participant_data['playerDeath'],
                    'enemy_player_kills': participant_data['EnemyPlayerKills'],
                    'enemy_player_assists': participant_data['EnemyPlayerAssists'],
                    'enemy_player_deaths': participant_data['EnemyPlayerDeath'],
                    'team_kills': participant_data['TeamKills'],
                    'team_assists': participant_data['TeamAssist'],
                    'team_deaths': participant_data['TeamDeath'],
                    'enemy_team_kills': participant_data['enemyTeamKills'],
                    'enemy_team_assists': participant_data['EnemyTeamAssist'],
                    'enemy_team_deaths': participant_data['EnnemyTeamDeath'],
                    'player_cs': participant_data['PlayerCS'],
                    'enemy_player_cs': participant_data['EnemyPlayerCS'],
                    'team_cs': participant_data['TeamTotalCS'],
                    'enemy_team_cs': participant_data['EnemyTeamTotalCS'],
                    'player_damages': participant_data['PlayerDamages'],
                    'enemy_player_damages': participant_data['EnemyPlayerDamages'],
                    'team_damages': participant_data['TeamDamages'],
                    'enemy_team_damages': participant_data['EnemyTeamDamages'],
                    'player_damage_taken': participant_data['PlayerDamageTaken'],
                    'enemy_player_damage_taken': participant_data['EnemyPlayerDamageTaken'],
                    'team_damage_taken': participant_data['TeamDamageTaken'],
                    'enemy_team_damage_taken': participant_data['EnemyTeamDamageTaken'],
                    'player_damage_mitigated': participant_data['PlayerDamageMitigated'],
                    'player_gold_earned': participant_data['PlayerGoldEarned'],
                    'enemy_player_gold_earned': participant_data['EnemyPlayerGoldEarned'],
                    'team_gold_earned': participant_data['TeamGoldEarned'],
                    'enemy_team_gold_earned': participant_data['EnemyTeamGoldEarned'],
                    'player_total_wards_placed':participant_data['PlayerTotalWardsPlaced'],
                    'enemy_player_total_wards_placed':participant_data['EnemyPlayerTotalWardsPlaced'],
                    'team_total_wards_placed':participant_data['TeamTotalWardsPlaced'],
                    'enemy_team_total_wards_placed':participant_data['EnemyTeamTotalWardsPlaced'],
                    'player_wards_killed': participant_data['PlayerWardsKilled'],
                    'enemy_players_wards_killed': participant_data['EnemyPlayerWardsKilled'],
                    'team_wards_killeds': participant_data['TeamWardsKilled'],
                    'enemy_team_wards_killed': participant_data['EnemyTeamWardsKilled'],
                    'player_total_heal': participant_data['PlayerTotalHeal'],
                    'enemy_player_total_heal': participant_data['EnemyPlayerTotalHeal'],
                    'team_total_heals': participant_data['TeamTotalHeal'],
                    'enemy_team_total_heals': participant_data['EnemyTeamTotalHeal'],
                    

                    # Ajouter d'autres champs si nécessaire
                }
            )

        return render(request, 'data.html', {'match_data': match_data})


class Last20GamesView(View):
    def get(self, request, summoner_name):
        summoner = cass.Summoner(name=summoner_name, region="EUW")
        all_matches = summoner.match_history[:20]

        # Filtrer pour obtenir uniquement les matchs en ranked solo/duo
        ranked_solo_matches = []
        for match in all_matches:
            try:
                match_queue = match.queue
                if match_queue == cass.Queue.ranked_solo_fives and match.duration.seconds >= 300:  # Exclure les parties de moins de 5 minutes
                    ranked_solo_matches.append(match)
                    if len(ranked_solo_matches) == 20:  # Arrêter une fois que 20 matchs valides sont trouvés
                        break
            except (AttributeError, KeyError):
                # Gérer les cas où l'attribut 'queue' n'est pas disponible ou non reconnu
                continue

        if len(ranked_solo_matches) == 0:
            return render(request, 'last20games.html', {'error': "Aucune partie récente trouvée en Ranked Solo/Duo ou non-remake"})
        
        print("oui regarde la", len(ranked_solo_matches))
        role_count = Counter()
        champion_count = Counter()
        total_wins = 0

        for match in ranked_solo_matches:
            participant = match.participants[summoner]
            role = str(participant.lane) if participant.lane != "NONE" else "Undefined"
            champion = participant.champion.name
            win = participant.stats.win

            role_count[role] += 1
            champion_count[champion] += 1
            total_wins += 1 if win else 0

        most_played_role, most_played_role_count = role_count.most_common(1)[0]
        most_played_champion, most_played_champion_games = champion_count.most_common(1)[0]
        champion_obj = cass.Champion(name=most_played_champion, region="EUW")
        most_played_champion_image_url = champion_obj.image.url
        most_played_champion_wins = sum(1 for match in ranked_solo_matches if match.participants[summoner].champion.name == most_played_champion and match.participants[summoner].stats.win)
        win_rate_most_played_champion = (most_played_champion_wins / most_played_champion_games) * 100
        player_win_rate = (total_wins / len(ranked_solo_matches)) * 100
        

        context = {
            'summoner_name': summoner_name,
            'most_played_role': most_played_role,
            'most_played_role_count': most_played_role_count,
            'most_played_champion': most_played_champion,
            'most_played_champion_image_url': most_played_champion_image_url,
            'most_played_champion_games': most_played_champion_games,
            'win_rate_most_played_champion': win_rate_most_played_champion,
            'player_win_rate': player_win_rate,
            'total_games': len(ranked_solo_matches)
        }

        return render(request, 'last20games.html', context)

