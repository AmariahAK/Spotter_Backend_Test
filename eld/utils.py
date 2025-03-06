import requests
import logging
from datetime import datetime, timedelta
from django.conf import settings

logger = logging.getLogger(__name__)

class ELDLogGenerator:
    def __init__(self, trip_data):
        self.current_location = trip_data['current_location']
        self.pickup_location = trip_data['pickup_location']
        self.dropoff_location = trip_data['dropoff_location']
        self.current_cycle_used = trip_data['current_cycle_used']
        self.route_details = None
        self.log_sheets = []
        
        self.max_drive_hours = 11
        self.max_on_duty_hours = 14
        self.min_rest_hours = 10
        self.max_cycle_hours = 70
        self.fuel_interval = 1000
        self.fuel_time = 0.5
        self.pickup_dropoff_time = 1
        self.avg_speed = 55

    def get_coordinates(self, address):
        url = "https://api.openrouteservice.org/geocode/search"
        headers = {'Authorization': settings.OPENROUTE_API_KEY}
        params = {'text': address, 'size': 1}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'features' in data and data['features']:
                    coords = data['features'][0]['geometry']['coordinates']
                    logger.info(f"Geocoded {address} to {coords}")
                    return coords
                logger.warning(f"No features for {address}: {response.text}")
            else:
                logger.error(f"Geocode failed for {address}: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Geocode exception for {address}: {str(e)}")
        return None

    def get_route_leg(self, start_coords, end_coords):
        url = "https://api.openrouteservice.org/v2/directions/driving-hgv"
        headers = {'Authorization': settings.OPENROUTE_API_KEY, 'Content-Type': 'application/json'}
        payload = {'coordinates': [start_coords, end_coords], 'instructions': True, 'geometry': True}
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=5)
            if response.status_code == 200:
                route = response.json()['routes'][0]
                distance_miles = route['summary']['distance'] / 1609.34
                duration_hours = route['summary']['duration'] / 3600
                logger.info(f"Route from {start_coords} to {end_coords}: {distance_miles} mi, {duration_hours} hr")
                return {
                    'distance': round(distance_miles, 2),
                    'duration': round(duration_hours, 2),
                    'geometry': route['geometry']
                }
            logger.error(f"Route failed: {response.status_code} - {response.text}")
            return None
        except Exception as e:
            logger.error(f"Route exception: {str(e)}")
            return None

    def calculate_route(self):
        coords = {
            'current': self.get_coordinates(self.current_location),
            'pickup': self.get_coordinates(self.pickup_location),
            'dropoff': self.get_coordinates(self.dropoff_location)
        }
        if not all(coords.values()):
            raise ValueError("Failed to geocode one or more locations")
        
        leg1 = self.get_route_leg(coords['current'], coords['pickup'])
        leg2 = self.get_route_leg(coords['pickup'], coords['dropoff'])
        if not (leg1 and leg2):
            raise ValueError("Failed to calculate route")
        
        self.route_details = {
            'legs': [
                {'from': self.current_location, 'to': self.pickup_location, **leg1},
                {'from': self.pickup_location, 'to': self.dropoff_location, **leg2}
            ],
            'total_distance': leg1['distance'] + leg2['distance'],
            'total_duration': leg1['duration'] + leg2['duration']
        }
        logger.info(f"Route calculated: {self.route_details}")
        return self.route_details

    def generate_log_sheets(self):
        if not self.route_details:
            logger.info("Calculating route...")
            self.calculate_route()
        
        total_distance = self.route_details['total_distance']
        driving_time = self.route_details['total_duration']
        fuel_stops = max(0, int(total_distance / self.fuel_interval))
        logger.info(f"Total Distance: {total_distance}, Driving Time: {driving_time}, Fuel Stops: {fuel_stops}")
        
        current_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
        remaining_cycle = self.max_cycle_hours - self.current_cycle_used
        day_log = self._init_day_log(current_time.date())
        
        current_time, day_log = self._add_event(day_log, 'On duty', current_time, self.pickup_dropoff_time, "Loading")
        leg1_time = self.route_details['legs'][0]['duration']
        current_time, day_log, remaining_cycle = self._add_driving(day_log, current_time, leg1_time, remaining_cycle)
        
        leg2_time = self.route_details['legs'][1]['duration']
        time_per_segment = leg2_time / (fuel_stops + 1) if fuel_stops else leg2_time
        
        for i in range(fuel_stops + 1):
            current_time, day_log, remaining_cycle = self._add_driving(day_log, current_time, time_per_segment, remaining_cycle)
            if i < fuel_stops:
                current_time, day_log = self._add_event(day_log, 'On duty', current_time, self.fuel_time, "Fueling")
        
        current_time, day_log = self._add_event(day_log, 'On duty', current_time, self.pickup_dropoff_time, "Unloading")
        self._finalize_day(day_log)
        logger.info(f"Log sheets generated: {self.log_sheets}")
        return {'route_details': self.route_details, 'log_sheets': self.log_sheets}

    def _init_day_log(self, date):
        return {
            'date': date.strftime('%Y-%m-%d'),
            'grid': ['OFF'] * 96,
            'events': [],
            'totals': {'driving': 0, 'on_duty': 0, 'off_duty': 0, 'sleeper': 0}
        }

    def _add_event(self, day_log, status, start_time, duration_hours, activity=None):
        end_time = start_time + timedelta(hours=duration_hours)
        if end_time.date() > start_time.date():
            self._finalize_day(day_log)
            day_log = self._init_day_log(end_time.date())
            start_time = end_time.replace(hour=8, minute=0)
            end_time = start_time + timedelta(hours=duration_hours)
        
        event = {'status': status, 'start': start_time.strftime('%H:%M'), 'end': end_time.strftime('%H:%M'), 'duration': duration_hours}
        if activity:
            event['activity'] = activity
        
        start_idx = int((start_time.hour * 4) + (start_time.minute / 15))
        end_idx = int((end_time.hour * 4) + (end_time.minute / 15))
        status_code = {'Driving': 'D', 'On duty': 'ON', 'Off duty': 'OFF', 'Sleeper berth': 'SB'}[status]
        
        for i in range(start_idx, min(end_idx, 96)):
            day_log['grid'][i] = status_code
        
        day_log['events'].append(event)
        # Fix: Use 'sleeper' instead of 'sleeper_berth'
        total_key = 'sleeper' if status == 'Sleeper berth' else status.lower().replace(' ', '_')
        day_log['totals'][total_key] += duration_hours
        return end_time, day_log

    def _add_driving(self, day_log, start_time, drive_time, remaining_cycle):
        while drive_time > 0:
            available = min(self.max_drive_hours - day_log['totals']['driving'],
                            self.max_on_duty_hours - day_log['totals']['on_duty'],
                            remaining_cycle, drive_time)
            if available <= 0:
                self._finalize_day(day_log)
                start_time = start_time.replace(hour=8, minute=0) + timedelta(days=1)
                day_log = self._init_day_log(start_time.date())
                start_time, day_log = self._add_event(day_log, 'Sleeper berth', start_time, self.min_rest_hours)
                remaining_cycle = self.max_cycle_hours if start_time.weekday() == 0 else remaining_cycle
                continue
            
            start_time, day_log = self._add_event(day_log, 'Driving', start_time, available)
            drive_time -= available
            remaining_cycle -= available
        
        return start_time, day_log, remaining_cycle

    def _finalize_day(self, day_log):
        self.log_sheets.append(day_log)