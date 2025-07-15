# functions wie get blablabla

import requests
from django.http import JsonResponse
from bertopic import BERTopic
from django.shortcuts import render, redirect
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from sympy import false
from transformers import pipeline
from umap import UMAP
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from django.views.decorators.http import require_http_methods
from yt_dlp import YoutubeDL
import TU_fy
from app3.models import Song
import subprocess
import tempfile
import os
import requests
from django.http import JsonResponse
import plotly.io as pio
from openai import OpenAI
from django.views.decorators.http import require_POST
from django.shortcuts import render
from django.conf import settings

# Modell wird einmal global geladen (Performance!)
emotion_classifier = pipeline(
    "text-classification",
    model="bhadresh-savani/bert-base-go-emotion",
    return_all_scores=True,
    top_k=None
)

EMOJI_MAP = {
    "joy": "😊", "anger": "😡", "sadness": "😢", "disappointment": "😞",
    "amusement": "😄", "excitement": "🤩", "neutral": "😐", "pride": "😌",
    "gratitude": "🙏", "grief": "😭", "curiosity": "🧐", "love": "❤️",
    "fear": "😱", "embarrassment": "😳", "confusion": "😕"
}


# Send request func
def start(request):
    # if request.user.is_authenticated:
    #     return redirect('dashboard')
    return render(request, 'startingscreen.html')


from django.shortcuts import render
import requests
from django.contrib.auth.decorators import login_required


def get_cached_lyrics(artist, title):
    try:
        return Song.objects.get(
            artist__iexact=artist.strip(),
            title__iexact=title.strip()
        )
    except Song.DoesNotExist:
        return None


summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
@require_http_methods(['POST'])
def show_summary(request):
    lyrics = request.POST.get('lyrics')
    artist = request.POST.get('artist')
    title = request.POST.get('title')
    summary = None

    if lyrics:
        try:
            trimmed_lyrics = lyrics[:1000]  # ggf. kürzen
            result = summarizer(trimmed_lyrics, max_length=60, min_length=20, do_sample=False)
            summary = result[0]['summary_text']
        except Exception as e:
            summary = f"Fehler bei der Zusammenfassung: {str(e)}"
    else:
        summary = "Keine Lyrics übergeben."

    return render(request, 'summary.html', {
        'artist': artist,
        'title': title,
        'lyrics': lyrics,
        'summary': summary,
    })

from openai.types.chat import ChatCompletionUserMessageParam



def get_youtube_video(query):
    try:
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'extract_flat': 'in_playlist',  # funktioniert für ytsearch
            'force_generic_extractor': False,
            'noplaylist': True
        }

        with YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(f"ytsearch5:{query}", download=False)

            if not result or "entries" not in result:
                return None, None

            for entry in result["entries"]:
                if entry and entry.get("url"):
                    # `url` reicht bei Flat-Search aus
                    video_url = f"https://www.youtube.com/watch?v={entry['id']}"
                    return entry["id"], video_url

    except Exception as e:
        print(f"[YT] Fehler bei der Video-Suche: {e}")

    return None, None



def fetch_from_api(artist, title):
    try:
        # Verwenden Sie requests.utils.quote statt urllib.parse.quote
        from requests.utils import quote
        artist_encoded = quote(artist)
        title_encoded = quote(title)

        api_url = f"https://api.lyrics.ovh/v1/{artist_encoded}/{title_encoded}"
        response = requests.get(api_url, timeout=20)

        if response.status_code == 200:
            data = response.json()
            return data.get('lyrics', 'Keine Lyrics gefunden.'), None
        else:
            return None, f"Fehler {response.status_code}: Songtext nicht gefunden"

    except requests.exceptions.RequestException as e:
        return None, f"API-Fehler: {str(e)}"


def cache_lyrics(artist, title, lyrics, error):
    artist_clean = artist.strip()
    title_clean = title.strip()

    song, created = Song.objects.get_or_create(
        artist=artist_clean,
        title=title_clean
    )

    # Speichere Lyrics, wenn vorhanden, sonst speichere den Song trotzdem!
    if lyrics and not error:
        song.lyrics = lyrics

    song.save()  # <- immer speichern, nicht nur bei Lyrics
    
def get_or_create_full_song(artist, title):
    artist_clean = artist.strip()
    title_clean = title.strip()

    # Check if song with lyrics exists
    song = get_cached_lyrics(artist_clean, title_clean)
    if song:
        return song

    # Try fetching lyrics from API
    lyrics, error = fetch_from_api(artist_clean, title_clean)

    # Save song in DB, even if lyrics not found
    cache_lyrics(artist_clean, title_clean, lyrics if not error else None, error)

    # Return from DB
    return Song.objects.get(artist__iexact=artist_clean, title__iexact=title_clean)

