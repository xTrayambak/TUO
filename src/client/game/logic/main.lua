--[[ main.lua
--  @description Loads up all the LUA game logic
--  @author xTrayambak
--  @encoding utf-8
--]]

tuo.log("Loading LUA game logic.", "Worker/main.lua")

require("src.client.game.logic.ambience_manager")
require("src.client.game.logic.coordinates_screen")
require("src.client.game.logic.ingame_hud")
require("src.client.game.logic.map_loader")
