tool
extends EditorPlugin

var panel : VBoxContainer

func _enter_tree() -> void:
	panel = VBoxContainer.new()
	panel.name = "City Generator"
	var gen_btn = Button.new()
	gen_btn.text = "Generate City"
	gen_btn.tooltip = "Génère la ville dans la scène actuelle (appelle generate_city() sur le root)"
	gen_btn.connect("pressed", Callable(self, "_on_generate_pressed"))
	panel.add_child(gen_btn)
	var clear_btn = Button.new()
	clear_btn.text = "Clear City"
	clear_btn.tooltip = "Efface la ville générée (appelle clear_city() sur le root)"
	clear_btn.connect("pressed", Callable(self, "_on_clear_pressed"))
	panel.add_child(clear_btn)
	add_control_to_dock(DOCK_SLOT_RIGHT_UL, panel)

func _exit_tree() -> void:
	if panel:
		remove_control_from_docks(panel)
		panel.free()
		panel = null

func _on_generate_pressed() -> void:
	var root = get_editor_interface().get_edited_scene_root()
	if root and root.has_method("generate_city"):
		root.call("generate_city")
	else:
		EditorInterface.get_singleton().show_warning("Root node does not expose generate_city(). Add TileGenerator.gd to the scene root.")

func _on_clear_pressed() -> void:
	var root = get_editor_interface().get_edited_scene_root()
	if root and root.has_method("clear_city"):
		root.call("clear_city")
	else:
		EditorInterface.get_singleton().show_warning("Root node does not expose clear_city(). Add TileGenerator.gd to the scene root.")
