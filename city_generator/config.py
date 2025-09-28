"""
City configuration class for managing city generation parameters.
"""

from dataclasses import dataclass
from typing import Dict, Tuple
from enum import Enum

class ZoneType(Enum):
    """Zone types available in the city."""
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    BUSINESS = "business"
    LEISURE = "leisure"
    PARKS = "parks"
    INDUSTRIAL = "industrial"

@dataclass
class CityConfig:
    """Configuration class for city generation parameters."""
    
    # City size parameters
    width: int = 1000  # City width in meters
    height: int = 1000  # City height in meters
    
    # Road network parameters
    main_road_width: float = 20.0  # Main road width in meters
    secondary_road_width: float = 12.0  # Secondary road width in meters
    local_road_width: float = 8.0  # Local road width in meters
    
    # Grid parameters
    main_grid_size: int = 200  # Main grid size in meters
    secondary_grid_size: int = 100  # Secondary grid size in meters
    
    # Zone density parameters (0.0 to 1.0)
    zone_densities: Dict[ZoneType, float] = None
    
    # Zone distribution (percentage of city area)
    zone_distribution: Dict[ZoneType, float] = None
    
    # Building parameters
    max_building_height: Dict[ZoneType, int] = None
    min_building_height: Dict[ZoneType, int] = None
    
    # Noise parameters for organic city generation
    noise_scale: float = 0.1
    noise_octaves: int = 4
    
    def __post_init__(self):
        """Initialize default values if not provided."""
        if self.zone_densities is None:
            self.zone_densities = {
                ZoneType.RESIDENTIAL: 0.6,
                ZoneType.COMMERCIAL: 0.8,
                ZoneType.BUSINESS: 0.9,
                ZoneType.LEISURE: 0.4,
                ZoneType.PARKS: 0.1,
                ZoneType.INDUSTRIAL: 0.7
            }
        
        if self.zone_distribution is None:
            self.zone_distribution = {
                ZoneType.RESIDENTIAL: 0.35,
                ZoneType.COMMERCIAL: 0.15,
                ZoneType.BUSINESS: 0.20,
                ZoneType.LEISURE: 0.10,
                ZoneType.PARKS: 0.15,
                ZoneType.INDUSTRIAL: 0.05
            }
        
        if self.max_building_height is None:
            self.max_building_height = {
                ZoneType.RESIDENTIAL: 25,
                ZoneType.COMMERCIAL: 40,
                ZoneType.BUSINESS: 80,
                ZoneType.LEISURE: 15,
                ZoneType.PARKS: 5,
                ZoneType.INDUSTRIAL: 20
            }
        
        if self.min_building_height is None:
            self.min_building_height = {
                ZoneType.RESIDENTIAL: 6,
                ZoneType.COMMERCIAL: 8,
                ZoneType.BUSINESS: 20,
                ZoneType.LEISURE: 3,
                ZoneType.PARKS: 0,
                ZoneType.INDUSTRIAL: 8
            }
    
    def get_zone_color(self, zone_type: ZoneType) -> Tuple[float, float, float]:
        """Get the display color for a zone type."""
        colors = {
            ZoneType.RESIDENTIAL: (0.8, 0.8, 0.6),  # Light brown
            ZoneType.COMMERCIAL: (0.6, 0.6, 0.9),   # Light blue
            ZoneType.BUSINESS: (0.5, 0.5, 0.8),     # Blue
            ZoneType.LEISURE: (0.9, 0.7, 0.6),      # Orange
            ZoneType.PARKS: (0.4, 0.8, 0.4),        # Green
            ZoneType.INDUSTRIAL: (0.7, 0.7, 0.7)    # Gray
        }
        return colors.get(zone_type, (0.5, 0.5, 0.5))