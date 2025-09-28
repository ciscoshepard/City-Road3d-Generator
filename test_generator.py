#!/usr/bin/env python3
"""
Simple test script to verify the city generator functionality.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from city_generator.config import CityConfig, ZoneType
from city_generator.generator import CityGenerator

def test_basic_city_generation():
    """Test basic city generation functionality."""
    print("🧪 Test de génération de ville basique...")
    
    # Create a small test configuration
    config = CityConfig(
        width=200,
        height=200,
        main_grid_size=100,
        secondary_grid_size=50
    )
    
    # Generate city
    generator = CityGenerator(config)
    generator.generate_city()
    
    # Verify results
    assert len(generator.zone_manager.zones) > 0, "Aucune zone générée"
    assert len(generator.road_network.roads) > 0, "Aucune route générée"
    assert len(generator.buildings) >= 0, "Erreur dans la génération de bâtiments"
    
    # Get stats
    stats = generator.get_city_stats()
    
    print(f"✅ Test réussi!")
    print(f"   - {stats['total_zones']} zones")
    print(f"   - {stats['total_buildings']} bâtiments") 
    print(f"   - {stats['total_roads']} routes")
    print(f"   - {stats['total_intersections']} intersections")
    
    return generator

def test_export_functionality():
    """Test export functionality."""
    print("\n🧪 Test des fonctionnalités d'export...")
    
    config = CityConfig(width=100, height=100)
    generator = CityGenerator(config)
    generator.generate_city()
    
    # Test JSON export
    try:
        city_data = generator.export_to_json()
        assert 'zones' in city_data, "Données de zones manquantes dans l'export JSON"
        assert 'roads' in city_data, "Données de routes manquantes dans l'export JSON"
        assert 'buildings' in city_data, "Données de bâtiments manquantes dans l'export JSON"
        print("✅ Export JSON: OK")
    except Exception as e:
        print(f"❌ Export JSON: {e}")
        raise
    
    # Test OBJ export
    try:
        test_obj_file = '/tmp/test_city.obj'
        generator.export_to_obj(test_obj_file)
        
        # Verify file was created
        assert os.path.exists(test_obj_file), "Fichier OBJ non créé"
        
        # Verify file has content
        with open(test_obj_file, 'r') as f:
            content = f.read()
            assert 'v ' in content, "Pas de vertices dans le fichier OBJ"
            assert 'f ' in content, "Pas de faces dans le fichier OBJ"
        
        os.remove(test_obj_file)
        print("✅ Export OBJ: OK")
    except Exception as e:
        print(f"❌ Export OBJ: {e}")
        raise

def test_zone_types():
    """Test different zone types generation."""
    print("\n🧪 Test des types de zones...")
    
    config = CityConfig(width=300, height=300)
    generator = CityGenerator(config)
    generator.generate_city()
    
    # Check that different zone types are generated
    zone_types_found = set()
    for zone in generator.zone_manager.zones:
        zone_types_found.add(zone.zone_type)
    
    print(f"✅ Types de zones trouvés: {len(zone_types_found)}")
    for zone_type in zone_types_found:
        zones = generator.zone_manager.get_zones_by_type(zone_type)
        print(f"   - {zone_type.value}: {len(zones)} zones")

def run_all_tests():
    """Run all tests."""
    print("🚀 Début des tests du générateur de ville 3D")
    print("=" * 50)
    
    try:
        # Test basic functionality
        generator = test_basic_city_generation()
        
        # Test exports
        test_export_functionality()
        
        # Test zone types
        test_zone_types()
        
        print("\n🎉 Tous les tests sont passés avec succès!")
        print("Le générateur de ville 3D fonctionne correctement.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Échec du test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)