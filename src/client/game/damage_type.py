from enum import Enum

class DamageType(Enum):
    # Common
    NO_REASON = 0
    FALL = 1
    BURN = 2

damage_type_to_transtring = {
    DamageType.NO_REASON: 'entity.death.default',
    DamageType.FALL: 'entity.death.fall',
    DamageType.BURN: 'entity.death.burn'
}
