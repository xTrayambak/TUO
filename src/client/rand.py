import datetime as dt

class LCG:
    def __init__(self, seed: int):
        self.seed: int = seed
        self.__sample: int = 6364136223846793005


    def sample(self, minimum: int, maximum: int) -> int:
        time_factor: int = dt.datetime.today().hour + dt.datetime.today().day + dt.datetime.today().month - dt.datetime.today().minute + dt.datetime.today().microsecond
        return ((self.seed+time_factor) * self.__sample)
