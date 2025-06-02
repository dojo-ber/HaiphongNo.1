from django.db import models
from django.contrib.auth.models import User


class Playlist(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    #Wenn nan User löscht, werden die assoziierten Playlist automatisch mitgelöscht
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=160)
    #playlist_image = models.ImageField(uplaod_to=)
    
    def __str__(self):
        return self.name
    
class Song(models.Model):
    title = models.CharField(max_length=160)
    artist = models.CharField(max_length=160)
    album = models.CharField(max_length=160, null=True)
    #n zu m Beziehung zu User, da keine weitere Attribute, reicht ManyToManyField
    liked = models.ManyToManyField(User, related_name='liked_songs', blank=True)
    
    #title und artist sind keine Primäreschlüssel, sollten aber nur einmal in Playlist vorkommen
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
    
    