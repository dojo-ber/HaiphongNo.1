from django.db import models


class Request(models.Model):
    artist = models.CharField(max_length=100)
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.artist

    class Meta:
            app_label = 'app1'


class Response(models.Model):
    artist = models.CharField(max_length=100)
    lyrics = models.CharField(max_length=2000)

    def __str__(self):
        return self.artist
