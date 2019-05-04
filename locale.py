r = {
    'target': 'Одиночный',
    'AOE': 'по области',
    'cold': 'Заморозка',
    'stone': 'Камень',
    'fire': 'Огонь',
}


def rus(text):
    try:
        return r[text]
    except KeyError as e:
        return text
