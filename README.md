"""````markdown
name=README.md
# City-Road3d-Generator (MVP) - Enhanced

This update improves tile alignment, adds more tile types, introduces a zoning overlay, and provides a basic chunk streaming manager.

Files added/updated:
- Scripts/TileAlign.gd — helper to align tile pivot and rotation.
- Scripts/LSystem.gd — L-System generator and interpreter (existing updated).
- Scripts/TileGenerator.gd — updated to support L-System and mapping.
- Scripts/ChunkManager.gd — loads/unloads chunks around a player at runtime.
- Scripts/Zoning.gd — simple deterministic zoning per chunk and colored plane overlay.
- Scenes/Tiles/* — added TwoLane, CulDeSac, Roundabout, Sidewalk; updated tiles include Pivot nodes.
- addons/city_generator/ — editor plugin to Generate/Clear in editor.

Quick test (runtime):
1. git fetch origin initial-setup && git checkout initial-setup
2. Open project in Godot 4
3. Create a scene with Node3D root and attach Scripts/TileGenerator.gd
4. Assign tile scenes or configure L-System mapping
5. To test streaming, add ChunkManager.gd to a node and set player_path to your Player node
6. To visualize zones, create a Zoning node and call create_zone_plane(cx,cz) or integrate with ChunkManager

Notes:
- Tiles are placeholders and should be replaced with detailed models and textures.
- Alignments use Pivot nodes; use TileAlign.align_transform to fine-tune placement for imported models.
- Zoning uses a semi-transparent plane per chunk to visualize zone colors.
````"