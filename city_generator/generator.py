"""
Main city generator that orchestrates the creation of zones, roads, and buildings.
"""

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    import math
    import random
    HAS_NUMPY = False

import json
from typing import Dict, List, Tuple
from .config import CityConfig, ZoneType
from .zones import ZoneManager
from .roads import RoadNetwork

class Building:
    """Represents a building in the city."""
    
    def __init__(self, x: int, y: int, width: int, height: int, floors: int, zone_type: ZoneType):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.floors = floors
        self.zone_type = zone_type
        self.building_height = floors * 3.5  # Assuming 3.5m per floor
    
    def get_bounds(self) -> Tuple[int, int, int, int]:
        """Get building bounds as (x1, y1, x2, y2)."""
        return (self.x, self.y, self.x + self.width, self.y + self.height)
    
    def to_dict(self) -> Dict:
        """Convert building to dictionary for JSON export."""
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'floors': self.floors,
            'building_height': self.building_height,
            'zone_type': self.zone_type.value
        }

class CityGenerator:
    """Main city generator class."""
    
    def __init__(self, config: CityConfig):
        self.config = config
        self.zone_manager = ZoneManager(config)
        self.road_network = RoadNetwork(config)
        self.buildings: List[Building] = []
        self.generation_complete = False
    
    def generate_city(self):
        """Generate the complete city with zones, roads, and buildings."""
        print("Generating city zones...")
        self.zone_manager.generate_zones()
        
        print("Generating road network...")
        self.road_network.generate_road_network(self.zone_manager)
        
        print("Generating buildings...")
        self._generate_buildings()
        
        self.generation_complete = True
        print(f"City generation complete! Generated {len(self.buildings)} buildings in {len(self.zone_manager.zones)} zones.")
    
    def _generate_buildings(self):
        """Generate buildings within each zone."""
        for zone in self.zone_manager.zones:
            self._generate_zone_buildings(zone)
    
    def _generate_zone_buildings(self, zone):
        """Generate buildings within a specific zone."""
        if zone.zone_type == ZoneType.PARKS:
            # Parks have minimal or no buildings
            return
        
        # Building parameters based on zone type
        min_building_size = self._get_min_building_size(zone.zone_type)
        max_building_size = self._get_max_building_size(zone.zone_type)
        building_spacing = self._get_building_spacing(zone.zone_type)
        
        # Generate buildings in a grid pattern within the zone
        y = zone.y + building_spacing
        while y < zone.y + zone.height - min_building_size[1]:
            x = zone.x + building_spacing
            while x < zone.x + zone.width - min_building_size[0]:
                # Check if this location is suitable for a building
                if self._can_place_building(x, y, min_building_size):
                    # Randomly vary building size
                    if HAS_NUMPY:
                        width = np.random.randint(min_building_size[0], max_building_size[0] + 1)
                        height = np.random.randint(min_building_size[1], max_building_size[1] + 1)
                    else:
                        width = random.randint(min_building_size[0], max_building_size[0])
                        height = random.randint(min_building_size[1], max_building_size[1])
                    
                    # Ensure building fits within zone
                    width = min(width, zone.x + zone.width - x)
                    height = min(height, zone.y + zone.height - y)
                    
                    # Generate number of floors based on zone type
                    floors = self._generate_building_floors(zone.zone_type)
                    
                    # Apply zone density
                    if HAS_NUMPY:
                        should_place = np.random.random() < zone.density
                    else:
                        should_place = random.random() < zone.density
                    
                    if should_place:
                        building = Building(x, y, width, height, floors, zone.zone_type)
                        self.buildings.append(building)
                        zone.buildings.append(building)
                
                x += max_building_size[0] + building_spacing
            y += max_building_size[1] + building_spacing
    
    def _get_min_building_size(self, zone_type: ZoneType) -> Tuple[int, int]:
        """Get minimum building size for zone type."""
        sizes = {
            ZoneType.RESIDENTIAL: (8, 10),
            ZoneType.COMMERCIAL: (12, 15),
            ZoneType.BUSINESS: (20, 25),
            ZoneType.LEISURE: (10, 12),
            ZoneType.INDUSTRIAL: (25, 30),
            ZoneType.PARKS: (5, 5)
        }
        return sizes.get(zone_type, (10, 10))
    
    def _get_max_building_size(self, zone_type: ZoneType) -> Tuple[int, int]:
        """Get maximum building size for zone type."""
        sizes = {
            ZoneType.RESIDENTIAL: (15, 20),
            ZoneType.COMMERCIAL: (25, 30),
            ZoneType.BUSINESS: (40, 50),
            ZoneType.LEISURE: (20, 25),
            ZoneType.INDUSTRIAL: (50, 60),
            ZoneType.PARKS: (8, 8)
        }
        return sizes.get(zone_type, (20, 20))
    
    def _get_building_spacing(self, zone_type: ZoneType) -> int:
        """Get spacing between buildings for zone type."""
        spacing = {
            ZoneType.RESIDENTIAL: 5,
            ZoneType.COMMERCIAL: 3,
            ZoneType.BUSINESS: 8,
            ZoneType.LEISURE: 6,
            ZoneType.INDUSTRIAL: 10,
            ZoneType.PARKS: 20
        }
        return spacing.get(zone_type, 5)
    
    def _can_place_building(self, x: int, y: int, size: Tuple[int, int]) -> bool:
        """Check if a building can be placed at the given location."""
        # Check if the area overlaps with roads
        for dx in range(size[0]):
            for dy in range(size[1]):
                if self.road_network.is_road(x + dx, y + dy):
                    return False
        
        # Check minimum distance from roads
        min_distance_to_road = 5
        for dx in range(-min_distance_to_road, size[0] + min_distance_to_road):
            for dy in range(-min_distance_to_road, size[1] + min_distance_to_road):
                if self.road_network.is_road(x + dx, y + dy):
                    if (abs(dx) < min_distance_to_road and abs(dy) < min_distance_to_road):
                        return False
        
        return True
    
    def _generate_building_floors(self, zone_type: ZoneType) -> int:
        """Generate number of floors for a building based on zone type."""
        min_floors = self.config.min_building_height[zone_type] // 3.5
        max_floors = self.config.max_building_height[zone_type] // 3.5
        
        min_floors = max(1, int(min_floors))
        max_floors = max(min_floors, int(max_floors))
        
        # Use different distributions for different zone types
        if zone_type == ZoneType.BUSINESS:
            # Business districts tend to have taller buildings
            if HAS_NUMPY:
                return int(np.random.exponential(max_floors / 3)) + min_floors
            else:
                # Fallback exponential-like distribution
                return min(max_floors, min_floors + int(random.expovariate(3.0 / max_floors) * max_floors))
        elif zone_type == ZoneType.RESIDENTIAL:
            # Residential areas have more varied heights
            if HAS_NUMPY:
                return np.random.randint(min_floors, min(max_floors, 8) + 1)
            else:
                return random.randint(min_floors, min(max_floors, 8))
        else:
            # Other zones have uniform distribution
            if HAS_NUMPY:
                return np.random.randint(min_floors, max_floors + 1)
            else:
                return random.randint(min_floors, max_floors)
    
    def get_city_stats(self) -> Dict:
        """Get statistics about the generated city."""
        if not self.generation_complete:
            return {"error": "City generation not complete"}
        
        zone_stats = {}
        for zone_type in ZoneType:
            zones = self.zone_manager.get_zones_by_type(zone_type)
            buildings = [b for b in self.buildings if b.zone_type == zone_type]
            zone_stats[zone_type.value] = {
                "zones": len(zones),
                "buildings": len(buildings),
                "total_area": sum(z.width * z.height for z in zones),
                "avg_building_height": (sum(b.building_height for b in buildings) / len(buildings)) if buildings else 0
            }
        
        return {
            "total_zones": len(self.zone_manager.zones),
            "total_buildings": len(self.buildings),
            "total_roads": len(self.road_network.roads),
            "total_intersections": len(self.road_network.intersections),
            "city_size": f"{self.config.width}x{self.config.height}",
            "zone_stats": zone_stats
        }
    
    def export_to_json(self, filename: str = None) -> Dict:
        """Export the city data to JSON format."""
        if not self.generation_complete:
            raise ValueError("City generation not complete")
        
        city_data = {
            "config": {
                "width": self.config.width,
                "height": self.config.height,
                "main_road_width": self.config.main_road_width,
                "secondary_road_width": self.config.secondary_road_width,
                "local_road_width": self.config.local_road_width
            },
            "zones": [
                {
                    "type": zone.zone_type.value,
                    "x": zone.x,
                    "y": zone.y,
                    "width": zone.width,
                    "height": zone.height,
                    "density": zone.density,
                    "color": self.config.get_zone_color(zone.zone_type)
                }
                for zone in self.zone_manager.zones
            ],
            "roads": [
                {
                    "start": road.start,
                    "end": road.end,
                    "width": road.width,
                    "type": road.road_type
                }
                for road in self.road_network.roads
            ],
            "buildings": [building.to_dict() for building in self.buildings],
            "intersections": [
                {
                    "position": pos,
                    "connected_roads": len(intersection.connected_roads)
                }
                for pos, intersection in self.road_network.intersections.items()
            ]
        }
        
        if filename:
            with open(filename, 'w') as f:
                json.dump(city_data, f, indent=2)
        
        return city_data
    
    def export_to_obj(self, filename: str):
        """Export the city to OBJ format for 3D viewing."""
        if not self.generation_complete:
            raise ValueError("City generation not complete")
        
        with open(filename, 'w') as f:
            f.write("# 3D City Model\n")
            f.write("# Generated by City-Road3d-Generator\n\n")
            
            vertex_count = 1
            
            # Export buildings as simple boxes
            for building in self.buildings:
                # Building vertices (8 vertices for a box)
                x, y = building.x, building.y
                w, h = building.width, building.height
                height = building.building_height
                
                # Bottom vertices
                f.write(f"v {x} 0 {y}\n")          # 1
                f.write(f"v {x+w} 0 {y}\n")        # 2
                f.write(f"v {x+w} 0 {y+h}\n")      # 3
                f.write(f"v {x} 0 {y+h}\n")        # 4
                
                # Top vertices
                f.write(f"v {x} {height} {y}\n")     # 5
                f.write(f"v {x+w} {height} {y}\n")   # 6
                f.write(f"v {x+w} {height} {y+h}\n") # 7
                f.write(f"v {x} {height} {y+h}\n")   # 8
                
                # Building faces
                base = vertex_count
                # Bottom face
                f.write(f"f {base} {base+1} {base+2} {base+3}\n")
                # Top face
                f.write(f"f {base+4} {base+7} {base+6} {base+5}\n")
                # Side faces
                f.write(f"f {base} {base+4} {base+5} {base+1}\n")
                f.write(f"f {base+1} {base+5} {base+6} {base+2}\n")
                f.write(f"f {base+2} {base+6} {base+7} {base+3}\n")
                f.write(f"f {base+3} {base+7} {base+4} {base}\n")
                
                vertex_count += 8
            
            # Export roads as flat rectangles
            for road in self.road_network.roads:
                x1, y1 = road.start
                x2, y2 = road.end
                width = road.width / 2
                
                # Calculate perpendicular direction for road width
                length = road.get_length()
                if length > 0:
                    # Normalized direction
                    dx = (x2 - x1) / length
                    dy = (y2 - y1) / length
                    # Perpendicular direction
                    px = -dy * width
                    py = dx * width
                    
                    # Road vertices
                    f.write(f"v {x1 + px} 0.1 {y1 + py}\n")  # 1
                    f.write(f"v {x1 - px} 0.1 {y1 - py}\n")  # 2
                    f.write(f"v {x2 - px} 0.1 {y2 - py}\n")  # 3
                    f.write(f"v {x2 + px} 0.1 {y2 + py}\n")  # 4
                    
                    # Road face
                    base = vertex_count
                    f.write(f"f {base} {base+1} {base+2} {base+3}\n")
                    vertex_count += 4