# Hauptfunktion
def index(request):
    lyrics = None
    error = None
    artist = None
    title = None
    video_url = None  # <- NEU

    if request.method == 'POST':
        artist = request.POST.get('artist')
        title = request.POST.get('title')
    else:
        artist = request.GET.get('artist')
        title = request.GET.get('title')

    if artist and title:
        # Lyrics aus DB oder API holen
        song = get_cached_lyrics(artist, title)

        if song and song.lyrics:
            lyrics = song.lyrics
        else:
            lyrics, error = fetch_from_api(artist, title)
            cache_lyrics(artist, title, lyrics, error)

        # YouTube-Link suchen
        _, video_url = get_youtube_video(f"{artist} {title}")

    return render(request, 'index.html', {
        'lyrics': lyrics,
        'error': error,
        'artist': artist,
        'title': title,
        'video_url': video_url  # <- NEU
    })



import spacy
from django.shortcuts import render

# Lade das Modell einmal global (nicht bei jedem Request)
nlp = spacy.load("en_core_web_sm")  # oder "en_core_web_sm"

def analyze_ner(request):
    lyrics = request.POST.get('lyrics', '').strip()
    if not lyrics:
        return render(request, 'ner_result.html', {'error': "Keine Lyrics übermittelt."})

    doc = nlp(lyrics)
    raw_entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]

    # Duplikate entfernen:
    seen = set()
    unique_entities = []
    for ent in raw_entities:
        key = (ent["text"], ent["label"])
        if key not in seen:
            seen.add(key)
            unique_entities.append(ent)

    return render(request, 'ner_result.html', {'entities': unique_entities, 'lyrics': lyrics})



#testtest
def imprint(request):
    return render(request, 'imprint.html')


