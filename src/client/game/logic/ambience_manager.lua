--[[
  Ambience Manager for the game, rewritten in LUA.
--]]

local GameStates = tuo.getSharedData().GameStates
local Task = tuo.get_task_signals()

local first_runtime_cycle = true

local songs_ingame_overworld =
	{ "assets/music/gone.mp3", "assets/music/harbinger_of_joy.mp3", "assets/music/sonata.flac" }
local songs_ingame_hell = {}
local songs_ingame_void = { "assets/music/mist001.flac", "assets/music/mist002.flac" }

mood = 0

local songs_menu = { "assets/music/unlighted.mp3", "assets/music/white_phantom.mp3" }

function ambience_task()
	mood = mood + 1
	if tuo.get_volume_master() == 0 then
		-- Don't waste resources loading songs for nothing.
		return Task.cont
	end

	if first_runtime_cycle == true then
		first_runtime_cycle = false
		return Task.pause(random.randint(10, 25))
	end

	if tuo.get_state() == GameStates.MENU then
		local audio = audio_loader.load(random.choice(songs_menu))
		audio.play()

		free(audio)

		return Task.pause(random.randint(128, 128 + audio.get_length_int()))
	end

	if tuo.get_state() == GameStates.INGAME then
		local audio = audio_loader.load(random.choice(songs_ingame_overworld))
		audio.play()

		return Task.pause(random.randint(256, 256 + audio.get_length_int()))
	end

	if mood == 32768 then
		mood = 0
		-- Add spooky sounds here later on
	end

	return tuo.get_task_signals().cont
end

function main()
	tuo.new_task("ambience", ambience_task, true)
end

main()
