from classes.Mag import Mag
import random


class Battle:
    def __init__(self, players):
        self.mags = {player['id']: Mag(player['id'], player['name'], player['presets']) for player in players}
        self.order = list(self.mags.keys())
        self.status = 'wait'
        self.now_mag = 0

    def add_player(self, player):
        if player['id'] in self.mags:
            return False
        self.mags[player['id']] = Mag(player['id'], player['name'], player['presets'])
        self.order.append(player['id'])
        return True

    def start(self):
        self.status = 'start'
        return self.order[self.now_mag], self.mags[self.order[self.now_mag]].name

    def cast(self, this_mag, spell):
        if self.order[self.now_mag] != this_mag:
            return False, False
        this_mag = self.mags[this_mag]
        spell = this_mag.cast_spell(spell)
        results = []
        mags = []
        if spell.area == 'AOE':
            for player in self.mags.values():
                mags.append(player)
        else:
            if spell.type == 'heal':
                mags.append(this_mag)
            else:
                while True:
                    player = random.choice(list(self.mags.values()))
                    if player.id != this_mag.id:
                        mags.append(player)
                        break
        res = spell.cast(mags)
        results += res
        results.append(this_mag.next_turn())
        pops = []
        for mag in self.mags.values():
            if mag.hp <= 0:
                results.append({'dead': mag, 'from': mag.last_damage})
                pops.append(mag.id)
                print(mag.id)
                self.order.remove(mag.id)
        for mag in pops:
            self.mags.pop(mag)
        self.now_mag += 1
        if self.now_mag >= len(self.mags):
            self.now_mag = 0
        if len(self.mags) == 1:
            results.append({'win': self.mags.popitem()[1]})
            return results, False
        if len(self.mags) == 0:
            results.append({'draw': True})
            return results, False
        return results, self.mags[self.order[self.now_mag]]