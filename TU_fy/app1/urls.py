from django.urls import path, include

from . import views
from .views import start

urlpatterns = [
    path('', views.start, name='start'),
    path('main/', views.index, name='index'),
    path('impressum/', views.imprint, name='imprint'),
    path('analyze/', views.analyze_lyrics, name='analyze_lyrics'),
    path('analyze-sentiment/', views.analyze_sentiment, name='analyze_sentiment'),
    path('analyze/deep_sentiment/', views.deep_analyze_sentiment, name='deep_analyze_sentiment'),
    path('search/', views.search, name='lyrics_search'), #URLs für die Songsuche
    path('record/',views.record_audio_page, name='record_audio_page'),  # zeigt das HTML
    path('record/recognize_audio/', views.recognize_audio, name='recognize_audio') # API-Endpunkt

]