@require_http_methods(['POST'])
def analyze_lyrics(request):
    formatted_topics = []

    if request.method == "POST":
        lyrics = request.POST.get('lyrics', '')
        formatted_topics = []

        if lyrics:
            docs = [line.strip() for line in lyrics.split('\n') if line.strip()]

            # Optional: Mindestanzahl sichern (BERTopic braucht >5 docs)
            if len(docs) < 5:
                docs = docs * (6 // len(docs) + 1)

            umap_model = UMAP(n_neighbors=2, n_components=2, min_dist=0.0, metric='cosine')
            topic_model = BERTopic(language="multilingual", min_topic_size=2, umap_model=umap_model)

            print("Docs für BERTopic:", docs)
            print("Anzahl Docs:", len(docs))

            topics, _ = topic_model.fit_transform(docs)

            # Visualisierung
            fig = topic_model.visualize_topics()
            plot_html = pio.to_html(fig, full_html=false)

            fig_hierarchy = topic_model.visualize_hierarchy()
            hierarchy_html = pio.to_html(fig_hierarchy, full_html=False)

            topics_info = topic_model.get_topic_info()

            for i, row in topics_info.iterrows():
                topic_id = row['Topic']
                if topic_id == -1:
                    continue  # rausfiltern von "Rest"-Thema

                topic_words = topic_model.get_topic(topic_id)
                filtered_words = [word for word, _ in topic_words if word.strip() and word not in ENGLISH_STOP_WORDS]

                topic_name = ", ".join(filtered_words[:3]) if filtered_words else f"Thema {topic_id}"

                formatted_topics.append({
                    'id': topic_id,
                    'name': topic_name,
                    'words': filtered_words[:5]
                })
                print("Rendering mit Topics:", formatted_topics)

        else:
            formatted_topics.append({
                'id': 'n/a',
                'name': 'Keine Themen erkannt',
                'words': ['n/a']
            })
    else:
        lyrics = 'Keine Daten übermittelt.'

    return render(request, 'analysis_result.html', {
        'topics': formatted_topics,
        'original_lyrics': lyrics,
        'plot_html': plot_html,
        'hierarchy_html': hierarchy_html
    })


@require_http_methods(['POST'])
def deep_analyze_sentiment(request):
    if request.method == 'POST':
        lyrics = request.POST.get('lyrics', '')

        if not lyrics:
            return render(request, 'sentiment_result.html', {
                'sentiment': 'Keine Lyrics übergeben',
                'emoji': '❓',
                'original_lyrics': ''
            })

        truncated_lyrics = lyrics[:512]

        results = emotion_classifier(truncated_lyrics)
        emotions = results[0]
        emotions.sort(key=lambda x: x['score'], reverse=True)
        top_emotion = emotions[0]

        sentiment = top_emotion['label']
        emoji = EMOJI_MAP.get(sentiment, '❓')

    return render(request, 'deepsentiment_result.html', {
        'sentiment': sentiment.capitalize(),
        'emoji': emoji,
        'original_lyrics': lyrics,
        'scores': emotions[:5]
    })




# fast or regular
@require_http_methods(['POST'])
def analyze_sentiment(request):
    lyrics = request.POST.get('lyrics', '')
    sentiment_result = None
    emoji = '❓'

    if lyrics:
        analyzer = SentimentIntensityAnalyzer()
        sentiment = analyzer.polarity_scores(lyrics)
        score = sentiment['compound']

        if score >= 0.05:
            sentiment_result = "Positiv"
            emoji = "😊"
        elif score <= -0.05:
            sentiment_result = "Negativ"
            emoji = "😢"
        else:
            sentiment_result = "Neutral"
            emoji = "😐"

    return render(request, 'sentiment_result.html', {
        'sentiment': sentiment_result,
        'emoji': emoji,
        'original_lyrics': lyrics
    })


def search(request):
    context = {}

    if request.method == "POST":
        query = request.POST.get("query")
        if query:
            url = f"https://api.lyrics.ovh/suggest/{query}"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                # context["results"] = data.get("data", [])
                results = data.get("data", [])
                enriched_results = []
                for result in results:
                    title = result.get("title", "").strip()
                    artist = result.get("artist", {}).get("name", "").strip()

                    # Default: not liked
                    liked = False

                    if request.user.is_authenticated:
                        try:
                            song = Song.objects.get(title=title, artist=artist)
                            liked = request.user in song.liked.all()
                        except Song.DoesNotExist:
                            pass  # not in database, stay unliked

                    # Attach flag to the result
                    result["liked"] = liked
                    enriched_results.append(result)

                context["results"] = enriched_results
            else:
                context["error"] = "Fehler beim Abrufen der Songvorschläge."

    return render(request, "search.html", context)


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import redirect
import tempfile
import subprocess
import os
import json
import requests
import imageio_ffmpeg as ffmpeg
import uuid


@csrf_exempt
def recognize_audio(request):
    if request.method == 'POST':

        request.FILES.get('audio')
        audio_file = request.FILES['audio']

        print("Dateiname:", audio_file.name)
        print("Content-Type:", audio_file.content_type)
        print("Dateigröße:", audio_file.size)

        # Temporäre Input-Datei (.webm oder .ogg oder .whatever)
        input_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".webm")
        for chunk in audio_file.chunks():
            input_temp.write(chunk)
        input_temp.close()

        # Temporäre WAV-Datei (für fpcalc)
        output_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.wav")

        try:
            # Konvertieren mit ffmpeg
            ffmpeg_path = ffmpeg.get_ffmpeg_exe()
            subprocess.run([ffmpeg_path, '-y', '-i', input_temp.name, output_path], check=True)

            print("Konvertierte Datei:", output_path)

            # fpcalc ausführen...
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            fpcalc_path = os.path.join(BASE_DIR, 'fpcalc.exe')

            result = subprocess.run([fpcalc_path, '-json', output_path], capture_output=True, text=True)

            print("FPCalc stdout:", result.stdout)

            if result.returncode != 0:
                return JsonResponse({'error': 'Fingerprint-Fehler'}, status=500)

            data = json.loads(result.stdout)
            fingerprint = data['fingerprint']
            duration = data['duration']

            resp = requests.get("https://api.acoustid.org/v2/lookup", params={
                'client': 'LBUHnC6eBt',
                'duration': duration,
                'fingerprint': fingerprint,
                'meta': 'recordings+releasegroups+compress',
            })

            matches = resp.json().get("results", [])
            if matches and matches[0].get("recordings"):
                recording = matches[0]["recordings"][0]
                return JsonResponse({
                    'artist': recording.get("artists", [{}])[0].get("name"),
                    'title': recording.get("title"),
                })
            else:
                return JsonResponse({'error': 'Kein Treffer'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

        finally:
            if os.path.exists(input_temp.name):
                os.remove(input_temp.name)
            if os.path.exists(output_path):
                os.remove(output_path)

    return redirect('record_audio_page')


def record_audio_page(request):
    return render(request, "record_audio.html")