from django.db import models

class Trip(models.Model):
    current_location = models.CharField(max_length=255)
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    current_cycle_used = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Trip from {self.current_location} to {self.dropoff_location}"

class LogSheet(models.Model):
    trip = models.ForeignKey(Trip, related_name='log_sheets', on_delete=models.CASCADE)
    date = models.DateField()
    log_data = models.JSONField()  # {grid: [], events: [], totals: {}}
    
    def __str__(self):
        return f"Log for {self.date} - {self.trip}"