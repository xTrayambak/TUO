class Event:
    def __init__(self, name: str):
        self.name: str = name
        self.subscribers: list[callable] = []


    def subscribe(self, fn):
        self.subscribers.append(fn)


    def unsubscribe(self, fn):
        self.subscribers.remove(fn)


    def fire(self, args: list = None):
        for subscriber in self.subscribers:
            if args:
                subscriber(*args)
            else:
                subscriber()
