"""extends Node3D

tool

# Simple zoning generator per chunk. Colors: Business=red, Commercial=blue, Residential=orange, Park=green
enum Zone {BUSINESS, COMMERCIAL, RESIDENTIAL, PARK}

@export var chunk_size_tiles: int = 8
@export var tile_size: float = 10.0
@export var seed: int = 0

var zone_cache := {} # Vector2(cx,cz) -> Zone

func get_zone(cx: int, cz: int) -> int:
	var key = Vector2(cx, cz)
	if zone_cache.has(key):
		return zone_cache[key]
	# deterministic simple hash
	var h = int( (cx * 73856093) ^ (cz * 19349663) ^ seed )
	var r = abs(h) % 100
	var zone = Zone.RESIDENTIAL
	if r < 15:
		zone = Zone.BUSINESS
	elif r < 40:
		zone = Zone.COMMERCIAL
	elif r < 75:
		zone = Zone.RESIDENTIAL
	else:
		zone = Zone.PARK
	zone_cache[key] = zone
	return zone

func create_zone_plane(cx: int, cz: int) -> Node3D:
	var plane = MeshInstance3D.new()
	var m = PlaneMesh.new()
	m.size = Vector2(chunk_size_tiles * tile_size, chunk_size_tiles * tile_size)
	plane.mesh = m
	var mat = StandardMaterial3D.new()
	match get_zone(cx, cz):
		Zone.BUSINESS:
			mat.albedo_color = Color(1,0.2,0.2)
		Zone.COMMERCIAL:
			mat.albedo_color = Color(0.2,0.4,1)
		Zone.RESIDENTIAL:
			mat.albedo_color = Color(1,0.6,0.2)
		Zone.PARK:
			mat.albedo_color = Color(0.2,0.8,0.2)
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.albedo_color.a = 0.35
	plane.material_override = mat
	plane.rotation = Vector3(-PI/2, 0, 0)
	plane.translation = Vector3(cx * chunk_size_tiles * tile_size + (chunk_size_tiles*tile_size)/2.0, 0.05, cz * chunk_size_tiles * tile_size + (chunk_size_tiles*tile_size)/2.0)
	return plane
"""