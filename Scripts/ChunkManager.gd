"""extends Node3D

tool

@export var player_path: NodePath
@export var chunk_radius: int = 2        # how many chunks to load around player in each axis
@export var chunk_size: int = 8          # number of tiles per chunk (side length)
@export var tile_size: float = 10.0

onready var player := get_node_or_null(player_path)
var loaded_chunks := {} # Dictionary keyed by Vector2(x,z) -> Array of spawned Nodes

func _physics_process(_delta):
	if not Engine.is_editor_hint():
		if not player:
			return
		var p = player.global_transform.origin
		var cx = int(floor(p.x / (chunk_size * tile_size)))
		var cz = int(floor(p.z / (chunk_size * tile_size)))
		_ensure_chunks(cx, cz)

func _ensure_chunks(cx: int, cz: int) -> void:
	var want = []
	for dx in range(-chunk_radius, chunk_radius+1):
		for dz in range(-chunk_radius, chunk_radius+1):
			want.append(Vector2(cx+dx, cz+dz))

	# unload chunks not wanted
	for key in loaded_chunks.keys():
		if not want.has(key):
			for node in loaded_chunks[key]:
				if is_instance_valid(node):
					node.queue_free()
			loaded_chunks.erase(key)

	# load missing chunks
	for pos in want:
		if not loaded_chunks.has(pos):
			loaded_chunks[pos] = _generate_chunk(pos.x, pos.y)

func _generate_chunk(cx: int, cz: int) -> Array:
	# spawn a simple grid of straight road tiles as placeholder
	var spawned = []
	var base_x = cx * chunk_size * tile_size
	var base_z = cz * chunk_size * tile_size
	var tile_scene = preload("res://Scenes/Tiles/StraightRoad.tscn")
	for x in range(chunk_size):
		for z in range(chunk_size):
			var instance = tile_scene.instantiate() as Node3D
			instance.translation = Vector3(base_x + x * tile_size, 0, base_z + z * tile_size)
			add_child(instance)
			spawned.append(instance)
	return spawned
"""