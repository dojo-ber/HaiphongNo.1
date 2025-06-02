#functions wie get blablabla

import requests
from bertopic import BERTopic
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from transformers import pipeline
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


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


#Send request func
def start(request):
    return render(request, 'startingscreen.html')


@login_required
def index(request):
    lyrics = None
    error = None

    artist = request.GET.get('artist')
    title = request.GET.get('title')

    if artist and title:
        api_url = f"https://api.lyrics.ovh/v1/{artist}/{title}"
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()
            lyrics = data.get('lyrics', 'Keine Lyrics gefunden.')
        else:
            error = "Songtext nicht gefunden oder Fehler bei der API."

    return render(request, 'index.html', {
        'lyrics': lyrics,
        'error': error
    })


def imprint(request):
    return render(request, 'imprint.html')


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

            topic_model = BERTopic(language="multilingual", min_topic_size=2)

            print("Docs für BERTopic:", docs)
            print("Anzahl Docs:", len(docs))

            topics, _ = topic_model.fit_transform(docs)
            topics_info = topic_model.get_topic_info()

            for i, row in topics_info.iterrows():
                topic_id = row['Topic']
                if topic_id == -1:
                    continue  # rausfiltern von "Rest"-Thema

                topic_words = topic_model.get_topic(topic_id)
                filtered_words = [word for word, _ in topic_words if word not in ENGLISH_STOP_WORDS]

                formatted_topics.append({
                    'id': topic_id,
                    'name': f"Thema {topic_id}",
                    'words': filtered_words[:5]  # Top 5 Wörter
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
        'original_lyrics': lyrics
    })

def deep_analyze_sentiment(request):
        if request.method == 'POST':
            lyrics = request.POST.get('lyrics', '')

            if not lyrics:
                return render(request, 'sentiment_result.html', {
                    'sentiment': 'Keine Lyrics übergeben',
                    'emoji': '❓',
                    'original_lyrics': ''
                })

            results = emotion_classifier(lyrics)
            emotions = results[0]
            emotions.sort(key=lambda x: x['score'], reverse=True)
            top_emotion = emotions[0]

            sentiment = top_emotion['label']
            emoji = EMOJI_MAP.get(sentiment, '❓')

        return render(request, 'sentiment_result.html', {
                'sentiment': sentiment.capitalize(),
                'emoji': emoji,
                'original_lyrics': lyrics,
                'scores': emotions[:5]  # Optional: Top 5 anzeigen
        })
#fast or regular
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



