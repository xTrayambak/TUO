# The Untold Odyssey, a OSS game currently in an alpha stage.

According to a poll conducted, people wanted the game client to be OSS (note: not FOSS, the game will cost around 5-10$).

# Basics
The Untold Odyssey, abbreviated as TUO, is a survival-camping RPG. It combines the aspects of my favorite games like World of Magic (by vetexgames on ROBLOX) and Celeste together with a very cool thing -- camping!
TUO can be played as a singleplayer game, or as multiplayer.
- In TUO, once you spawn into the game, you need to collect resources, build your very first shelter, a measly tent, and then survive the first night. Sleeping does not skip the night, it only fastens the night cycle.
- As you travel across a gigantic map, with a few procedurally generated structures, you can find the clues needed to resent and look back at your forgotten past.


# Technical Jibberish -- Building the game
To build the game into a standalone executable, view this. [https://docs.panda3d.org/1.10/python/distribution/index]
Or, you can use the `deploy.py` script to do so automatically. (Just skip to the options until you get the build prompt)


# Credits -- Contributors
*Programmers:*
xTrayambak - Lead Programmer, Tech Lead, Director, responsible for internal Python logic, some sprite art and a bit of prototype music<br/>
KenzieLucyIcey - Second Lead Programmer, responsible for LUA game logic<br/>
Unreichvelt - Programmer, responsible for C++ logic (I think.)<br/>


*Artists:*
Laz/Viking/Vk - Sprite artist, ideas and motivation</br>
Nat/Arima - Background artist, general image artist, storywriter, ideas and motivation<br/>


*Composers:*
WORMSWORTH</br>
8Azriel8</br>
h_vn</br>


*Thank you list:*

Vardatry/Quack: Funding of the initial prototypes</br>
RDB: Being helpful [https://github.com/rdb] [https://rdb.name]</br>
Entikan: Being helpful</br>
Amitai: Funding of the initial prototypes, motivation and being very nice in general, a really cool dude indeed!</br>


# Credits -- Libraries used
Panda3D, a fast and intuitive game framework (https://github.com/panda3d/panda3d)<br/>
Lupa, a two-way bridge between LUA and Python (https://github.com/scoder/lupa)<br/>
Pyglet, an OpenGL wrapper for Python (https://github.com/pyglet/pyglet)<br/>
OpenDynamicsEngine - an excellent and simple physics/collision for simulating a physical world (https://ode.org)<br/>

# Roadmap -- Current priorities
- A working character controller
- Entities, FSM and pathfinding
- Network protocol
- Accounts ecosystem
- Launcher v2
- More ~~bloat~~ features
- New tiny audio backend to replace OpenAL (in order to get DSP working)
- Compile Nim binaries/DLLs for Michaelsoft Binbows so that those normies can get a framerate higher than 5
- Tweak RenderPipeline more
- Add new effects (motion trail, particles, etc.)


And many many more libraries.. (check requirements.txt for the entire list, since I am too lazy to put everything here)

Happy tweaking!
