"""
JTBD-анализ чата вебинара.
Категоризирует сообщения по Jobs-to-be-Done, считает частоту,
выделяет точные цитаты.
"""

import csv
import re
from pathlib import Path
from collections import Counter, defaultdict

BASE_DIR = Path(__file__).parent.parent
INPUT_FILE = BASE_DIR / "Выгрузка из чата.csv"
OUTPUT_FILE = BASE_DIR / "Материалы" / "JTBD_АНАЛИЗ.md"

# Модераторы
MODERATOR_NAMES = ['Модератор Полина', 'Модератор']

# JTBD категории с ключевыми словами/фразами
JTBD_CATEGORIES = {
    "ЗАРАБОТАТЬ_ДЕНЬГИ": {
        "keywords": [
            r'заработ', r'зарабат', r'деньг', r'доход', r'подработ',
            r'монетиз', r'первые деньги', r'заработок', r'прибыл',
            r'окупи', r'отбить', r'на жизнь', r'финанс',
        ],
        "job": "Когда я хочу увеличить доход, я хочу освоить вайбкодинг, чтобы получить новый источник заработка",
    },
    "СОЗДАТЬ_ПРОДУКТ": {
        "keywords": [
            r'создать приложени', r'сделать приложени', r'сделать бот',
            r'создать бот', r'создать сайт', r'сделать сайт',
            r'создать лендинг', r'хочу приложени', r'мобильное приложени',
            r'мини.?приложени', r'калькулятор', r'парсер', r'crm', r'срм',
            r'репетитор', r'помощник', r'ассистент', r'агент',
        ],
        "job": "Когда у меня есть идея продукта, я хочу создать его без программистов, чтобы запустить быстро и дёшево",
    },
    "НАЙТИ_КЛИЕНТОВ": {
        "keywords": [
            r'найти клиент', r'привлечь клиент', r'поиск клиент',
            r'искать клиент', r'где клиент', r'первый клиент',
            r'первых клиент', r'заявк', r'лид', r'теплых клиент',
            r'целевых клиент',
        ],
        "job": "Когда я освоил навык, я хочу найти клиентов, чтобы начать зарабатывать",
    },
    "АВТОМАТИЗИРОВАТЬ_БИЗНЕС": {
        "keywords": [
            r'автоматизир', r'автоматиз', r'автомат', r'упростить',
            r'рутин', r'экономит.*час', r'освобожд.*врем',
            r'операционк', r'масштабир',
        ],
        "job": "Когда в моём бизнесе много рутины, я хочу автоматизировать процессы, чтобы освободить время и масштабироваться",
    },
    "СМЕНИТЬ_ПРОФЕССИЮ": {
        "keywords": [
            r'поменять.*работ', r'поменять.*професси', r'сменить.*професси',
            r'уйти.*найм', r'уволить', r'ищу себя', r'новый.*путь',
            r'новую.*професси', r'из дома', r'удалённ', r'удаленн',
            r'не возвращаться в найм', r'бросить.*работ',
        ],
        "job": "Когда я устал от текущей работы, я хочу освоить новую профессию, чтобы работать удалённо и на себя",
    },
    "ДОВЕСТИ_ДО_ПРОДАКШНА": {
        "keywords": [
            r'не работает', r'ошибк', r'не выход', r'развернуть',
            r'деплой', r'deploy', r'хостинг', r'сервер', r'домен',
            r'перенести', r'размести', r'разместить', r'куда.*сохран',
            r'как.*запустить', r'код.*в.*продукт', r'за пределами.*студии',
            r'привязать.*домен', r'прикрепить.*домен',
        ],
        "job": "Когда у меня есть прототип, я хочу довести его до рабочего продукта, чтобы дать клиенту ссылку",
    },
    "НАУЧИТЬСЯ_ПРОДАВАТЬ": {
        "keywords": [
            r'продавать', r'продаж', r'предлагать.*услуг',
            r'предложить.*услуг', r'сколько.*брать', r'сколько.*стоит.*разработк',
            r'ценообразован', r'оплат', r'отказ',
            r'как.*передать.*клиент', r'договор',
        ],
        "job": "Когда я создал продукт, я хочу научиться его продавать, чтобы получать деньги",
    },
    "РАЗОБРАТЬСЯ_В_ИНСТРУМЕНТАХ": {
        "keywords": [
            r'что такое.*вайбкод', r'как.*использ', r'как.*войти',
            r'как.*зайти', r'vpn', r'впн', r'блочит.*регион',
            r'недоступен', r'как.*работать', r'какой.*инструмент',
            r'какая.*платформ', r'где.*делать', r'подписк',
            r'бесплатн', r'google.*ai.*studio', r'гугл.*студи',
            r'claude', r'клод', r'lovable', r'ловабл',
        ],
        "job": "Когда я хочу начать, я хочу разобраться в инструментах, чтобы понять что использовать и как получить доступ",
    },
    "ПОНЯТЬ_НИШУ": {
        "keywords": [
            r'не.*пойм.*что.*ближе', r'определить.*сфер',
            r'определить.*ниш', r'какую.*ниш', r'не.*знаю.*где.*примени',
            r'чем.*могу.*быть.*полезн', r'что.*можно.*предложить',
            r'что.*можно.*сделать', r'в.*чём.*разбира',
        ],
        "job": "Когда я хочу начать зарабатывать, но не знаю свою нишу, я хочу определить направление, чтобы не тратить время впустую",
    },
}

