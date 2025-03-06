from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import TripInputSerializer
from .models import Trip, LogSheet
from eld.utils import ELDLogGenerator
from datetime import datetime

class PlanTripView(APIView):
    def post(self, request):
        serializer = TripInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            generator = ELDLogGenerator(serializer.validated_data)
            trip_data = generator.generate_log_sheets()
            
            trip = Trip.objects.create(**serializer.validated_data)
            for log in trip_data['log_sheets']:
                LogSheet.objects.create(
                    trip=trip,
                    date=datetime.strptime(log['date'], '%Y-%m-%d').date(),
                    log_data=log
                )
            
            return Response(trip_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)