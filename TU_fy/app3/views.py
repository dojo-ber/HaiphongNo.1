from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import generic
from .models import Playlist, PlaylistSong, Song
from .forms import PlaylistForm


# View Classes machen das ganze viel einfacher
class PlaylistCreateView(LoginRequiredMixin, generic.CreateView):
    model = Playlist
    form_class = PlaylistForm
    template_name = 'playlist/create_playlist.html'
    success_url = reverse_lazy('overview_playlist')
    
    def form_valid(self, form):
        messages.success(self.request, "The playlist was created successfully.")
        form.instance.creator = self.request.user
        return super().form_valid(form)
    
    
class PlaylistOverview(LoginRequiredMixin, generic.ListView):
    model = Playlist
    template_name = 'playlist/overview_playlist.html'
    context_object_name = 'all_playlists'
    
    def get_queryset(self):
        return Playlist.objects.filter(creator=self.request.user).order_by('-created_at')
    
    
@login_required
def playlist_detail(request, playlist_id):
    playlist = get_object_or_404(Playlist, pk=playlist_id)
    songs = PlaylistSong.objects.filter(playlist=playlist).order_by('added_at')
    if playlist.creator != request.user:
        return redirect('index')
    return render(request, 'playlist/detail_playlist.html', {
        'playlist': playlist,
        'songs': songs,
    })
    
class PlaylistDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Playlist
    template_name = 'playlist/delete_playlist.html'
    context_object_name = 'playlist'
    success_url = reverse_lazy('overview_playlist')

    def get_queryset(self):
        return Playlist.objects.filter(creator=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "The playlist was deleted successfully.")
        return super().form_valid(form)
