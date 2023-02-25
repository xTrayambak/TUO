local GameStates = tuo.getSharedData().GameStates
local map_is_loaded = false
local SCALING_FACTOR = 2

function main()
	local map = Object(tuo, "assets/models/map.obj")
	map.set_hpr(Vector3(0, 90, 90))
end

main()
