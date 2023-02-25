"""
The NPC AI/thinker class.
My main goal is to stay faithful to the TUO ROBLOX game's AI behaviour, since it was pretty cool.

They have noggins now!
"""

from direct.fsm.FSM import FSM, FSMException

class Thinker:
    def __init__(self, instance):
        self.instance = instance
