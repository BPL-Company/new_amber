class Effect:
    def __init__(self, from_mag, mag):
        self.mag = mag
        self.from_mag = from_mag

    def do(self):
        pass

    def end_do(self):
        pass