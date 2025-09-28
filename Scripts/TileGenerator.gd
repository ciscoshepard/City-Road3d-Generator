extends Node3D
tool

@export var tile_scenes: Array[PackedScene] = []
@export var grid_size: int = 8
@export var tile_size: float = 10.0
var generated_tiles: Array[Node3D] = []

func generate_city() -> void:
	clear_city()
	if tile_scenes.empty():
		push_error("tile_scenes is empty — assignez au moins une scène de tuile dans l'inspecteur.")
		return
	for x in range(-grid_size, grid_size):
		for z in range(-grid_size, grid_size):
			var packed := tile_scenes[randi() % tile_scenes.size()]
			if packed == null:
				continue
			var tile := packed.instantiate() as Node3D
			tile.position = Vector3(x * tile_size, 0.0, z * tile_size)
			add_child(tile)
			generated_tiles.append(tile)

func clear_city() -> void:
	for t in generated_tiles:
		if is_instance_valid(t):
			t.queue_free()
		generated_tiles.clear()

func _get_configuration_warning() -> String:
	if Engine.is_editor_hint() and tile_scenes.empty():
		return "Assign tile scenes in 'tile_scenes' to generate the city."
	return ""

func _editor_generate() -> void:
	generate_city()

func _editor_clear() -> void:
	clear_city()
