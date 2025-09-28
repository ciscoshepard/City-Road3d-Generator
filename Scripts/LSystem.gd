extends Node
tool

# Generates an L-System string from an axiom and rules
func generate_lsystem(axiom: String, rules: Dictionary, iterations: int) -> String:
	var result := axiom
	for i in range(iterations):
		var new_result := ""
		for c in result:
			new_result += rules.get(c, str(c))
		result = new_result
	return result

# Interpret the L-System string and place tiles using a mapping of characters to PackedScene
# tokens:
#  F - forward (place straight)
#  C - curve
#  T - T-intersection
#  X - cross intersection
#  + - turn right 90deg
#  - - turn left 90deg
#  [ - push state
#  ] - pop state
func interpret_lsystem(lsys: String, tile_mapping: Dictionary, start_pos: Vector3, tile_size: float, parent: Node) -> Array:
	var placed := []
	var dir_list := [Vector3(0,0,1), Vector3(1,0,0), Vector3(0,0,-1), Vector3(-1,0,0)]
	var dir_idx := 0
	var pos := start_pos
	var stack = []

	for ch in lsys:
		match ch:
			"F":
				if tile_mapping.has("F"):
					var scene := tile_mapping["F"]
					var node := scene.instantiate() as Node3D
					node.position = pos
					node.rotation = Vector3(0, atan2(dir_list[dir_idx].x, dir_list[dir_idx].z), 0)
					parent.add_child(node)
					placed.append(node)
				pos += dir_list[dir_idx] * tile_size
			"C":
				if tile_mapping.has("C"):
					var scene := tile_mapping["C"]
					var node := scene.instantiate() as Node3D
					node.position = pos
					node.rotation = Vector3(0, atan2(dir_list[dir_idx].x, dir_list[dir_idx].z), 0)
					parent.add_child(node)
					placed.append(node)
				pos += dir_list[dir_idx] * tile_size
			"T":
				if tile_mapping.has("T"):
					var scene := tile_mapping["T"]
					var node := scene.instantiate() as Node3D
					node.position = pos
					node.rotation = Vector3(0, atan2(dir_list[dir_idx].x, dir_list[dir_idx].z), 0)
					parent.add_child(node)
					placed.append(node)
				pos += dir_list[dir_idx] * tile_size
			"X":
				if tile_mapping.has("X"):
					var scene := tile_mapping["X"]
					var node := scene.instantiate() as Node3D
					node.position = pos
					node.rotation = Vector3(0, atan2(dir_list[dir_idx].x, dir_list[dir_idx].z), 0)
					parent.add_child(node)
					placed.append(node)
				pos += dir_list[dir_idx] * tile_size
			"+":
				dir_idx = (dir_idx + 1) % 4
			"-":
				dir_idx = (dir_idx - 1 + 4) % 4
			"[":
				stack.append({"pos":pos, "dir_idx":dir_idx})
			"]":
				if stack.size() > 0:
					var s = stack.pop_back()
					pos = s["pos"]
					dir_idx = s["dir_idx"]
				_:
					# ignore unknown symbols
					pass

	return placed
