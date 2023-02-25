from src.log import log, warn
from src.client.entity import Entity

class BehaviourStates:
    WANDER = 0
    SLEEP = 1
    CHASE_AGGRESSIVE = 2
    ATTACKING = 3


class Bandit(Entity):
    def __init__(self, *args):
        super().__init__(*args)
        self.state = BehaviourStates.WANDER
