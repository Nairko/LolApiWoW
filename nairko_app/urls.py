from django.urls import path
from . import views

urlpatterns = [
    path('summoner/', views.SummonerView.as_view(), name='summoner'),
    # Ajoutez d'autres URL ici au besoin
    path('summoner/lastgame/<str:summoner_name>/', views.LastGamesView.as_view(), name='last_game'),
    path('summoner/stats/<str:summoner_name>/', views.DetailedStatsView.as_view(), name='stats'),
    path('summoner/data/<str:summoner_name>/', views.DetailedDataView.as_view(), name='data'),
    path('summoner/last20games/<str:summoner_name>/', views.Last20GamesView.as_view(), name='last20games'),
    
]
