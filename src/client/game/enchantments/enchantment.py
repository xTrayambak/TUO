import random

def int_to_roman_numeral(num: int) -> str:
    """
    Thank you Romans, very cool.
    https://www.w3resource.com/python-exercises/class-exercises/python-class-exercise-1.php
    """
    val = [
            1000, 900, 500, 400,
            100, 90, 50, 40,
            10, 9, 5, 4,
            1
            ]
    syb = [
        "M", "CM", "D", "CD",
        "C", "XC", "L", "XL",
        "X", "IX", "V", "IV",
        "I"
    ]
    roman_num = ''
    i = 0
    while num > 0:
        for _ in range(num // val[i]):
            roman_num += syb[i]
            num -= val[i]
        i += 1
    return roman_num


class Enchantment:
    def __init__(self, enc_id: str, level: int = 1):
        self.enc_id = enc_id
        self.level = level


    def damage_handler(self, source, damage: int | float) -> int | float:
        return damage


    def get_roman_numeral(self) -> str:
        """
        So, what they taught me a billion years ago was worth it? No way!
        """
        return int_to_roman_numeral(self.level)

    def get_decorative_name(self) -> str:
        return f'???? {self.get_roman_numeral()}'
