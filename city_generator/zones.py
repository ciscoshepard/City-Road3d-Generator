"""
Zone management system for the 3D city generator.
"""

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    import math
    import random
    HAS_NUMPY = False

try:
    from noise import pnoise2
    HAS_NOISE = True
except ImportError:
    HAS_NOISE = False
    
    def pnoise2(x, y, octaves=1, persistence=0.5, lacunarity=2.0):
        """Simple fallback noise function"""
        return (math.sin(x * 0.1) * math.cos(y * 0.1) + 
                math.sin(x * 0.05) * math.cos(y * 0.05) * 0.5)
from typing import List, Tuple, Dict
from .config import ZoneType, CityConfig

class Zone:
    """Represents a zone in the city."""
    
    def __init__(self, zone_type: ZoneType, x: int, y: int, width: int, height: int, density: float = 1.0):
        self.zone_type = zone_type
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.density = density
        self.buildings = []
    
    def get_bounds(self) -> Tuple[int, int, int, int]:
        """Get zone boundaries as (x1, y1, x2, y2)."""
        return (self.x, self.y, self.x + self.width, self.y + self.height)
    
    def contains_point(self, x: int, y: int) -> bool:
        """Check if a point is within this zone."""
        return (self.x <= x < self.x + self.width and 
                self.y <= y < self.y + self.height)

