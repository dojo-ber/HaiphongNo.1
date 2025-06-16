from django.db import models
from django.contrib.auth.models import User
import os
def playlist_image_path(instance, filename):
    # Datei wird gespeichert unter: playlist_images/user_id/playlist_id/filename
    return f'playlist_images/{instance.creator.id}/{instance.id}/{filename}'

class Playlist(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    #Wenn nan User löscht, werden die assoziierten Playlist automatisch mitgelöscht
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=160)
    is_default = models.BooleanField(default=False)  # Default Playlist
    image = models.ImageField(
    upload_to='playlist_images/',
    blank=True,
    null=True,
    default='playlist_images/default_cover.jpg'
)
    def __str__(self):
        return self.name
class Song(models.Model):
    title = models.CharField(max_length=160)
    artist = models.CharField(max_length=160)
    album = models.CharField(max_length=160, null=True, blank=True)
    lyrics = models.TextField(null=True, blank=True)  # NEU: Lyrics-Feld hinzugefügt
    liked = models.ManyToManyField(User, related_name='liked_songs', blank=True)
    
    class Meta:
        unique_together = ('title', 'artist')

    def __str__(self):
        return f"{self.title} - {self.artist}"

# da extra Attribute added_at, muss extra Model gemacht werden
class PlaylistSong(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.playlist.name} - {self.song.title} by {self.song.artist}"
    
    