# Профессии / ниши для подсчёта
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
    "Фриланс (общий)": [r'фриланс', r'самозанят'],
    "Безработные": [r'безработн', r'ищу себя', r'банкротств.*бизнес'],
    "Логистика/транспорт": [r'логист', r'водител', r'такси', r'перевоз'],
    "Бухгалтерия/финансы": [r'бухгалт', r'финанс.*эксперт', r'сметчик'],
}


def load_messages():
    """Загружает все сообщения из CSV."""
    messages = []
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            if len(row) < 5:
                continue
            time_str, sender_id, name, receiver_id, message = row[0], row[1], row[2], row[3], row[4]
            if any(mod.lower() in name.lower() for mod in MODERATOR_NAMES):
                continue
            if not message.strip():
                continue
            messages.append({
                'time': time_str,
                'sender_id': sender_id,
                'name': name,
                'message': message.strip(),
            })
    return messages


def categorize_message(message_text, categories):
    """Возвращает список категорий, к которым относится сообщение."""
    found = []
    text_lower = message_text.lower()
    for cat_name, cat_data in categories.items():
        for kw in cat_data['keywords']:
            if re.search(kw, text_lower):
                found.append(cat_name)
                break
    return found


def analyze_professions(messages):
    """Анализирует профессии участников."""
    prof_counter = Counter()
    prof_people = defaultdict(set)

    for msg in messages:
        text_lower = msg['message'].lower()
        for prof, keywords in PROFESSION_KEYWORDS.items():
            for kw in keywords:
                if re.search(kw, text_lower):
                    prof_counter[prof] += 1
                    prof_people[prof].add(msg['name'])
                    break

    return prof_counter, prof_people


def analyze_desired_products(messages):
    """Ищет конкретные продукты, которые люди хотят создать."""
    product_patterns = [
        (r'бот', 'Телеграм-бот / чат-бот'),
        (r'калькулятор', 'Калькулятор'),
        (r'парсер', 'Парсер'),
        (r'приложени', 'Приложение (общее)'),
        (r'мобильн.*приложени', 'Мобильное приложение'),
        (r'сайт|лендинг', 'Сайт / лендинг'),
        (r'crm|срм', 'CRM-система'),
        (r'репетитор', 'Репетитор / обучающий инструмент'),
        (r'помощник|ассистент', 'AI-помощник / ассистент'),
        (r'автоответчик', 'Автоответчик'),
        (r'магазин', 'Интернет-магазин'),
        (r'интернет.?магазин', 'Интернет-магазин'),
    ]

    product_counter = Counter()
    product_quotes = defaultdict(list)

    for msg in messages:
        text_lower = msg['message'].lower()
        if len(msg['message']) < 15:
            continue
        for pattern, label in product_patterns:
            if re.search(pattern, text_lower):
                product_counter[label] += 1
                if len(product_quotes[label]) < 5 and len(msg['message']) > 25:
                    product_quotes[label].append(f"{msg['name']}: «{msg['message'][:150]}»")
                break

    return product_counter, product_quotes


