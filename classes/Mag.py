from classes.Spell import *
from classes.effects.effects import *


class Mag:
    def __init__(self, id, name, presets=None):
        self.id = id
        self.name = name
        self.hp = 10
        self.reg_hp = 0
        self.effects = {}
        if presets:
            self.presets = presets
        else:
            self.presets = []
        self.last_damage = None

    def deal_damage(self, spell):
        results = {'damage': 0, 'effects': [], 'to_mag': self, 'from_mag': spell.from_mag}
        if 'cold' in spell.with_effects:
            if 'cold' in self.effects:
                spell.damage += self.effects['cold'].power
                results['effects'].append({'add_term_cold': self.effects['cold']})
                self.effects['cold'].add_term()
            else:
                self.effects['cold'] = Cold(spell.from_mag, self)
                results['effects'].append({'add_cold': self.effects['cold']})
        if 'fire' in spell.with_effects:
            if 'fire' in self.effects:
                results['effects'].append({'add_term_fire': self.effects['fire']})
                self.effects['fire'].add_term()
            else:
                self.effects['fire'] = Fire(spell.from_mag, self)
                results['effects'].append({'add_fire': self.effects['fire']})
        results['damage'] = spell.damage
        self.hp -= spell.damage
        self.last_damage = spell.from_mag
        return results

    def cast_spell(self, spell_text):
        is_preset = False
        if spell_text in self.presets:
            self.presets.remove(spell_text)
            is_preset = True
        return compute_spell(spell_text, from_mag=self, to_mag=None, is_preset=is_preset)

    def heals(self, spell):
        results = {'heal': 0, 'effects': [], 'to_mag': self, 'from_mag': spell.from_mag}
        self.hp += spell.heal
        results['heal'] += spell.heal
        return results

    def next_turn(self):
        results = {'damage': 0, 'effects': [], 'to_mag': self.id}
        ef_end_do = []
        for effect in self.effects:
            res = self.effects[effect].do()
            if 'end_cold' in res:
                ef_end_do.append(effect)
            results['effects'].append(res)
        for effect in ef_end_do:
            self.effects[effect].end_do()
        self.hp += self.reg_hp
        return results
