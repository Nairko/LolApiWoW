from django_cassiopeia import cassiopeia as cass
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.http import HttpResponse

class SummonerView(View):
    def get(self,request):
        summoner = cass.Summoner(name="B3NN0X", region="EUW")
        return JsonResponse({"name": summoner.name, "level": summoner.level})


class LastGamesView(View):
    def get(self, request, summoner_name):
        summoner = cass.Summoner(name=summoner_name, region="EUW")
        match_history = summoner.match_history[:5]  # Prendre les 5 derniers matchs

        if len(match_history) == 0:
            return render(request, 'index.html', {'error': "Aucune partie récente trouvée"})

        total_kills = total_deaths = total_assists = total_cs = total_gold = total_time_played = 0

        games_data = []

        for match in match_history:
            participants = match.participants
            participant = next((p for p in participants if p.summoner.id == summoner.id), None)
            time_played_seconds = participant.stats.time_played
            time_played_minutes = time_played_seconds / 60

            if participant:
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

        return render(request, 'index.html', context)

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

            for participant in match.participants:
                # Collecte des statistiques pour chaque participant
                kills = participant.stats.kills
                deaths = participant.stats.deaths
                assists = participant.stats.assists
                cs = participant.stats.total_minions_killed + participant.stats.neutral_minions_killed
                gold = participant.stats.gold_earned

                participant_info = {
                    'summoner_name': participant.summoner.name,
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
        match_history = summoner.match_history[:2]  # Prendre le dernier match
        match = match_history[0] if match_history else None
        print(len(match_history))  # Doit être > 0 pour continuer

        if not match:
            return HttpResponse("Aucune partie récente trouvée.", status=404)

        # Collecter les données
        match_duration_minutes = match.duration.total_seconds() / 60
        match_data = {
            'match_id': match.id,
            'match_duration': match_duration_minutes,
            'participants': []
        }

        for participant in match.participants:
            # Identifier l'équipe adverse
            enemy_team = match.red_team if participant.team == match.blue_team else match.blue_team
            enemy_participant = None
            for ep in enemy_team.participants:
                if ep.lane == participant.lane:  # Comparaison simplifiée
                    enemy_participant = ep
                    break


            participant_data = {
                'side': participant.team.side.name,
                'NomPlayer': participant.summoner.name,
                'RolePlayer': f"{participant.lane}/{participant.role}",
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
                'PlayerDamages': participant.stats.total_damage_dealt_to_champions,
                'EnemyPlayerDamages': enemy_participant.stats.total_damage_dealt_to_champions,
                # ... Continuer avec les autres statistiques
            }

            match_data['participants'].append(participant_data)

        return render(request, 'data.html', {'match_data': match_data})

