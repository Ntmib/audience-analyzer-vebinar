"""
JTBD-анализ чата вебинара — День 2.
Выводит данные в JSON для встраивания в HTML-дашборд.
"""

import csv
import re
import json
from pathlib import Path
from collections import Counter, defaultdict

BASE_DIR = Path(__file__).parent.parent
INPUT_FILE = BASE_DIR / "Выгрузка день 2.csv"

MODERATOR_NAMES = ['Модератор Полина', 'Модератор']
MIN_MESSAGE_LENGTH = 15

NOISE_PATTERNS = [
    r'^[\+\!\.\,\?\s]+$',
    r'^[^\w\s]*$',
    r'^\s*$',
    r'^https?://',
    r'aiquiz\.aibasis',
]

GREETING_WORDS = [
    'привет', 'здравствуйте', 'добрый вечер', 'добрый день', 'доброй ночи',
    'здравия', 'всем привет', 'приветствую', 'хай', 'hello', 'hi',
    'пока', 'до свидания', 'до завтра', 'до встречи', 'всем пока',
    'спасибо', 'благодарю', 'спасибо за эфир', 'спасибо большое',
    'класс', 'огонь', 'супер', 'круто', 'ого', 'вау', 'ура',
    'да', 'нет', 'ок', 'хорошо', 'понятно', 'ясно', 'точно',
]

JTBD_CATEGORIES = {
    "ЗАРАБОТАТЬ_ДЕНЬГИ": {
        "keywords": [r'заработ', r'зарабат', r'деньг', r'доход', r'подработ', r'монетиз', r'первые деньги', r'заработок', r'прибыл', r'окупи', r'отбить', r'на жизнь', r'финанс'],
        "job": "Когда я хочу увеличить доход, я хочу освоить вайбкодинг, чтобы получить новый источник заработка",
    },
    "СОЗДАТЬ_ПРОДУКТ": {
        "keywords": [r'создать приложени', r'сделать приложени', r'сделать бот', r'создать бот', r'создать сайт', r'сделать сайт', r'создать лендинг', r'хочу приложени', r'мобильное приложени', r'мини.?приложени', r'калькулятор', r'парсер', r'crm', r'срм', r'репетитор', r'помощник', r'ассистент', r'агент'],
        "job": "Когда у меня есть идея продукта, я хочу создать его без программистов, чтобы запустить быстро и дёшево",
    },
    "НАЙТИ_КЛИЕНТОВ": {
        "keywords": [r'найти клиент', r'привлечь клиент', r'поиск клиент', r'искать клиент', r'где клиент', r'первый клиент', r'первых клиент', r'заявк', r'лид', r'теплых клиент', r'целевых клиент'],
        "job": "Когда я освоил навык, я хочу найти клиентов, чтобы начать зарабатывать",
    },
    "АВТОМАТИЗИРОВАТЬ_БИЗНЕС": {
        "keywords": [r'автоматизир', r'автоматиз', r'автомат', r'упростить', r'рутин', r'экономит.*час', r'освобожд.*врем', r'операционк', r'масштабир'],
        "job": "Когда в моём бизнесе много рутины, я хочу автоматизировать процессы, чтобы освободить время и масштабироваться",
    },
    "СМЕНИТЬ_ПРОФЕССИЮ": {
        "keywords": [r'поменять.*работ', r'поменять.*професси', r'сменить.*професси', r'уйти.*найм', r'уволить', r'ищу себя', r'новый.*путь', r'новую.*професси', r'из дома', r'удалённ', r'удаленн', r'не возвращаться в найм', r'бросить.*работ'],
        "job": "Когда я устал от текущей работы, я хочу освоить новую профессию, чтобы работать удалённо и на себя",
    },
    "ДОВЕСТИ_ДО_ПРОДАКШНА": {
        "keywords": [r'не работает', r'ошибк', r'не выход', r'развернуть', r'деплой', r'deploy', r'хостинг', r'сервер', r'домен', r'перенести', r'размести', r'разместить', r'куда.*сохран', r'как.*запустить', r'за пределами.*студии', r'привязать.*домен'],
        "job": "Когда у меня есть прототип, я хочу довести его до рабочего продукта, чтобы дать клиенту ссылку",
    },
    "НАУЧИТЬСЯ_ПРОДАВАТЬ": {
        "keywords": [r'продавать', r'продаж', r'предлагать.*услуг', r'предложить.*услуг', r'сколько.*брать', r'сколько.*стоит.*разработк', r'ценообразован', r'оплат', r'отказ', r'как.*передать.*клиент', r'договор'],
        "job": "Когда я создал продукт, я хочу научиться его продавать, чтобы получать деньги",
    },
    "РАЗОБРАТЬСЯ_В_ИНСТРУМЕНТАХ": {
        "keywords": [r'что такое.*вайбкод', r'как.*использ', r'как.*войти', r'как.*зайти', r'vpn', r'впн', r'блочит.*регион', r'недоступен', r'как.*работать', r'какой.*инструмент', r'какая.*платформ', r'где.*делать', r'подписк', r'бесплатн', r'google.*ai.*studio', r'гугл.*студи', r'claude', r'клод', r'lovable', r'ловабл'],
        "job": "Когда я хочу начать, я хочу разобраться в инструментах, чтобы понять что использовать и как получить доступ",
    },
    "ПОНЯТЬ_НИШУ": {
        "keywords": [r'не.*пойм.*что.*ближе', r'определить.*сфер', r'определить.*ниш', r'какую.*ниш', r'не.*знаю.*где.*примени', r'чем.*могу.*быть.*полезн', r'что.*можно.*предложить', r'что.*можно.*сделать', r'в.*чём.*разбира'],
        "job": "Когда я хочу начать зарабатывать, но не знаю свою нишу, я хочу определить направление, чтобы не тратить время впустую",
    },
}

