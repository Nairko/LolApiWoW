# Generated by Django 5.0.1 on 2024-02-20 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nairko_app', '0005_participant_enemy_player_cs_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='enemy_team_total_heals',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='participant',
            name='team_total_heals',
            field=models.IntegerField(default=0),
        ),
    ]
