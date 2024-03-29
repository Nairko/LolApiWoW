# Generated by Django 5.0.1 on 2024-02-03 18:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nairko_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Match',
            fields=[
                ('match_id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('duration', models.FloatField(help_text='Durée du match en minutes')),
            ],
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('side', models.CharField(max_length=50)),
                ('nom_player', models.CharField(max_length=100)),
                ('role', models.CharField(max_length=50)),
                ('champion_jouer', models.CharField(max_length=100)),
                ('resultat', models.IntegerField()),
                ('player_kills', models.IntegerField()),
                ('player_assists', models.IntegerField()),
                ('player_deaths', models.IntegerField()),
                ('enemy_player_kills', models.IntegerField()),
                ('enemy_player_assists', models.IntegerField()),
                ('enemy_player_deaths', models.IntegerField()),
                ('team_kills', models.IntegerField()),
                ('team_assists', models.IntegerField()),
                ('team_deaths', models.IntegerField()),
                ('enemy_team_kills', models.IntegerField()),
                ('enemy_team_assists', models.IntegerField()),
                ('enemy_team_deaths', models.IntegerField()),
                ('player_damages', models.IntegerField()),
                ('enemy_player_damages', models.IntegerField()),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participants', to='nairko_app.match')),
            ],
        ),
    ]
