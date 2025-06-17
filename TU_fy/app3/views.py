from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import generic
from .models import Playlist, PlaylistSong, Song
from .forms import PlaylistForm

    
    
class PlaylistOverview(LoginRequiredMixin, generic.ListView):
    model = Playlist
    template_name = 'playlist/overview_playlist.html'
    context_object_name = 'all_playlists'
    
    def get_queryset(self):
        # Stelle sicher, dass die Default-Playlist existiert
        if not Playlist.objects.filter(creator=self.request.user, is_default=True).exists():
            Playlist.objects.create(
                creator=self.request.user,
                name="Meine Favoriten",
                is_default=True
            )
        return Playlist.objects.filter(creator=self.request.user).order_by('-is_default','-created_at')
    
@login_required
def playlist_detail(request, pk):
    playlist = get_object_or_404(Playlist, pk=pk)
    songs = PlaylistSong.objects.filter(playlist=playlist).select_related("song").order_by('added_at')

    if playlist.creator != request.user:
        return redirect('index')

    # Enrich with like state
    enriched_songs = []
    for item in songs:
        item.liked = request.user in item.song.liked.all()
        enriched_songs.append(item)

    return render(request, 'playlist/detail_playlist.html', {
        'playlist': playlist,
        'songs': enriched_songs,
    })

def dashboard(request):
    # Check if default playlist exists
    if not Playlist.objects.filter(creator=request.user, is_default=True).exists():
        Playlist.objects.create(
            creator=request.user,
            name="Meine Favoriten",
            is_default=True
        )
    return render(request, 'dashboard.html')
    
class PlaylistCreateView(LoginRequiredMixin, generic.CreateView):
    model = Playlist
    form_class = PlaylistForm
    template_name = 'playlist/create_playlist.html'
    success_url = reverse_lazy('overview_playlist')

    def form_valid(self, form):
        messages.success(self.request, "Die Playlist wurde erfolgreich erstellt.")
        form.instance.creator = self.request.user
        return super().form_valid(form)
    
    
class PlaylistUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Playlist
    template_name = 'playlist/update_playlist.html'
    form_class = PlaylistForm
    success_url = reverse_lazy('overview_playlist')
    
    def dispatch(self, request, *args, **kwargs):
        playlist = get_object_or_404(Playlist, pk=kwargs['pk'])
        if playlist.creator != request.user or playlist.is_default:
            messages.error(request, "Du bist nicht berechtigt, diese Playlist zu bearbeiten.")
            return redirect('overview_playlist')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "Die Playlist wurde erflogreich bearbeitet.")
        return super().form_valid(form)


class PlaylistDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Playlist
    template_name = 'playlist/delete_playlist.html'
    context_object_name = 'playlist'
    success_url = reverse_lazy('overview_playlist')

    def dispatch(self, request, *args, **kwargs):
        playlist = get_object_or_404(Playlist, pk=kwargs['pk'])
        if playlist.creator != request.user or playlist.is_default:
            messages.error(request, "Du bist nicht berechtigt, diese Playlist zu löschen.")
            return redirect('overview_playlist')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, "Die Playlist wurde erfolgreich gelöscht.")
        return super().form_valid(form)
    
@require_http_methods(['POST'])
@login_required
def toggle_like_song(request):
    artist_name = request.POST.get("artist")
    song_title = request.POST.get("title")

    if not artist_name or not song_title:
        return redirect("index")  # or show a message

    # 1. Get or create the Song
    song, created = Song.objects.get_or_create(
        title=song_title.strip(),
        artist=artist_name.strip()
    )

    # 2. Get or create the user's "Meine Favoriten" playlist
    favorites, _ = Playlist.objects.get_or_create(
        creator=request.user,
        is_default=True,
        name="Meine Favoriten"
    )

    # 3. Check if the song is already in that playlist and liked
    is_liked = request.user in song.liked.all()
    is_in_playlist = PlaylistSong.objects.filter(playlist=favorites, song=song).exists()

    if is_liked and is_in_playlist:
        # UNLIKE and REMOVE from playlist
        song.liked.remove(request.user)
        PlaylistSong.objects.filter(playlist=favorites, song=song).delete()
    else:
        # LIKE and ADD to playlist
        song.liked.add(request.user)
        PlaylistSong.objects.get_or_create(playlist=favorites, song=song)

    return redirect('overview_playlist')