class ZoneManager:
    """Manages zones within the city."""
    
    def __init__(self, config: CityConfig):
        self.config = config
        self.zones: List[Zone] = []
        if HAS_NUMPY:
            self.zone_grid = np.zeros((config.height, config.width), dtype=int)
        else:
            self.zone_grid = [[0 for _ in range(config.width)] 
                             for _ in range(config.height)]
        self.zone_type_map = {}
        
    def generate_zones(self):
        """Generate zones using Voronoi-like algorithm with noise."""
        # Calculate number of zones based on city size and distribution
        total_area = self.config.width * self.config.height
        zone_areas = {}
        
        for zone_type, percentage in self.config.zone_distribution.items():
            zone_areas[zone_type] = int(total_area * percentage)
        
        # Generate zone seeds using noise
        seeds = self._generate_zone_seeds(zone_areas)
        
        # Create zone grid
        if HAS_NUMPY:
            self.zone_grid = np.zeros((self.config.height, self.config.width), dtype=int)
        else:
            self.zone_grid = [[0 for _ in range(self.config.width)] 
                             for _ in range(self.config.height)]
        
        # Assign each cell to the nearest seed
        for y in range(self.config.height):
            for x in range(self.config.width):
                # Add noise to make zones more organic
                noise_val = pnoise2(x * self.config.noise_scale, 
                                  y * self.config.noise_scale,
                                  octaves=self.config.noise_octaves)
                
                closest_zone_id = self._find_closest_zone(x, y, seeds, noise_val)
                if HAS_NUMPY:
                    self.zone_grid[y, x] = closest_zone_id
                else:
                    self.zone_grid[y][x] = closest_zone_id
        
        # Convert grid to zone objects
        self._create_zone_objects(seeds)
    
    def _generate_zone_seeds(self, zone_areas: Dict[ZoneType, int]) -> Dict[int, Tuple[int, int, ZoneType]]:
        """Generate seed points for zones."""
        seeds = {}
        zone_id = 1
        
        for zone_type, area in zone_areas.items():
            # Calculate approximate number of zones for this type
            avg_zone_size = 10000  # 100x100 average zone size
            num_zones = max(1, area // avg_zone_size)
            
            for _ in range(num_zones):
                # Random position with some clustering
                if zone_type == ZoneType.BUSINESS:
                    # Business zones tend to be in the center
                    if HAS_NUMPY:
                        x = int(np.random.normal(self.config.width // 2, self.config.width // 6))
                        y = int(np.random.normal(self.config.height // 2, self.config.height // 6))
                    else:
                        x = int(random.gauss(self.config.width // 2, self.config.width // 6))
                        y = int(random.gauss(self.config.height // 2, self.config.height // 6))
                elif zone_type == ZoneType.PARKS:
                    # Parks are more distributed
                    if HAS_NUMPY:
                        x = np.random.randint(0, self.config.width)
                        y = np.random.randint(0, self.config.height)
                    else:
                        x = random.randint(0, self.config.width - 1)
                        y = random.randint(0, self.config.height - 1)
                else:
                    # Other zones have moderate clustering
                    if HAS_NUMPY:
                        x = int(np.random.normal(self.config.width // 2, self.config.width // 4))
                        y = int(np.random.normal(self.config.height // 2, self.config.height // 4))
                    else:
                        x = int(random.gauss(self.config.width // 2, self.config.width // 4))
                        y = int(random.gauss(self.config.height // 2, self.config.height // 4))
                
                # Ensure seeds are within bounds
                x = max(0, min(self.config.width - 1, x))
                y = max(0, min(self.config.height - 1, y))
                
                seeds[zone_id] = (x, y, zone_type)
                self.zone_type_map[zone_id] = zone_type
                zone_id += 1
        
        return seeds
    
    def _find_closest_zone(self, x: int, y: int, seeds: Dict[int, Tuple[int, int, ZoneType]], noise_val: float) -> int:
        """Find the closest zone seed to a point, modified by noise."""
        min_distance = float('inf')
        closest_zone_id = 1
        
        for zone_id, (seed_x, seed_y, zone_type) in seeds.items():
            if HAS_NUMPY:
                distance = np.sqrt((x - seed_x)**2 + (y - seed_y)**2)
            else:
                distance = math.sqrt((x - seed_x)**2 + (y - seed_y)**2)
            
            # Modify distance based on zone preferences and noise
            zone_preference = self._get_zone_preference(x, y, zone_type)
            modified_distance = distance * (1 + noise_val * 0.3) * zone_preference
            
            if modified_distance < min_distance:
                min_distance = modified_distance
                closest_zone_id = zone_id
        
        return closest_zone_id
    
    def _get_zone_preference(self, x: int, y: int, zone_type: ZoneType) -> float:
        """Get zone preference multiplier based on location."""
        center_x = self.config.width // 2
        center_y = self.config.height // 2
        if HAS_NUMPY:
            distance_to_center = np.sqrt((x - center_x)**2 + (y - center_y)**2)
            max_distance = np.sqrt(center_x**2 + center_y**2)
        else:
            distance_to_center = math.sqrt((x - center_x)**2 + (y - center_y)**2)
            max_distance = math.sqrt(center_x**2 + center_y**2)
        normalized_distance = distance_to_center / max_distance
        
        preferences = {
            ZoneType.BUSINESS: 0.5 + normalized_distance * 0.8,  # Prefer center
            ZoneType.COMMERCIAL: 0.7 + normalized_distance * 0.6,  # Moderate center preference
            ZoneType.RESIDENTIAL: 1.0,  # No preference
            ZoneType.INDUSTRIAL: 0.8 + normalized_distance * 0.4,  # Slight edge preference
            ZoneType.PARKS: 1.0,  # No preference
            ZoneType.LEISURE: 0.9 + normalized_distance * 0.3,  # Slight center preference
        }
        
        return preferences.get(zone_type, 1.0)
    
    def _create_zone_objects(self, seeds: Dict[int, Tuple[int, int, ZoneType]]):
        """Create zone objects from the grid."""
        processed = set()
        
        for zone_id in seeds.keys():
            if zone_id in processed:
                continue
                
            # Find all connected cells for this zone
            zone_cells = self._find_connected_cells(zone_id)
            if not zone_cells:
                continue
            
            # Calculate bounding box
            min_x = min(x for x, y in zone_cells)
            max_x = max(x for x, y in zone_cells)
            min_y = min(y for x, y in zone_cells)
            max_y = max(y for x, y in zone_cells)
            
            # Create zone object
            zone_type = self.zone_type_map[zone_id]
            density = self.config.zone_densities[zone_type]
            
            zone = Zone(zone_type, min_x, min_y, 
                       max_x - min_x + 1, max_y - min_y + 1, density)
            self.zones.append(zone)
            processed.add(zone_id)
    
    def _find_connected_cells(self, zone_id: int) -> List[Tuple[int, int]]:
        """Find all cells belonging to a zone using flood fill."""
        cells = []
        visited = set()
        
        # Find first occurrence of zone_id
        start_pos = None
        for y in range(self.config.height):
            for x in range(self.config.width):
                if HAS_NUMPY:
                    cell_value = self.zone_grid[y, x]
                else:
                    cell_value = self.zone_grid[y][x]
                    
                if cell_value == zone_id:
                    start_pos = (x, y)
                    break
            if start_pos:
                break
        
        if not start_pos:
            return cells
        
        # Flood fill to find all connected cells
        stack = [start_pos]
        
        while stack:
            x, y = stack.pop()
            if (x, y) in visited:
                continue
                
            if (x < 0 or x >= self.config.width or 
                y < 0 or y >= self.config.height):
                continue
                
            if HAS_NUMPY:
                cell_value = self.zone_grid[y, x]
            else:
                cell_value = self.zone_grid[y][x]
                
            if cell_value != zone_id:
                continue
            
            visited.add((x, y))
            cells.append((x, y))
            
            # Add neighbors
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                stack.append((x + dx, y + dy))
        
        return cells
    
    def get_zone_at(self, x: int, y: int) -> Zone:
        """Get the zone at a specific coordinate."""
        for zone in self.zones:
            if zone.contains_point(x, y):
                return zone
        return None
    
    def get_zones_by_type(self, zone_type: ZoneType) -> List[Zone]:
        """Get all zones of a specific type."""
        return [zone for zone in self.zones if zone.zone_type == zone_type]