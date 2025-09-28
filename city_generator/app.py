"""
Web application for the 3D city generator.
"""

import json
import os
import io
import base64

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

from .config import CityConfig, ZoneType
from .generator import CityGenerator

# Check for web dependencies at module level
try:
    from flask import Flask, render_template, request, jsonify, send_file
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from PIL import Image
    HAS_WEB_DEPS = True
    
    app = Flask(__name__)
    current_city = None
    
    @app.route('/')
    def index():
        """Main page with city configuration and visualization."""
        return render_template('index.html')

    @app.route('/api/generate', methods=['POST'])
    def generate_city():
        """API endpoint to generate a new city."""
        global current_city
        
        try:
            data = request.get_json() or {}
            
            # Create configuration from request data
            config = CityConfig(
                width=data.get('width', 1000),
                height=data.get('height', 1000),
                main_road_width=data.get('main_road_width', 20.0),
                secondary_road_width=data.get('secondary_road_width', 12.0),
                local_road_width=data.get('local_road_width', 8.0),
                main_grid_size=data.get('main_grid_size', 200),
                secondary_grid_size=data.get('secondary_grid_size', 100)
            )
            
            # Update zone distributions if provided
            if 'zone_distribution' in data:
                for zone_type_str, percentage in data['zone_distribution'].items():
                    try:
                        zone_type = ZoneType(zone_type_str)
                        config.zone_distribution[zone_type] = percentage / 100.0
                    except ValueError:
                        pass
            
            # Create and generate city
            current_city = CityGenerator(config)
            current_city.generate_city()
            
            # Get city statistics
            stats = current_city.get_city_stats()
            
            return jsonify({
                'success': True,
                'message': 'City generated successfully!',
                'stats': stats
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error generating city: {str(e)}'
            }), 500

    @app.route('/api/export/<format>')
    def export_city(format):
        """Export city in various formats."""
        global current_city
        
        if current_city is None or not current_city.generation_complete:
            return jsonify({'error': 'No city generated'}), 404
        
        try:
            if format == 'json':
                city_data = current_city.export_to_json()
                
                # Create a file-like object
                output = io.StringIO()
                json.dump(city_data, output, indent=2)
                output.seek(0)
                
                return send_file(
                    io.BytesIO(output.getvalue().encode()),
                    mimetype='application/json',
                    as_attachment=True,
                    download_name='city_data.json'
                )
                
            elif format == 'obj':
                # Create temporary OBJ file
                filename = '/tmp/city_model.obj'
                current_city.export_to_obj(filename)
                
                return send_file(
                    filename,
                    mimetype='application/octet-stream',
                    as_attachment=True,
                    download_name='city_model.obj'
                )
                
            else:
                return jsonify({'error': 'Unsupported format'}), 400
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/config')
    def get_default_config():
        """Get default configuration values."""
        config = CityConfig()
        
        return jsonify({
            'width': config.width,
            'height': config.height,
            'main_road_width': config.main_road_width,
            'secondary_road_width': config.secondary_road_width,
            'local_road_width': config.local_road_width,
            'main_grid_size': config.main_grid_size,
            'secondary_grid_size': config.secondary_grid_size,
            'zone_distribution': {
                zone_type.value: int(percentage * 100)
                for zone_type, percentage in config.zone_distribution.items()
            },
            'zone_densities': {
                zone_type.value: density
                for zone_type, density in config.zone_densities.items()
            }
        })
    
except ImportError:
    HAS_WEB_DEPS = False
    app = None

def create_app():
    """Create Flask application."""
    if not HAS_WEB_DEPS:
        raise ImportError("Flask and other web dependencies are required for the web interface. Install them with: pip install flask matplotlib pillow")
    return app

if HAS_WEB_DEPS and __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)