from classes.effects.Effect import Effect


class Cold(Effect):
    def __init__(self, from_mag, mag, count_turns=2):
        super().__init__(from_mag, mag)
        self.count_turns_to_end = count_turns
        self.power = 1

    def do(self):
        if self.count_turns_to_end == 1:
            return {'end_cold': self.mag.name}
        self.count_turns_to_end -= 1
        return {}

    def end_do(self):
        self.mag.effects.pop('cold')

    def add_term(self):
        self.count_turns_to_end += 1
        self.power += 1


class Fire(Effect):
    def __init__(self, from_mag, mag, count_turns=2):
        super().__init__(from_mag, mag)
        self.count_turns_to_end = count_turns
        self.power = 1

    def do(self):
        if self.count_turns_to_end == 1:
            return {'end_fire': self.mag.name}
        self.mag.hp -= self.power
        self.count_turns_to_end -= 1
        self.mag.last_damage = self.from_mag
        return {'fire_do': self}

    def end_do(self):
        self.mag.effects.pop('fire')

    def add_term(self):
        self.count_turns_to_end += 1
        self.power += 1