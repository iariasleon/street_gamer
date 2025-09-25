from django.db import models
from django.contrib.auth.models import User

class PlayerLocation(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player.username} @ ({self.latitude}, {self.longitude})"


class Place(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    radius = models.FloatField(default=20)  # metros de radio para considerar "llegado"
    question = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class PlayerPlaceStatus(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('player', 'place')

    def __str__(self):
        return f"{self.player.username} - {self.place.name} - {'✔' if self.completed else '✘'}"
