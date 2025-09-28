extends Node
tool

func generate_lsystem(axiom: String, rules: Dictionary, iterations: int) -> String:
	var result := axiom
	for i in range(iterations):
		var new_result := ""
		for c in result:
			new_result += rules.get(c, str(c))
		result = new_result
	return result

func interpret_lsystem(lsys: String) -> Array:
	var instructions := []
	for c in lsys:
		instructions.append(str(c))
	return instructions
