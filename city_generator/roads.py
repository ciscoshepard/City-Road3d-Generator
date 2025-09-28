"""
Road network generation system for the 3D city generator.
"""

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    import math
    import random
    HAS_NUMPY = False

from typing import List, Tuple, Set, Dict
from .config import CityConfig, ZoneType

class Road:
    """Represents a road segment."""
    
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], width: float, road_type: str = "local"):
        self.start = start
        self.end = end
        self.width = width
        self.road_type = road_type  # "main", "secondary", "local"
    
    def get_length(self) -> float:
        """Calculate road length."""
        if HAS_NUMPY:
            return np.sqrt((self.end[0] - self.start[0])**2 + (self.end[1] - self.start[1])**2)
        else:
            return math.sqrt((self.end[0] - self.start[0])**2 + (self.end[1] - self.start[1])**2)
    
    def get_direction(self) -> Tuple[float, float]:
        """Get normalized direction vector."""
        dx = self.end[0] - self.start[0]
        dy = self.end[1] - self.start[1]
        length = self.get_length()
        if length == 0:
            return (0, 0)
        return (dx / length, dy / length)

class Intersection:
    """Represents a road intersection."""
    
    def __init__(self, position: Tuple[int, int]):
        self.position = position
        self.connected_roads: List[Road] = []
    
    def add_road(self, road: Road):
        """Add a road to this intersection."""
        self.connected_roads.append(road)

