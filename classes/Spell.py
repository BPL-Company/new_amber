class Spell:
    def __init__(self, area, type, with_effects, from_mag, to_mag):
        self.area = area
        self.type = type
        self.with_effects = with_effects
        self.from_mag = from_mag
        self.to_mag = to_mag

    def cast(self, to_mags):
        pass


class DamageSpell(Spell):
    koefs = {'AOE': 0.4, 'target': 1}

    def __init__(self, area, type, damage, with_effects, from_mag, to_mag):
        super().__init__(area, type, with_effects, from_mag, to_mag)
        self.damage = int(damage * self.koefs[area])

    def cast(self, to_mags):
        res = []
        for mag in to_mags:
            res.append(mag.deal_damage(self))
        return res


class HealSpell(Spell):
    koefs = {'AOE': 1, 'target': 2}

    def __init__(self, area, type, heal, with_effects, from_mag, to_mag):
        super().__init__(area, type, with_effects, from_mag, to_mag)
        self.heal = heal*self.koefs[area]

    def cast(self, to_mags):
        res = []
        for mag in to_mags:
            res.append(mag.heals(self))
        return res


words = {
        'cold': {'list': ['мороз', 'холод', 'сосульк', 'снег', 'лед', 'морож'], 'damage': 1},
        'AOE': {'list': ['все', 'област', 'кажд'], 'damage': 0},
        'stone': {'list': ['камен', 'глыб', 'земл'], 'damage': 3},
        'fire': {'list': ['огон', 'пламя', 'огн', 'пламе'], 'damage': 0},
        'heal': {'list': ['хил', 'здоров', 'лекар', 'лечен'], 'heal': 2}
    }


def compute_spell(spell_text, from_mag=None, to_mag=None):
    spell_text = spell_text.lower()
    spell = []
    damage = 0
    heal = 0
    area_type = 'target'
    spell_type = 'damage'
    for type in words:
        for name in words[type]['list']:
            if name in spell_text:
                if type in ['AOE']:
                    area_type = type
                    break
                if type in ['heal']:
                    spell_type = type
                    heal += words[type]['heal']
                    break
                spell.append(type)
                damage += words[type]['damage']
                break
    with_effects = []
    for word in spell:
        if word in words:
            with_effects.append(word)
    if spell_type == 'heal':
        return HealSpell(area_type, spell_type, heal, with_effects, from_mag, to_mag)
    else:
        return DamageSpell(area_type, spell_type, damage, with_effects, from_mag, to_mag)
