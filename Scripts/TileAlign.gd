"""extends Node

# Helper for computing rotation and pivot offsets for tiles
# Usage: TileAlign.align_transform(tile_node, direction_index, pivot_offset)
# direction_index: 0 = +Z, 1 = +X, 2 = -Z, 3 = -X

func _ready():
	pass

static func dir_from_index(idx: int) -> Vector3:
	match idx % 4:
		0: return Vector3(0, 0, 1)
		1: return Vector3(1, 0, 0)
		2: return Vector3(0, 0, -1)
		3: return Vector3(-1, 0, 0)
	return Vector3(0,0,1)

static func yaw_from_dir_idx(idx: int) -> float:
	# returns Y rotation in radians for given direction index
	match idx % 4:
		0: return 0.0
		1: return -PI/2
		2: return PI
		3: return PI/2
	return 0.0

static func align_transform(node: Node3D, dir_idx: int, pivot_offset: Vector3=Vector3.ZERO) -> void:
	# Align node's transform so pivot_offset in local space sits at node's position
	var yaw = yaw_from_dir_idx(dir_idx)
	var rot = Vector3(0, yaw, 0)
	# Apply rotation to pivot offset
	var rotated_offset = Vector3(
		pivot_offset.x * cos(yaw) - pivot_offset.z * sin(yaw),
		pivot_offset.y,
		pivot_offset.x * sin(yaw) + pivot_offset.z * cos(yaw)
	)
	node.rotation = rot
	node.translation -= rotated_offset
"""