def find_switching_triggers(messages):
    """Ищет триггеры переключения — что привело людей на вебинар."""
    trigger_patterns = {
        "Устал от найма / хочу уйти": [
            r'устал', r'надоел', r'ненавиж', r'бросить.*работ',
            r'уйти.*найм', r'не.*возвращ',
        ],
        "Нет денег / маленькая ЗП / пенсия": [
            r'пенси.*не хватает', r'мало.*плат', r'маленьк.*зарплат',
            r'маленьк.*пенси', r'хочу.*добавить', r'дополнительн',
        ],
        "Увидел возможности ИИ": [
            r'заинтересов', r'впервые', r'интересно', r'зацепило',
            r'вдохновля', r'новая.*ниша', r'свежая.*ниша',
        ],
        "Банкротство / потеря бизнеса": [
            r'банкротств', r'потеря', r'закры.*бизнес',
        ],
        "Уже учился у Димы раньше": [
            r'с.*курса', r'с.*лайк.*центр', r'проходил.*обучени',
            r'давно.*знаю', r'уже.*обучал',
        ],
    }

    trigger_counter = Counter()
    trigger_quotes = defaultdict(list)

    for msg in messages:
        text_lower = msg['message'].lower()
        for trigger_name, patterns in trigger_patterns.items():
            for p in patterns:
                if re.search(p, text_lower):
                    trigger_counter[trigger_name] += 1
                    if len(trigger_quotes[trigger_name]) < 3 and len(msg['message']) > 20:
                        trigger_quotes[trigger_name].append(
                            f"{msg['name']}: «{msg['message'][:150]}»"
                        )
                    break

    return trigger_counter, trigger_quotes


def find_anxiety_messages(messages):
    """Ищет тревоги, страхи и возражения."""
    anxiety_patterns = {
        "Страх 'не получится'": [
            r'не получ', r'не смогу', r'не.*умею', r'боюсь',
            r'тараканов.*голов', r'не уверен', r'затык',
            r'самостоятельно.*не', r'не.*понимаю',
        ],
        "Страх продаж / отказов": [
            r'не.*умею.*предлагать', r'боюсь.*отказ', r'плохо.*переношу',
            r'не.*умею.*продавать', r'кажется.*нет.*денег',
        ],
        "Дорого / нет денег на инструменты": [
            r'платный', r'сколько.*стоит', r'бесплатн',
            r'отбивать', r'инвестировать', r'100.*доллар',
        ],
        "Техническая беспомощность": [
            r'не.*знаю.*как', r'не.*понимаю', r'сложно',
            r'не.*разбираюсь', r'для.*чайник',
        ],
        "Блокировки РФ": [
            r'блочит', r'недоступен', r'не.*заходит', r'не.*работает.*vpn',
            r'впн.*не', r'регион',
        ],
    }

    anxiety_counter = Counter()
    anxiety_quotes = defaultdict(list)

    for msg in messages:
        text_lower = msg['message'].lower()
        if len(msg['message']) < 15:
            continue
        for anx_name, patterns in anxiety_patterns.items():
            for p in patterns:
                if re.search(p, text_lower):
                    anxiety_counter[anx_name] += 1
                    if len(anxiety_quotes[anx_name]) < 5 and len(msg['message']) > 25:
                        anxiety_quotes[anx_name].append(
                            f"{msg['name']}: «{msg['message'][:200]}»"
                        )
                    break

    return anxiety_counter, anxiety_quotes


