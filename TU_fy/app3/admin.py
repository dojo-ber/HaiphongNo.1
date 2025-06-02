from django.contrib import admin
from .models import Playlist, PlaylistSong, Song

# Register your models here.
admin.site.register(Playlist)
admin.site.register(PlaylistSong)
admin.site.register(Song)