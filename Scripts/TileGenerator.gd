extends Node3D
tool

@export var tile_scenes: Array[PackedScene] = []
@export var grid_size: int = 8
@export var tile_size: float = 10.0
@export var use_lsystem: bool = false
@export var lsystem_axiom: String = "F"
@export var lsystem_rules: Dictionary = {"F":"F+F-F-F+F"}
@export var lsystem_iterations: int = 2
# mapping: char -> PackedScene (assign in inspector via the resource picker)
@export var tile_mapping: Dictionary = {}

var generated_tiles: Array[Node3D] = []

onready var lsys = preload("res://Scripts/LSystem.gd").new()

func generate_city() -> void:
	clear_city()
	if use_lsystem:
		# validate mapping
		if tile_mapping.empty():
			push_error("tile_mapping is empty — assign mappings for F/C/T/X in the inspector.")
			return
		var lstring := lsys.generate_lsystem(lsystem_axiom, lsystem_rules, lsystem_iterations)
		var placed = lsys.interpret_lsystem(lstring, tile_mapping, Vector3.ZERO, tile_size, self)
		for p in placed:
			generated_tiles.append(p)
		return

	# fallback: simple grid generation
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
	if Engine.is_editor_hint() and not use_lsystem and tile_scenes.empty():
		return "Assign tile scenes in 'tile_scenes' to generate the city or enable L-System mode and configure mapping."
	return ""

func _editor_generate() -> void:
	generate_city()

func _editor_clear() -> void:
	clear_city()