class RoadNetwork:
    """Manages the road network generation and pathfinding."""
    
    def __init__(self, config: CityConfig):
        self.config = config
        self.roads: List[Road] = []
        self.intersections: Dict[Tuple[int, int], Intersection] = {}
        if HAS_NUMPY:
            self.road_grid = np.zeros((config.height, config.width), dtype=bool)
        else:
            self.road_grid = [[False for _ in range(config.width)] 
                             for _ in range(config.height)]
    
    def generate_road_network(self, zone_manager):
        """Generate the complete road network."""
        # 1. Generate main arterial roads
        self._generate_main_roads()
        
        # 2. Generate secondary roads
        self._generate_secondary_roads()
        
        # 3. Generate local roads within zones
        self._generate_local_roads(zone_manager)
        
        # 4. Connect zones with additional roads
        self._connect_zones(zone_manager)
        
        # 5. Update road grid for pathfinding
        self._update_road_grid()
    
    def _generate_main_roads(self):
        """Generate main arterial roads in a grid pattern."""
        # Vertical main roads
        for x in range(0, self.config.width, self.config.main_grid_size):
            if x < self.config.width:
                road = Road((x, 0), (x, self.config.height - 1), 
                           self.config.main_road_width, "main")
                self.roads.append(road)
                self._add_intersections_for_road(road)
        
        # Horizontal main roads
        for y in range(0, self.config.height, self.config.main_grid_size):
            if y < self.config.height:
                road = Road((0, y), (self.config.width - 1, y), 
                           self.config.main_road_width, "main")
                self.roads.append(road)
                self._add_intersections_for_road(road)
    
    def _generate_secondary_roads(self):
        """Generate secondary roads for better connectivity."""
        # Vertical secondary roads
        for x in range(self.config.secondary_grid_size, self.config.width, self.config.secondary_grid_size):
            if x % self.config.main_grid_size != 0:  # Don't overlap with main roads
                road = Road((x, 0), (x, self.config.height - 1), 
                           self.config.secondary_road_width, "secondary")
                self.roads.append(road)
                self._add_intersections_for_road(road)
        
        # Horizontal secondary roads
        for y in range(self.config.secondary_grid_size, self.config.height, self.config.secondary_grid_size):
            if y % self.config.main_grid_size != 0:  # Don't overlap with main roads
                road = Road((0, y), (self.config.width - 1, y), 
                           self.config.secondary_road_width, "secondary")
                self.roads.append(road)
                self._add_intersections_for_road(road)
    
    def _generate_local_roads(self, zone_manager):
        """Generate local roads within zones based on zone type and density."""
        for zone in zone_manager.zones:
            self._generate_zone_roads(zone)
    
    def _generate_zone_roads(self, zone):
        """Generate roads within a specific zone."""
        # Different road patterns based on zone type
        if zone.zone_type == ZoneType.RESIDENTIAL:
            self._generate_residential_roads(zone)
        elif zone.zone_type == ZoneType.COMMERCIAL:
            self._generate_commercial_roads(zone)
        elif zone.zone_type == ZoneType.BUSINESS:
            self._generate_business_roads(zone)
        elif zone.zone_type == ZoneType.INDUSTRIAL:
            self._generate_industrial_roads(zone)
        elif zone.zone_type == ZoneType.PARKS:
            self._generate_park_roads(zone)
        elif zone.zone_type == ZoneType.LEISURE:
            self._generate_leisure_roads(zone)
    
    def _generate_residential_roads(self, zone):
        """Generate residential road pattern (curved streets, cul-de-sacs)."""
        local_grid_size = 50
        
        # Create a local grid within the zone
        for x in range(zone.x, zone.x + zone.width, local_grid_size):
            for y in range(zone.y, zone.y + zone.height, local_grid_size):
                if x + local_grid_size <= zone.x + zone.width:
                    road = Road((x, y), (x + local_grid_size, y), 
                               self.config.local_road_width, "local")
                    self.roads.append(road)
                
                if y + local_grid_size <= zone.y + zone.height:
                    road = Road((x, y), (x, y + local_grid_size), 
                               self.config.local_road_width, "local")
                    self.roads.append(road)
    
    def _generate_commercial_roads(self, zone):
        """Generate commercial road pattern (regular grid for easy access)."""
        local_grid_size = 40
        
        for x in range(zone.x, zone.x + zone.width, local_grid_size):
            if x + local_grid_size <= zone.x + zone.width:
                for y in range(zone.y, zone.y + zone.height, local_grid_size * 2):
                    if y + local_grid_size <= zone.y + zone.height:
                        road = Road((x, y), (x + local_grid_size, y), 
                                   self.config.local_road_width, "local")
                        self.roads.append(road)
    
    def _generate_business_roads(self, zone):
        """Generate business district roads (wide avenues)."""
        local_grid_size = 60
        
        # Wide avenues for business district
        for x in range(zone.x, zone.x + zone.width, local_grid_size):
            if x < zone.x + zone.width:
                road = Road((x, zone.y), (x, zone.y + zone.height), 
                           self.config.secondary_road_width, "local")
                self.roads.append(road)
        
        for y in range(zone.y, zone.y + zone.height, local_grid_size):
            if y < zone.y + zone.height:
                road = Road((zone.x, y), (zone.x + zone.width, y), 
                           self.config.secondary_road_width, "local")
                self.roads.append(road)
    
    def _generate_industrial_roads(self, zone):
        """Generate industrial roads (wide for trucks)."""
        local_grid_size = 80
        
        for x in range(zone.x, zone.x + zone.width, local_grid_size):
            if x < zone.x + zone.width:
                road = Road((x, zone.y), (x, zone.y + zone.height), 
                           self.config.local_road_width * 1.5, "local")
                self.roads.append(road)
    
    def _generate_park_roads(self, zone):
        """Generate park roads (minimal, curved paths)."""
        # Only perimeter roads for parks
        if zone.width > 100 or zone.height > 100:
            # Perimeter road
            perimeter_points = [
                (zone.x, zone.y),
                (zone.x + zone.width, zone.y),
                (zone.x + zone.width, zone.y + zone.height),
                (zone.x, zone.y + zone.height),
                (zone.x, zone.y)
            ]
            
            for i in range(len(perimeter_points) - 1):
                road = Road(perimeter_points[i], perimeter_points[i + 1], 
                           self.config.local_road_width * 0.8, "local")
                self.roads.append(road)
    
    def _generate_leisure_roads(self, zone):
        """Generate leisure area roads (moderate density)."""
        local_grid_size = 45
        
        for x in range(zone.x, zone.x + zone.width, local_grid_size):
            for y in range(zone.y, zone.y + zone.height, local_grid_size * 2):
                if (x + local_grid_size <= zone.x + zone.width and 
                    y + local_grid_size <= zone.y + zone.height):
                    road = Road((x, y), (x + local_grid_size, y), 
                               self.config.local_road_width, "local")
                    self.roads.append(road)
    
    def _connect_zones(self, zone_manager):
        """Add connecting roads between different zones."""
        zones = zone_manager.zones
        
        for i, zone1 in enumerate(zones):
            for zone2 in zones[i + 1:]:
                distance = self._zone_distance(zone1, zone2)
                if distance < 150:  # Connect nearby zones
                    self._add_zone_connector(zone1, zone2)
    
    def _zone_distance(self, zone1, zone2) -> float:
        """Calculate distance between two zones."""
        center1 = (zone1.x + zone1.width // 2, zone1.y + zone1.height // 2)
        center2 = (zone2.x + zone2.width // 2, zone2.y + zone2.height // 2)
        
        if HAS_NUMPY:
            return np.sqrt((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)
        else:
            return math.sqrt((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)
    
    def _add_zone_connector(self, zone1, zone2):
        """Add a connecting road between two zones."""
        # Find the closest points between zones
        center1 = (zone1.x + zone1.width // 2, zone1.y + zone1.height // 2)
        center2 = (zone2.x + zone2.width // 2, zone2.y + zone2.height // 2)
        
        road = Road(center1, center2, self.config.local_road_width, "local")
        self.roads.append(road)
    
    def _add_intersections_for_road(self, road):
        """Add intersections at the endpoints of a road."""
        for point in [road.start, road.end]:
            if point not in self.intersections:
                self.intersections[point] = Intersection(point)
            self.intersections[point].add_road(road)
    
    def _update_road_grid(self):
        """Update the road grid for pathfinding and visualization."""
        for road in self.roads:
            # Bresenham's line algorithm to mark road cells
            self._draw_line_on_grid(road.start, road.end, road.width)
    
    def _draw_line_on_grid(self, start: Tuple[int, int], end: Tuple[int, int], width: float):
        """Draw a line on the road grid using Bresenham's algorithm."""
        x0, y0 = start
        x1, y1 = end
        
        # Bresenham's line algorithm
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        x, y = x0, y0
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        
        if dx > dy:
            err = dx / 2.0
            while x != x1:
                self._mark_road_point(x, y, width)
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2.0
            while y != y1:
                self._mark_road_point(x, y, width)
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy
        
        self._mark_road_point(x, y, width)
    
    def _mark_road_point(self, x: int, y: int, width: float):
        """Mark a point as a road with given width."""
        half_width = int(width // 2)
        
        for dx in range(-half_width, half_width + 1):
            for dy in range(-half_width, half_width + 1):
                nx, ny = x + dx, y + dy
                if (0 <= nx < self.config.width and 
                    0 <= ny < self.config.height):
                    if HAS_NUMPY:
                        self.road_grid[ny, nx] = True
                    else:
                        self.road_grid[ny][nx] = True
    
    def is_road(self, x: int, y: int) -> bool:
        """Check if a point is on a road."""
        if 0 <= x < self.config.width and 0 <= y < self.config.height:
            if HAS_NUMPY:
                return self.road_grid[y, x]
            else:
                return self.road_grid[y][x]
        return False
    
    def get_nearest_road(self, x: int, y: int) -> Tuple[int, int]:
        """Find the nearest road point to given coordinates."""
        min_distance = float('inf')
        nearest_point = (x, y)
        
        for road in self.roads:
            # Check multiple points along the road
            steps = max(1, int(road.get_length() // 10))
            for i in range(steps + 1):
                t = i / max(1, steps)
                road_x = int(road.start[0] + t * (road.end[0] - road.start[0]))
                road_y = int(road.start[1] + t * (road.end[1] - road.start[1]))
                
                if HAS_NUMPY:
                    distance = np.sqrt((x - road_x)**2 + (y - road_y)**2)
                else:
                    distance = math.sqrt((x - road_x)**2 + (y - road_y)**2)
                if distance < min_distance:
                    min_distance = distance
                    nearest_point = (road_x, road_y)
        
        return nearest_point