PROFESSION_KEYWORDS = {
    "Сетевой маркетинг": [r'сетев', r'млм', r'mlm'],
    "Недвижимость": [r'недвижимост', r'риэлтор', r'риелтор', r'посуточн.*аренд'],
    "Маркетплейсы": [r'маркетплейс', r'вайлдберриз', r'wildberries', r'озон', r'ozon', r'селлер'],
    "Медицина": [r'медиц', r'медсестр', r'врач', r'невролог', r'фармац'],
    "Образование/репетиторы": [r'преподават', r'учитель', r'педагог', r'репетитор', r'тренер'],
    "IT/Digital": [r'smm', r'смм', r'программ', r'дизайн', r'сайт', r'seo', r'разработ'],
    "Строительство/ремонт": [r'строител', r'ремонт', r'монтаж', r'инженер'],
    "Бьюти": [r'бьюти', r'маникюр', r'подолог', r'nail', r'косметолог'],
    "Психология": [r'психолог'],
    "Юриспруденция": [r'юрист', r'юрид', r'банкротств', r'судебн'],
    "Пенсионеры": [r'пенсион'],
    "Общепит/еда": [r'суши', r'ресторан', r'кафе', r'кухн', r'повар'],
    "Копирайтинг/контент": [r'копирайт', r'контент', r'журнал'],
    "Продажи": [r'менеджер.*продаж', r'продавец', r'продавц'],
    "Фриланс": [r'фриланс', r'самозанят'],
    "Бухгалтерия/финансы": [r'бухгалт', r'финанс.*эксперт', r'сметчик'],
    "Логистика/транспорт": [r'логист', r'водител', r'такси', r'перевоз'],
    "Безработные": [r'безработн', r'ищу себя'],
}

