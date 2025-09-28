"""
Main entry point for the City Road 3D Generator.
"""

import argparse
import sys
import os
from .config import CityConfig, ZoneType
from .generator import CityGenerator
from .app import create_app

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description="Générateur 3D de réseau routier de ville",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  %(prog)s --web                    # Lance l'interface web
  %(prog)s --cli --width 2000       # Génère une ville 2000x2000 en CLI
  %(prog)s --cli --export city.obj  # Génère et exporte en OBJ
        """
    )
    
    parser.add_argument('--web', action='store_true', 
                       help='Lancer l\'interface web (par défaut)')
    parser.add_argument('--cli', action='store_true', 
                       help='Mode ligne de commande')
    
    # City parameters
    parser.add_argument('--width', type=int, default=1000,
                       help='Largeur de la ville en mètres (défaut: 1000)')
    parser.add_argument('--height', type=int, default=1000,
                       help='Hauteur de la ville en mètres (défaut: 1000)')
    parser.add_argument('--main-road-width', type=float, default=20.0,
                       help='Largeur des routes principales (défaut: 20.0)')
    parser.add_argument('--secondary-road-width', type=float, default=12.0,
                       help='Largeur des routes secondaires (défaut: 12.0)')
    parser.add_argument('--local-road-width', type=float, default=8.0,
                       help='Largeur des routes locales (défaut: 8.0)')
    
    # Zone distribution
    parser.add_argument('--residential', type=float, default=0.35,
                       help='Pourcentage de zones résidentielles (défaut: 0.35)')
    parser.add_argument('--commercial', type=float, default=0.15,
                       help='Pourcentage de zones commerciales (défaut: 0.15)')
    parser.add_argument('--business', type=float, default=0.20,
                       help='Pourcentage de zones business (défaut: 0.20)')
    parser.add_argument('--leisure', type=float, default=0.10,
                       help='Pourcentage de zones de loisirs (défaut: 0.10)')
    parser.add_argument('--parks', type=float, default=0.15,
                       help='Pourcentage de parcs (défaut: 0.15)')
    parser.add_argument('--industrial', type=float, default=0.05,
                       help='Pourcentage de zones industrielles (défaut: 0.05)')
    
    # Export options
    parser.add_argument('--export', type=str,
                       help='Exporter vers un fichier (format déterminé par l\'extension: .json, .obj)')
    parser.add_argument('--preview', type=str,
                       help='Sauvegarder un aperçu 2D vers un fichier image')
    
    # Web server options
    parser.add_argument('--host', type=str, default='0.0.0.0',
                       help='Adresse IP pour le serveur web (défaut: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000,
                       help='Port pour le serveur web (défaut: 5000)')
    parser.add_argument('--debug', action='store_true',
                       help='Mode debug pour le serveur web')
    
    args = parser.parse_args()
    
    # If no mode specified, default to web
    if not args.cli:
        args.web = True
    
    try:
        if args.web:
            run_web_app(args)
        else:
            run_cli_app(args)
    except KeyboardInterrupt:
        print("\nInterrompu par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        print(f"Erreur: {e}")
        sys.exit(1)

def run_web_app(args):
    """Run the web application."""
    try:
        from .app import create_app
        print(f"🌐 Démarrage du serveur web sur http://{args.host}:{args.port}")
        print("Appuyez sur Ctrl+C pour arrêter le serveur")
        
        app = create_app()
        app.run(host=args.host, port=args.port, debug=args.debug)
    except ImportError as e:
        print(f"❌ Erreur: {e}")
        print("Pour utiliser l'interface web, installez les dépendances:")
        print("pip install flask matplotlib pillow")
        sys.exit(1)

def run_cli_app(args):
    """Run the command-line application."""
    print("🏙️  Générateur 3D de Ville - Mode CLI")
    print("=" * 50)
    
    # Validate zone distribution
    total_zones = (args.residential + args.commercial + args.business + 
                  args.leisure + args.parks + args.industrial)
    
    if abs(total_zones - 1.0) > 0.01:
        print(f"⚠️  Attention: La distribution des zones ne fait pas 100% ({total_zones:.1%})")
        print("   Les valeurs seront normalisées automatiquement.")
        
        # Normalize values
        args.residential /= total_zones
        args.commercial /= total_zones
        args.business /= total_zones
        args.leisure /= total_zones
        args.parks /= total_zones
        args.industrial /= total_zones
    
    # Create configuration
    config = CityConfig(
        width=args.width,
        height=args.height,
        main_road_width=args.main_road_width,
        secondary_road_width=args.secondary_road_width,
        local_road_width=args.local_road_width
    )
    
    # Update zone distribution
    config.zone_distribution = {
        ZoneType.RESIDENTIAL: args.residential,
        ZoneType.COMMERCIAL: args.commercial,
        ZoneType.BUSINESS: args.business,
        ZoneType.LEISURE: args.leisure,
        ZoneType.PARKS: args.parks,
        ZoneType.INDUSTRIAL: args.industrial
    }
    
    print(f"📏 Dimensions: {args.width}x{args.height} mètres")
    print(f"🛣️  Routes: Principales {args.main_road_width}m, " +
          f"Secondaires {args.secondary_road_width}m, " +
          f"Locales {args.local_road_width}m")
    print("\n📊 Distribution des zones:")
    for zone_type, percentage in config.zone_distribution.items():
        print(f"   {get_zone_icon(zone_type)} {zone_type.value.title()}: {percentage:.1%}")
    
    print("\n🚀 Génération de la ville...")
    
    # Generate city
    generator = CityGenerator(config)
    generator.generate_city()
    
    # Display statistics
    stats = generator.get_city_stats()
    print("\n✅ Génération terminée!")
    print(f"   🏙️  {stats['total_zones']} zones générées")
    print(f"   🏢 {stats['total_buildings']} bâtiments créés")
    print(f"   🛣️  {stats['total_roads']} routes tracées")
    print(f"   ⚡ {stats['total_intersections']} intersections")
    
    # Detailed zone statistics
    print("\n📈 Détails par zone:")
    for zone_type_str, zone_stats in stats['zone_stats'].items():
        zone_type = ZoneType(zone_type_str)
        icon = get_zone_icon(zone_type)
        print(f"   {icon} {zone_type.value.title()}: " +
              f"{zone_stats['zones']} zones, {zone_stats['buildings']} bâtiments, " +
              f"hauteur moy. {zone_stats['avg_building_height']:.1f}m")
    
    # Export if requested
    if args.export:
        export_file(generator, args.export)
    
    # Generate preview if requested
    if args.preview:
        generate_preview(generator, args.preview)
    
    print("\n🎉 Terminé!")

def export_file(generator, filename):
    """Export city to file."""
    print(f"\n💾 Export vers {filename}...")
    
    try:
        _, ext = os.path.splitext(filename.lower())
        
        if ext == '.json':
            generator.export_to_json(filename)
            print(f"✅ Export JSON réussi: {filename}")
            
        elif ext == '.obj':
            generator.export_to_obj(filename)
            print(f"✅ Export OBJ réussi: {filename}")
            
        else:
            print(f"❌ Format non supporté: {ext}")
            print("   Formats supportés: .json, .obj")
            
    except Exception as e:
        print(f"❌ Erreur lors de l'export: {e}")

def generate_preview(generator, filename):
    """Generate 2D preview image."""
    print(f"\n🖼️  Génération de l'aperçu vers {filename}...")
    
    try:
        import matplotlib.pyplot as plt
        
        # Create figure
        fig, ax = plt.subplots(1, 1, figsize=(12, 12))
        ax.set_xlim(0, generator.config.width)
        ax.set_ylim(0, generator.config.height)
        ax.set_aspect('equal')
        
        # Draw zones
        for zone in generator.zone_manager.zones:
            color = generator.config.get_zone_color(zone.zone_type)
            rect = plt.Rectangle((zone.x, zone.y), zone.width, zone.height,
                               facecolor=color, alpha=0.6, edgecolor='black', linewidth=0.5)
            ax.add_patch(rect)
        
        # Draw roads
        for road in generator.road_network.roads:
            if road.road_type == 'main':
                color = 'black'
                width = 3
            elif road.road_type == 'secondary':
                color = 'gray'
                width = 2
            else:
                color = 'lightgray'
                width = 1
            
            ax.plot([road.start[0], road.end[0]], [road.start[1], road.end[1]], 
                   color=color, linewidth=width)
        
        # Draw buildings
        for building in generator.buildings:
            height_ratio = building.building_height / 100
            color_intensity = min(1.0, 0.3 + height_ratio * 0.7)
            
            rect = plt.Rectangle((building.x, building.y), building.width, building.height,
                               facecolor='brown', alpha=color_intensity, 
                               edgecolor='darkbrown', linewidth=0.3)
            ax.add_patch(rect)
        
        ax.set_title(f'Ville Générée ({generator.config.width}x{generator.config.height}m)')
        ax.set_xlabel('X (mètres)')
        ax.set_ylabel('Y (mètres)')
        
        # Add legend
        legend_elements = []
        for zone_type in ZoneType:
            zones = generator.zone_manager.get_zones_by_type(zone_type)
            if zones:
                color = generator.config.get_zone_color(zone_type)
                legend_elements.append(plt.Rectangle((0, 0), 1, 1, facecolor=color, 
                                                   alpha=0.6, label=zone_type.value.title()))
        
        if legend_elements:
            ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.15, 1))
        
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Aperçu sauvegardé: {filename}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération de l'aperçu: {e}")

def get_zone_icon(zone_type):
    """Get emoji icon for zone type."""
    icons = {
        ZoneType.RESIDENTIAL: '🏠',
        ZoneType.COMMERCIAL: '🏪',
        ZoneType.BUSINESS: '🏢',
        ZoneType.LEISURE: '🎪',
        ZoneType.PARKS: '🌳',
        ZoneType.INDUSTRIAL: '🏭'
    }
    return icons.get(zone_type, '🏙️')

if __name__ == '__main__':
    main()