"""
Route matching utilities for InGazo.

This module contains logic for:
- Finding rides that match a user's route
- Calculating route compatibility
- Matching passengers with drivers on similar routes
"""

from typing import List, Optional, Tuple

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db.models import F, QuerySet
from django.utils import timezone

from apps.rides.models import Ride


def find_matching_rides(
    start_point: Point,
    end_point: Point,
    departure_date: Optional[str] = None,
    min_seats: int = 1,
    max_price: Optional[float] = None,
    radius_km: float = 10.0,
    max_results: int = 50
) -> QuerySet:
    """
    Find rides that match the given route criteria.
    
    Uses PostGIS spatial queries to efficiently find rides where:
    - The ride's start location is within radius_km of the requested start
    - The ride's end location is within radius_km of the requested end
    - The ride has enough available seats
    - The ride's price is within budget (if specified)
    
    Args:
        start_point: Geographic point for pickup location (SRID 4326)
        end_point: Geographic point for dropoff location (SRID 4326)
        departure_date: Optional date filter (YYYY-MM-DD)
        min_seats: Minimum number of seats required
        max_price: Maximum price per seat
        radius_km: Search radius in kilometers
        max_results: Maximum number of results to return
    
    Returns:
        QuerySet of matching Ride objects, annotated with distances
    """
    # Base queryset - only scheduled, future rides with available seats
    queryset = Ride.objects.select_related(
        'driver', 'driver__user', 'vehicle'
    ).prefetch_related('stops').filter(
        status=Ride.RideStatus.SCHEDULED,
        departure_time__gte=timezone.now(),
        seats_available__gte=min_seats
    )
    
    # Spatial filter using PostGIS
    queryset = queryset.filter(
        start_location__distance_lte=(start_point, D(km=radius_km)),
        end_location__distance_lte=(end_point, D(km=radius_km))
    )
    
    # Date filter
    if departure_date:
        queryset = queryset.filter(departure_time__date=departure_date)
    
    # Price filter
    if max_price is not None:
        queryset = queryset.filter(price_per_seat__lte=max_price)
    
    # Annotate with distances for sorting and display
    queryset = queryset.annotate(
        start_distance=Distance('start_location', start_point),
        end_distance=Distance('end_location', end_point),
        total_distance=Distance('start_location', start_point) + Distance('end_location', end_point)
    )
    
    # Order by total distance (closest match first), then by departure time
    queryset = queryset.order_by('total_distance', 'departure_time')
    
    return queryset[:max_results]


def calculate_route_compatibility(
    ride_start: Point,
    ride_end: Point,
    passenger_start: Point,
    passenger_end: Point
) -> Tuple[float, float, float]:
    """
    Calculate how compatible a passenger's route is with a ride's route.
    
    Returns a tuple of:
    - start_distance: Distance from ride start to passenger pickup (meters)
    - end_distance: Distance from ride end to passenger dropoff (meters)
    - compatibility_score: 0-100 score (100 = perfect match)
    
    Args:
        ride_start: Ride's starting point
        ride_end: Ride's ending point
        passenger_start: Passenger's pickup point
        passenger_end: Passenger's dropoff point
    
    Returns:
        Tuple of (start_distance, end_distance, compatibility_score)
    """
    # Calculate distances in meters
    start_distance = ride_start.distance(passenger_start) * 111320  # Approx meters per degree
    end_distance = ride_end.distance(passenger_end) * 111320
    
    # Calculate compatibility score
    # Perfect match = 0 distance = 100 score
    # 10km distance = 0 score
    max_acceptable_distance = 10000  # 10km in meters
    
    start_score = max(0, 100 - (start_distance / max_acceptable_distance * 100))
    end_score = max(0, 100 - (end_distance / max_acceptable_distance * 100))
    
    # Average the scores
    compatibility_score = (start_score + end_score) / 2
    
    return (start_distance, end_distance, compatibility_score)


def find_rides_along_route(
    route_points: List[Point],
    departure_date: Optional[str] = None,
    min_seats: int = 1,
    radius_km: float = 5.0
) -> QuerySet:
    """
    Find rides that pass through any of the given route points.
    Useful for finding rides when the passenger can be picked up at multiple locations.
    
    Args:
        route_points: List of points along the passenger's acceptable route
        departure_date: Optional date filter
        min_seats: Minimum seats required
        radius_km: Search radius around each point
    
    Returns:
        QuerySet of matching rides
    """
    from django.db.models import Q
    
    if not route_points:
        return Ride.objects.none()
    
    # Build OR query for all points
    location_query = Q()
    for point in route_points:
        location_query |= Q(start_location__distance_lte=(point, D(km=radius_km)))
    
    queryset = Ride.objects.filter(
        status=Ride.RideStatus.SCHEDULED,
        departure_time__gte=timezone.now(),
        seats_available__gte=min_seats
    ).filter(location_query)
    
    if departure_date:
        queryset = queryset.filter(departure_time__date=departure_date)
    
    return queryset.distinct()


def suggest_pickup_point(
    ride: Ride,
    passenger_location: Point,
    max_detour_km: float = 5.0
) -> Optional[Point]:
    """
    Suggest the best pickup point for a passenger on a given ride.
    
    Considers:
    - The ride's route (start to end via stops)
    - The passenger's location
    - Maximum acceptable detour distance
    
    Args:
        ride: The Ride object
        passenger_location: Passenger's preferred location
        max_detour_km: Maximum detour driver is willing to make
    
    Returns:
        Suggested pickup point, or None if no suitable point found
    """
    # Simple implementation: check ride's start and stops
    best_point = None
    best_distance = float('inf')
    
    # Check start location
    start_dist = ride.start_location.distance(passenger_location) * 111320 / 1000  # km
    if start_dist <= max_detour_km and start_dist < best_distance:
        best_point = ride.start_location
        best_distance = start_dist
    
    # Check stops
    for stop in ride.stops.all():
        stop_dist = stop.location.distance(passenger_location) * 111320 / 1000  # km
        if stop_dist <= max_detour_km and stop_dist < best_distance:
            best_point = stop.location
            best_distance = stop_dist
    
    return best_point


# Future enhancements to implement:
# - Route interpolation for finding optimal pickup/dropoff points
# - Traffic-aware matching using external APIs
# - Machine learning-based compatibility scoring
# - Real-time route matching for flexible pickups