def find_desired_outcomes(messages):
    """Ищет желаемые результаты — что люди хотят получить от практикума."""
    outcome_patterns = {
        "Первые деньги / конкретная сумма": [
            r'заработать.*\d', r'хочу.*\d.*руб', r'хочу.*\d.*тыс',
            r'первые деньги', r'первый.*доход',
        ],
        "Готовый продукт / прототип": [
            r'готовый.*прототип', r'рабочий.*прототип',
            r'конкретное.*решение', r'конкретн.*результат',
            r'одну.*работающую', r'создать.*продукт',
        ],
        "Первые клиенты / заявки": [
            r'перв.*клиент', r'перв.*заявк', r'перв.*заказ',
        ],
        "Понять свою нишу / направление": [
            r'определить.*продукт', r'определить.*направлени',
            r'понять.*что.*хочу', r'определиться',
        ],
        "Автоматизация своего бизнеса": [
            r'автоматизир.*свой', r'автоматиз.*бизнес',
            r'упростить.*работ', r'упростить.*жизн',
        ],
    }

    outcome_counter = Counter()
    outcome_quotes = defaultdict(list)

    for msg in messages:
        text_lower = msg['message'].lower()
        if len(msg['message']) < 15:
            continue
        for out_name, patterns in outcome_patterns.items():
            for p in patterns:
                if re.search(p, text_lower):
                    outcome_counter[out_name] += 1
                    if len(outcome_quotes[out_name]) < 5 and len(msg['message']) > 20:
                        outcome_quotes[out_name].append(
                            f"{msg['name']}: «{msg['message'][:200]}»"
                        )
                    break

    return outcome_counter, outcome_quotes


