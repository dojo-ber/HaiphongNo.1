#functions wie get blablabla



import requests
from django.shortcuts import render


#Send request func
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
