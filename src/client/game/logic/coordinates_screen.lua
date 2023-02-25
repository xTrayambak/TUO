local coords = nil
local font = tuo.font_loader.load("gentium_basic")

function load_coordinates_screen()
	tuo.log("Loading coordinates screen", "Worker/CoordinatesScreen")
	coords = TextLabel(tuo, font, "XYZ: NaN / NaN / NaN", 0.1)
end

function round(num, numDecimalPlaces)
	local mult = 10 ^ (numDecimalPlaces or 0)
	return math.floor(num * mult + 0.5) / mult
end

function coords_update()
	if tuo.get_state() == tuo.get_shared_data().GameStates.INGAME then
		coords.show()
	else
		coords.hide()
	end

	local player_pos = tuo.player.get_pos()
	coords.set_text(
		"XYZ: " .. round(player_pos.x, 1) .. " / " .. round(player_pos.y, 1) .. " / " .. round(player_pos.z, 1)
	)
	return tuo.get_task_signals().cont
end

function main()
	load_coordinates_screen()
	tuo.new_task("coords_update", coords_update)
end

main()