def main():
    messages = load_messages()
    total_messages = len(messages)
    unique_people = len(set(m['sender_id'] for m in messages))

    print(f"Загружено сообщений (без модератора): {total_messages}")
    print(f"Уникальных участников: {unique_people}")

    # 1. JTBD категоризация
    jtbd_counter = Counter()
    jtbd_quotes = defaultdict(list)
    jtbd_people = defaultdict(set)

    for msg in messages:
        cats = categorize_message(msg['message'], JTBD_CATEGORIES)
        for cat in cats:
            jtbd_counter[cat] += 1
            jtbd_people[cat].add(msg['sender_id'])
            if len(jtbd_quotes[cat]) < 7 and len(msg['message']) > 25:
                jtbd_quotes[cat].append(f"{msg['name']}: «{msg['message'][:200]}»")

    # 2. Профессии
    prof_counter, prof_people = analyze_professions(messages)

    # 3. Желаемые продукты
    product_counter, product_quotes = analyze_desired_products(messages)

    # 4. Триггеры переключения
    trigger_counter, trigger_quotes = find_switching_triggers(messages)

    # 5. Тревоги и страхи
    anxiety_counter, anxiety_quotes = find_anxiety_messages(messages)

    # 6. Желаемые результаты от практикума
    outcome_counter, outcome_quotes = find_desired_outcomes(messages)

    # Генерируем отчёт
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("# JTBD-анализ аудитории вебинара по вайбкодингу\n\n")
        f.write(f"**Всего сообщений (без модератора):** {total_messages}\n")
        f.write(f"**Уникальных участников:** {unique_people}\n\n")
        f.write("---\n\n")

        # JTBD Jobs
        f.write("## 1. JOBS TO BE DONE — рейтинг задач аудитории\n\n")
        f.write("| # | Job | Упоминаний | Уникальных людей |\n")
        f.write("|---|-----|-----------|------------------|\n")
        for i, (cat, count) in enumerate(jtbd_counter.most_common(), 1):
            people_count = len(jtbd_people[cat])
            job_text = JTBD_CATEGORIES[cat]['job']
            f.write(f"| {i} | **{cat.replace('_', ' ')}** | {count} | {people_count} |\n")
        f.write("\n")

        for cat, count in jtbd_counter.most_common():
            job_text = JTBD_CATEGORIES[cat]['job']
            people_count = len(jtbd_people[cat])
            f.write(f"### {cat.replace('_', ' ')}\n\n")
            f.write(f"**Job:** {job_text}\n\n")
            f.write(f"**Упоминаний:** {count} | **Уникальных людей:** {people_count}\n\n")
            f.write("**Цитаты:**\n")
            for q in jtbd_quotes[cat]:
                f.write(f"- {q}\n")
            f.write("\n---\n\n")

        # Профессии
        f.write("## 2. ПРОФЕССИИ И НИШИ АУДИТОРИИ\n\n")
        f.write("| Профессия/ниша | Упоминаний | Уникальных людей |\n")
        f.write("|---------------|-----------|------------------|\n")
        for prof, count in prof_counter.most_common():
            people = len(prof_people[prof])
            f.write(f"| {prof} | {count} | {people} |\n")
        f.write("\n---\n\n")

        # Желаемые продукты
        f.write("## 3. КАКИЕ ПРОДУКТЫ ХОТЯТ СОЗДАТЬ\n\n")
        f.write("| Тип продукта | Упоминаний |\n")
        f.write("|-------------|------------|\n")
        for product, count in product_counter.most_common():
            f.write(f"| {product} | {count} |\n")
        f.write("\n")
        for product, count in product_counter.most_common(5):
            f.write(f"### {product}\n\n")
            for q in product_quotes.get(product, []):
                f.write(f"- {q}\n")
            f.write("\n")
        f.write("---\n\n")

        # Триггеры
        f.write("## 4. ТРИГГЕРЫ ПЕРЕКЛЮЧЕНИЯ — почему пришли\n\n")
        f.write("| Триггер | Упоминаний |\n")
        f.write("|---------|------------|\n")
        for trig, count in trigger_counter.most_common():
            f.write(f"| {trig} | {count} |\n")
        f.write("\n")
        for trig, count in trigger_counter.most_common():
            f.write(f"### {trig}\n\n")
            for q in trigger_quotes.get(trig, []):
                f.write(f"- {q}\n")
            f.write("\n")
        f.write("---\n\n")

        # Тревоги
        f.write("## 5. ТРЕВОГИ И СТРАХИ\n\n")
        f.write("| Страх | Упоминаний |\n")
        f.write("|-------|------------|\n")
        for anx, count in anxiety_counter.most_common():
            f.write(f"| {anx} | {count} |\n")
        f.write("\n")
        for anx, count in anxiety_counter.most_common():
            f.write(f"### {anx}\n\n")
            for q in anxiety_quotes.get(anx, []):
                f.write(f"- {q}\n")
            f.write("\n")
        f.write("---\n\n")

        # Желаемые результаты
        f.write("## 6. ЖЕЛАЕМЫЕ РЕЗУЛЬТАТЫ ОТ ПРАКТИКУМА\n\n")
        f.write("| Результат | Упоминаний |\n")
        f.write("|-----------|------------|\n")
        for out, count in outcome_counter.most_common():
            f.write(f"| {out} | {count} |\n")
        f.write("\n")
        for out, count in outcome_counter.most_common():
            f.write(f"### {out}\n\n")
            for q in outcome_quotes.get(out, []):
                f.write(f"- {q}\n")
            f.write("\n")
        f.write("---\n\n")

        # Рекомендации
        f.write("## 7. РЕКОМЕНДАЦИИ ДЛЯ КОНТЕНТА И ОФФЕРА\n\n")
        f.write("*(генерируется отдельно на основе данных выше)*\n")

    print(f"\nОтчёт сохранён: {OUTPUT_FILE}")
    print("\n=== СВОДКА ===\n")

    print("ТОП-5 JOBS:")
    for cat, count in jtbd_counter.most_common(5):
        people_count = len(jtbd_people[cat])
        print(f"  {cat}: {count} упоминаний / {people_count} людей")

    print("\nТОП-5 ПРОФЕССИЙ:")
    for prof, count in prof_counter.most_common(5):
        print(f"  {prof}: {len(prof_people[prof])} людей")

    print("\nТОП-5 ПРОДУКТОВ:")
    for product, count in product_counter.most_common(5):
        print(f"  {product}: {count}")

    print("\nТОП ТРЕВОГИ:")
    for anx, count in anxiety_counter.most_common():
        print(f"  {anx}: {count}")

    print("\nТОП ЖЕЛАЕМЫЕ РЕЗУЛЬТАТЫ:")
    for out, count in outcome_counter.most_common():
        print(f"  {out}: {count}")


if __name__ == '__main__':
    main()