PRODUCT_PATTERNS = [
    (r'бот', 'Телеграм-бот / чат-бот'),
    (r'калькулятор', 'Калькулятор'),
    (r'парсер', 'Парсер'),
    (r'мобильн.*приложени', 'Мобильное приложение'),
    (r'приложени', 'Приложение (общее)'),
    (r'сайт|лендинг', 'Сайт / лендинг'),
    (r'crm|срм', 'CRM-система'),
    (r'помощник|ассистент', 'AI-помощник / ассистент'),
    (r'агент', 'AI-агент'),
    (r'магазин|интернет.?магазин', 'Интернет-магазин'),
]

ANXIETY_PATTERNS = {
    "Страх 'не получится'": [r'не получ', r'не смогу', r'не.*умею', r'боюсь', r'не уверен', r'затык', r'самостоятельно.*не', r'не.*понимаю'],
    "Страх продаж / отказов": [r'не.*умею.*предлагать', r'боюсь.*отказ', r'плохо.*переношу', r'не.*умею.*продавать'],
    "Дорого / нет денег": [r'платный', r'сколько.*стоит', r'бесплатн', r'отбивать', r'инвестировать', r'100.*доллар'],
    "Техническая беспомощность": [r'не.*знаю.*как', r'не.*понимаю', r'сложно', r'не.*разбираюсь', r'для.*чайник'],
    "Блокировки РФ": [r'блочит', r'недоступен', r'не.*заходит', r'впн', r'регион'],
}

OUTCOME_PATTERNS = {
    "Первые деньги / конкретная сумма": [r'заработать.*\d', r'хочу.*\d.*руб', r'первые деньги', r'первый.*доход'],
    "Готовый продукт / прототип": [r'готовый.*прототип', r'рабочий.*прототип', r'конкретн.*результат', r'создать.*продукт'],
    "Первые клиенты / заявки": [r'перв.*клиент', r'перв.*заявк', r'перв.*заказ'],
    "Понять свою нишу": [r'определить.*продукт', r'определить.*направлени', r'понять.*что.*хочу', r'определиться'],
    "Автоматизация бизнеса": [r'автоматизир.*свой', r'автоматиз.*бизнес', r'упростить.*работ'],
}


def is_noise(message: str) -> bool:
    msg = message.strip()
    if not msg:
        return True
    for pattern in NOISE_PATTERNS:
        if re.match(pattern, msg, re.IGNORECASE):
            return True
    text_only = re.sub(r'[^\w\s]', '', msg)
    text_only = re.sub(r'\s+', ' ', text_only).strip()
    if len(text_only) < MIN_MESSAGE_LENGTH:
        return True
    msg_lower = msg.lower().strip('!., \n\r\t')
    msg_clean = re.sub(r'[^\w\s]', '', msg_lower).strip()
    for greeting in GREETING_WORDS:
        if msg_clean == greeting or (msg_clean.startswith(greeting) and len(msg_clean) < len(greeting) + 15):
            return True
    return False


def load_messages():
    messages = []
    total_raw = 0
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if len(row) < 5:
                continue
            total_raw += 1
            time_str, sender_id, name, receiver_id, message = row[0], row[1], row[2], row[3], row[4]
            if any(mod.lower() in name.lower() for mod in MODERATOR_NAMES):
                continue
            messages.append({
                'time': time_str,
                'sender_id': sender_id,
                'name': name,
                'message': message.strip(),
            })
    return messages, total_raw


