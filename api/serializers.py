from rest_framework import serializers
from .models import Trip, LogSheet

class TripInputSerializer(serializers.Serializer):
    current_location = serializers.CharField(max_length=255, trim_whitespace=True)
    pickup_location = serializers.CharField(max_length=255, trim_whitespace=True)
    dropoff_location = serializers.CharField(max_length=255, trim_whitespace=True)
    current_cycle_used = serializers.FloatField(min_value=0, max_value=70)

class LogSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogSheet
        fields = ['date', 'log_data']

class TripSerializer(serializers.ModelSerializer):
    log_sheets = LogSheetSerializer(many=True, read_only=True)
    
    class Meta:
        model = Trip
        fields = ['id', 'current_location', 'pickup_location', 'dropoff_location', 
                  'current_cycle_used', 'created_at', 'log_sheets']