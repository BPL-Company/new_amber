class TurnResult:
    type_damage = {'stone': '🔻', 'cold': '🔹', 'fire': '🔸'}
    mess = {'fire': {'end': '{} перестал гореть\n', 'add': '{} горит!\n', 'add_term': '{} горит!\n', 'fire_do': '{} горит!\n'},
            'cold': {'end': '{} вышел из заморозки\n', 'add': '{} заморожнен!\n', 'add_term': '{} заморожен!\n'}}

    def __init__(self, results):
        print(results)
        self.is_draw = False
        self.who_win = None
        self.spell_is_success = True
        self.who_cast_in_this_turn = None
        self.mags = {}
        self.ded = []
        for ress in results:
            try:
                self.mags[ress['to_mag']] = {'damage': {}, 'heal': {}, 'effects': {}}
            except:
                pass
        for ress in results:
            if 'dead' in ress:
                self.ded.append(ress)
                continue
            if 'win' in ress:
                self.who_win = ress['win']
                continue
            if 'draw' in ress:
                self.is_draw = True
                continue
            if 'success' in ress:
                if not ress['success']:
                    self.spell_is_success = False
                else:
                    self.spell_is_success = True
                self.who_cast_in_this_turn = ress['to_mag']
                continue
            if 'heal' in ress:
                self.mags[ress['to_mag']]['heal'] = {'value': ress['heal'], 'from': ress['from_mag']}
            if 'damage' in ress:
                self.mags[ress['to_mag']]['damage'] = ress['damage']
            for effect in ress['effects']:
                if 'add_cold' in effect:
                    cold = effect['add_cold']
                    self.mags[cold.mag]['effects']['cold'] = {'action': 'add', 'effect': cold}
                if 'add_term_cold' in effect:
                    cold = effect['add_term_cold']
                    self.mags[cold.mag]['effects']['cold'] = {'action': 'add_term', 'effect': cold}
                if 'end_cold' in effect:
                    self.mags[effect['end_cold']]['effects']['cold'] = {'action': 'end'}
                if 'add_fire' in effect:
                    fire = effect['add_fire']
                    self.mags[fire.mag]['effects']['fire'] = {'action': 'add', 'effect': fire}
                if 'add_term_fire' in effect:
                    fire = effect['add_term_fire']
                    self.mags[fire.mag]['effects']['fire'] = {'action': 'add_term', 'effect': fire}
                if 'end_fire' in effect:
                    self.mags[effect['end_fire']]['effects']['fire'] = {'action': 'end'}
                if 'fire_do' in effect:
                    fire = effect['fire_do']
                    self.mags[fire.mag]['effects']['fire'] = {'action': 'fire_do', 'effect': fire}
                    self.mags[fire.mag]['damage']['fire'] += fire.power

    def to_rus(self):
        text = ''
        if not self.spell_is_success:
            text += 'У {} не получилось наколдовать свое заклинание!\n'.format(self.who_cast_in_this_turn.name)
        for mag in self.mags:
            res = self.mags[mag]
            text_dmg = None
            for type_damage in res['damage']:
                if res['damage'][type_damage] != 0:
                    if not text_dmg:
                        text_dmg = '{} получил '.format(mag.name)
                    text_dmg += '{}{}+'.format(res['damage'][type_damage], self.type_damage[type_damage])
            if text_dmg:
                text += text_dmg + '={}♥️ урона!\n'.format(sum([damage for damage in res['damage'].values()]))
            if res['heal']:
                if res['heal']['from'] is mag:
                    text += '{} выхилился на {}♥️!\n'.format(res['heal']['from'].name, res['heal']['value'])
                else:
                    text += '{} выхилил {} на {}♥️!\n'.format(res['heal']['from'].name, mag.name, res['heal']['value'])
            text = del_last_plus(text)
        for res in self.ded:
            text += '{} умер от {}!\n'.format(res['dead'].name, res['from'].name)
        text_ef = '\nЭффекты:\n'
        for mag in self.mags:
            res = self.mags[mag]
            for effect in res['effects']:
                text_ef += self.mess[effect][res['effects'][effect]['action']].format(mag.name)
        if text_ef != '\nЭффекты:\n':
            text += text_ef
        if self.is_draw:
            text += 'Ничья!'
        if self.who_win:
            text += '\n*{}* выиграл!'.format(self.who_win.name)
        return text


def del_last_plus(text):
    return ''.join(list(reversed((''.join(list(reversed(text))).replace('+', '', 1)))))
