from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import generic
from .models import Playlist, PlaylistSong, Song
from .forms import PlaylistForm
from django.core.exceptions import PermissionDenied
    
    
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
        return Playlist.objects.filter(creator=self.request.user).order_by('-created_at')
    
@login_required
def playlist_detail(request, pk):
    playlist = get_object_or_404(Playlist, pk=pk)
    songs = PlaylistSong.objects.filter(playlist=playlist).order_by('added_at')
    if playlist.creator != request.user:
        return redirect('index')
    return render(request, 'playlist/detail_playlist.html', {
        'playlist': playlist,
        'songs': songs,
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
        messages.success(self.request, "The playlist was created successfully.")
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
        messages.success(self.request, "The playlist was edited successfully.")
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
        messages.success(self.request, "The playlist was deleted successfully.")
        return super().form_valid(form)
    
    