def main():
    all_messages, total_raw = load_messages()

    # Отфильтровываем мусор для анализа
    meaningful = [m for m in all_messages if not is_noise(m['message'])]
    total_messages = len(all_messages)
    unique_people = len(set(m['sender_id'] for m in all_messages))
    meaningful_count = len(meaningful)
    meaningful_people = len(set(m['sender_id'] for m in meaningful))

    result = {
        "stats": {
            "total_raw": total_raw,
            "total_messages": total_messages,
            "meaningful": meaningful_count,
            "unique_people": unique_people,
            "meaningful_people": meaningful_people,
        },
        "jtbd": [],
        "professions": [],
        "products": [],
        "anxieties": [],
        "outcomes": [],
        "quotes": {},
    }

    # JTBD
    jtbd_counter = Counter()
    jtbd_quotes = defaultdict(list)
    jtbd_people = defaultdict(set)
    for msg in meaningful:
        text_lower = msg['message'].lower()
        for cat_name, cat_data in JTBD_CATEGORIES.items():
            for kw in cat_data['keywords']:
                if re.search(kw, text_lower):
                    jtbd_counter[cat_name] += 1
                    jtbd_people[cat_name].add(msg['sender_id'])
                    if len(jtbd_quotes[cat_name]) < 5 and len(msg['message']) > 25:
                        jtbd_quotes[cat_name].append(f"{msg['name']}: «{msg['message'][:180]}»")
                    break

    for cat, count in jtbd_counter.most_common():
        result["jtbd"].append({
            "name": cat.replace('_', ' '),
            "count": count,
            "people": len(jtbd_people[cat]),
            "job": JTBD_CATEGORIES[cat]['job'],
            "quotes": jtbd_quotes[cat],
        })

    # Профессии
    prof_counter = Counter()
    prof_people = defaultdict(set)
    for msg in all_messages:
        text_lower = msg['message'].lower()
        for prof, keywords in PROFESSION_KEYWORDS.items():
            for kw in keywords:
                if re.search(kw, text_lower):
                    prof_counter[prof] += 1
                    prof_people[prof].add(msg['sender_id'])
                    break

    for prof, count in prof_counter.most_common():
        result["professions"].append({
            "name": prof,
            "count": count,
            "people": len(prof_people[prof]),
        })

    # Продукты
    product_counter = Counter()
    product_quotes = defaultdict(list)
    for msg in all_messages:
        text_lower = msg['message'].lower()
        if len(msg['message']) < 15:
            continue
        for pattern, label in PRODUCT_PATTERNS:
            if re.search(pattern, text_lower):
                product_counter[label] += 1
                if len(product_quotes[label]) < 4 and len(msg['message']) > 25:
                    product_quotes[label].append(f"{msg['name']}: «{msg['message'][:150]}»")
                break

    for product, count in product_counter.most_common():
        result["products"].append({
            "name": product,
            "count": count,
            "quotes": product_quotes[product],
        })

    # Тревоги
    anxiety_counter = Counter()
    anxiety_quotes = defaultdict(list)
    for msg in all_messages:
        text_lower = msg['message'].lower()
        if len(msg['message']) < 15:
            continue
        for anx_name, patterns in ANXIETY_PATTERNS.items():
            for p in patterns:
                if re.search(p, text_lower):
                    anxiety_counter[anx_name] += 1
                    if len(anxiety_quotes[anx_name]) < 4 and len(msg['message']) > 25:
                        anxiety_quotes[anx_name].append(f"{msg['name']}: «{msg['message'][:180]}»")
                    break

    for anx, count in anxiety_counter.most_common():
        result["anxieties"].append({
            "name": anx,
            "count": count,
            "quotes": anxiety_quotes[anx],
        })

    # Желаемые результаты
    outcome_counter = Counter()
    outcome_quotes = defaultdict(list)
    for msg in all_messages:
        text_lower = msg['message'].lower()
        if len(msg['message']) < 15:
            continue
        for out_name, patterns in OUTCOME_PATTERNS.items():
            for p in patterns:
                if re.search(p, text_lower):
                    outcome_counter[out_name] += 1
                    if len(outcome_quotes[out_name]) < 4 and len(msg['message']) > 20:
                        outcome_quotes[out_name].append(f"{msg['name']}: «{msg['message'][:180]}»")
                    break

    for out, count in outcome_counter.most_common():
        result["outcomes"].append({
            "name": out,
            "count": count,
            "quotes": outcome_quotes[out],
        })

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
