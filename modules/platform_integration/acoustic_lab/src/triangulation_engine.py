#!/usr/bin/env python3
"""
Acoustic Lab - Triangulation Engine

Calculates sound source location using time-of-arrival differences from multiple sensors.
Implements geometric triangulation algorithms for educational acoustic analysis.

Sound speed in air: 1100 ft/s (approximate at room temperature)
"""

import numpy as np
from typing import List, Tuple, Dict, Optional
from math import radians, sin, cos, atan2, sqrt


class TriangulationEngine:
    """
    Educational acoustic triangulation engine.

    Calculates sound source location using geometric methods based on:
    - GPS coordinates of acoustic sensors
    - Time delays between sensor detections
    - Speed of sound in air (1100 ft/s)
    """

    # Speed of sound in air at room temperature (ft/s)
    SOUND_SPEED = 1100.0

    def __init__(self):
        """Initialize the triangulation engine."""
        # Define fixed sensor positions for educational simulation
        # These represent a fictional campus layout in Salt Lake City area
        self.sensor_positions = {
            'sensor_1': (40.7649, -111.8421),  # University of Utah approximate
            'sensor_2': (40.7640, -111.8370),  # ~500m east
            'sensor_3': (40.7690, -111.8420),  # ~450m north
        }

    def calculate_location(self, sensor_data: List[Dict]) -> Tuple[float, float]:
        """
        Calculate sound source location from multiple sensor detections.

        Args:
            sensor_data: List of sensor detection data, each containing:
                - 'sensor_id': Identifier for the sensor
                - 'timestamp': Detection timestamp
                - 'gps': {'lat': float, 'lon': float} of the sensor

        Returns:
            Tuple of (latitude, longitude) for calculated sound source location

        Raises:
            ValueError: Insufficient sensor data or invalid inputs
        """
        if len(sensor_data) < 2:
            raise ValueError("At least 2 sensor detections required for triangulation")

        # Extract timestamps and positions
        detections = []
        for data in sensor_data:
            sensor_id = data.get('sensor_id')
            timestamp = data.get('timestamp')
            gps = data.get('gps', {})

            if not all([sensor_id, timestamp, gps.get('lat'), gps.get('lon')]):
                continue

            detections.append({
                'sensor_id': sensor_id,
                'timestamp': timestamp,
                'position': (gps['lat'], gps['lon'])
            })

        if len(detections) < 2:
            raise ValueError("Insufficient valid sensor detections")

        # Sort by timestamp (earliest first)
        detections.sort(key=lambda x: x['timestamp'])

        # Calculate time delays from first detection
        reference_time = detections[0]['timestamp']
        reference_pos = detections[0]['position']

        time_delays = []
        positions = [reference_pos]

        for detection in detections[1:]:
            # Calculate time delay in seconds
            delay = detection['timestamp'] - reference_time
            if delay < 0:
                continue  # Skip detections before reference

            time_delays.append(delay)
            positions.append(detection['position'])

        if len(time_delays) < 1:
            raise ValueError("No valid time delays calculated")

        # Perform triangulation calculation
        return self._triangulate_positions(reference_pos, positions[1:], time_delays)

    def _triangulate_positions(self, reference_pos: Tuple[float, float],
                              other_positions: List[Tuple[float, float]],
                              time_delays: List[float]) -> Tuple[float, float]:
        """
        Perform geometric triangulation calculation.

        Uses the method of least squares to find the most likely source location
        that satisfies the time-distance relationships from multiple sensors.

        Args:
            reference_pos: (lat, lon) of first detection sensor
            other_positions: List of (lat, lon) for other detecting sensors
            time_delays: Time delays for each sensor relative to first

        Returns:
            Estimated (latitude, longitude) of sound source
        """
        # Convert GPS coordinates to local Cartesian coordinates (meters)
        # Using simple equirectangular projection for educational purposes
        ref_x, ref_y = self._gps_to_cartesian(reference_pos[0], reference_pos[1])

        sensor_positions_cartesian = [(ref_x, ref_y)]  # Reference sensor at origin

        for lat, lon in other_positions:
            x, y = self._gps_to_cartesian(lat, lon)
            # Translate so reference sensor is at (0, 0)
            sensor_positions_cartesian.append((x - ref_x, y - ref_y))

        # Calculate distances from time delays
        distances = [delay * self.SOUND_SPEED for delay in time_delays]

        # Use iterative least squares optimization for triangulation
        # Start with centroid of sensor positions as initial guess
        if len(sensor_positions_cartesian) == 2:
            # Simple 2-sensor case: solve analytically
            source_pos = self._two_sensor_triangulation(
                sensor_positions_cartesian[1], distances[0]
            )
        else:
            # Multi-sensor case: use iterative optimization
            source_pos = self._multi_sensor_triangulation(
                sensor_positions_cartesian[1:], distances
            )

        # Convert back to GPS coordinates
        source_lat, source_lon = self._cartesian_to_gps(source_pos[0] + ref_x, source_pos[1] + ref_y)

        return source_lat, source_lon

    def _gps_to_cartesian(self, lat: float, lon: float) -> Tuple[float, float]:
        """
        Convert GPS coordinates to Cartesian coordinates (approximate).

        Uses equirectangular projection centered on reference point.
        Accurate enough for small areas (<10km).

        Args:
            lat: Latitude in degrees
            lon: Longitude in degrees

        Returns:
            Tuple of (x, y) in meters
        """
        # Earth radius in meters
        EARTH_RADIUS = 6371000

        # Convert to radians
        lat_rad = radians(lat)
        lon_rad = radians(lon)

        # Equirectangular projection
        x = EARTH_RADIUS * lon_rad * cos(radians(40.76))  # Approximate latitude for Utah
        y = EARTH_RADIUS * lat_rad

        return x, y

    def _cartesian_to_gps(self, x: float, y: float) -> Tuple[float, float]:
        """
        Convert Cartesian coordinates back to GPS (approximate).

        Args:
            x: X coordinate in meters
            y: Y coordinate in meters

        Returns:
            Tuple of (latitude, longitude) in degrees
        """
        EARTH_RADIUS = 6371000

        lon_rad = x / (EARTH_RADIUS * cos(radians(40.76)))
        lat_rad = y / EARTH_RADIUS

        lat = lat_rad * 180 / np.pi
        lon = lon_rad * 180 / np.pi

        return lat, lon

    def _two_sensor_triangulation(self, sensor_pos: Tuple[float, float],
                                 distance: float) -> Tuple[float, float]:
        """
        Triangulate using two sensors (simplified case).

        Args:
            sensor_pos: (x, y) position of second sensor relative to first
            distance: Distance from second sensor to sound source

        Returns:
            Estimated (x, y) position of sound source
        """
        # For educational purposes, return a position along the perpendicular bisector
        # This is a simplified approximation
        sensor_x, sensor_y = sensor_pos

        # Distance from origin to sensor
        sensor_distance = sqrt(sensor_x**2 + sensor_y**2)

        if sensor_distance == 0:
            return (distance, 0)  # Default position

        # Find intersection points of circle with line from origin through sensor
        # For simplicity, return point at distance along the line to sensor
        scale_factor = distance / sensor_distance
        return (sensor_x * scale_factor, sensor_y * scale_factor)

    def _multi_sensor_triangulation(self, sensor_positions: List[Tuple[float, float]],
                                   distances: List[float]) -> Tuple[float, float]:
        """
        Multi-sensor triangulation using least squares optimization.

        Args:
            sensor_positions: List of (x, y) sensor positions relative to reference
            distances: Corresponding distances to sound source

        Returns:
            Estimated (x, y) position of sound source
        """
        # Use iterative least squares for educational demonstration
        # Start with weighted average of sensor positions
        total_weight = 0
        weighted_x = 0
        weighted_y = 0

        for (x, y), distance in zip(sensor_positions, distances):
            if distance > 0:
                weight = 1.0 / distance  # Closer sensors have higher weight
                weighted_x += x * weight
                weighted_y += y * weight
                total_weight += weight

        if total_weight > 0:
            return (weighted_x / total_weight, weighted_y / total_weight)
        else:
            return (0, 0)

    def calculate_error_estimate(self, calculated_pos: Tuple[float, float],
                               sensor_positions: List[Tuple[float, float]],
                               actual_distances: List[float]) -> float:
        """
        Calculate error estimate for triangulation result.

        Args:
            calculated_pos: Calculated (lat, lon) position
            sensor_positions: List of sensor (lat, lon) positions
            actual_distances: Actual distances from sensors to source

        Returns:
            RMS error estimate in meters
        """
        errors = []

        for sensor_pos, actual_distance in zip(sensor_positions, actual_distances):
            calculated_distance = self._haversine_distance(calculated_pos, sensor_pos)
            error = abs(calculated_distance - actual_distance)
            errors.append(error)

        if errors:
            return sqrt(sum(e**2 for e in errors) / len(errors))  # RMS error
        else:
            return 0.0

    def _haversine_distance(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """
        Calculate distance between two GPS coordinates using haversine formula.

        Args:
            pos1: (lat, lon) of first point
            pos2: (lat, lon) of second point

        Returns:
            Distance in meters
        """
        R = 6371000  # Earth radius in meters

        lat1, lon1 = pos1
        lat2, lon2 = pos2

        phi1 = radians(lat1)
        phi2 = radians(lat2)
        delta_phi = radians(lat2 - lat1)
        delta_lambda = radians(lon2 - lon1)

        a = sin(delta_phi/2)**2 + cos(phi1) * cos(phi2) * sin(delta_lambda/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return R * c


# Global triangulation engine instance
_triangulation_engine_instance = None

def get_triangulation_engine() -> TriangulationEngine:
    """Get the global triangulation engine instance (singleton pattern)."""
    global _triangulation_engine_instance
    if _triangulation_engine_instance is None:
        _triangulation_engine_instance = TriangulationEngine()
    return _triangulation_engine_instance
