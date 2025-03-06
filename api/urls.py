from django.urls import path
from .views import PlanTripView, health_check

urlpatterns = [
    path('plan-trip/', PlanTripView.as_view(), name='plan-trip'),
    path('health/', health_check, name='health_check'),
]
