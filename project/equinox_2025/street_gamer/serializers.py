from rest_framework import serializers
from .models import PlayerLocation, Place

class PlayerLocationSerializer(serializers.ModelSerializer):
    player = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = PlayerLocation
        fields = ['id', 'player', 'latitude', 'longitude', 'timestamp']

class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ['id', 'name', 'description', 'latitude', 'longitude', 'radius', 'question', 'answer']
