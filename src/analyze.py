"""
JTBD analyzer module.
Categorizes messages by jobs, professions, products, anxieties.
Generates audience portraits and offer recommendations.
"""

import json
import re
from pathlib import Path
from collections import Counter, defaultdict


CONFIG_DIR = Path(__file__).parent.parent / 'config'


def _load_json(filename: str) -> dict | list:
    with open(CONFIG_DIR / filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def _match_categories(text_lower: str, categories: dict) -> list[str]:
    """Return list of category names matching the text."""
    found = []
    for cat_name, cat_data in categories.items():
        keywords = cat_data['keywords'] if isinstance(cat_data, dict) else cat_data
        for kw in keywords:
            if re.search(kw, text_lower):
                found.append(cat_name)
                break
    return found


def _analyze_jtbd(messages: list[dict], jtbd_config: dict) -> list[dict]:
    """Analyze JTBD categories from messages."""
    counter = Counter()
    quotes: dict[str, list[str]] = defaultdict(list)
    people: dict[str, set] = defaultdict(set)

    for msg in messages:
        text_lower = msg['message'].lower()
        for cat_name, cat_data in jtbd_config.items():
            for kw in cat_data['keywords']:
                if re.search(kw, text_lower):
                    counter[cat_name] += 1
                    people[cat_name].add(msg['sender_id'])
                    if len(quotes[cat_name]) < 5 and len(msg['message']) > 25:
                        quotes[cat_name].append(
                            f"{msg['name']}: \u00ab{msg['message'][:180]}\u00bb"
                        )
                    break

    result = []
    for cat, count in counter.most_common():
        result.append({
            'name': cat.replace('_', ' '),
            'key': cat,
            'count': count,
            'people': len(people[cat]),
            'job': jtbd_config[cat]['job'],
            'quotes': quotes[cat],
        })
    return result


def _analyze_professions(messages: list[dict], prof_config: dict) -> list[dict]:
    """Analyze profession/niche mentions."""
    counter = Counter()
    people: dict[str, set] = defaultdict(set)

    for msg in messages:
        text_lower = msg['message'].lower()
        for prof, keywords in prof_config.items():
            for kw in keywords:
                if re.search(kw, text_lower):
                    counter[prof] += 1
                    people[prof].add(msg['sender_id'])
                    break

    return [
        {'name': prof, 'count': count, 'people': len(people[prof])}
        for prof, count in counter.most_common()
    ]


def _analyze_products(messages: list[dict], product_config: list[dict]) -> list[dict]:
    """Analyze desired product types."""
    counter = Counter()
    quotes: dict[str, list[str]] = defaultdict(list)

    for msg in messages:
        text_lower = msg['message'].lower()
        if len(msg['message']) < 15:
            continue
        for item in product_config:
            if re.search(item['pattern'], text_lower):
                label = item['label']
                counter[label] += 1
                if len(quotes[label]) < 4 and len(msg['message']) > 25:
                    quotes[label].append(
                        f"{msg['name']}: \u00ab{msg['message'][:150]}\u00bb"
                    )
                break

    return [
        {'name': prod, 'count': count, 'quotes': quotes.get(prod, [])}
        for prod, count in counter.most_common()
    ]


def _analyze_anxieties(messages: list[dict], anx_config: dict) -> list[dict]:
    """Analyze fears and anxieties."""
    counter = Counter()
    quotes: dict[str, list[str]] = defaultdict(list)

    for msg in messages:
        text_lower = msg['message'].lower()
        if len(msg['message']) < 15:
            continue
        for anx_name, patterns in anx_config.items():
            for p in patterns:
                if re.search(p, text_lower):
                    counter[anx_name] += 1
                    if len(quotes[anx_name]) < 5 and len(msg['message']) > 25:
                        quotes[anx_name].append(
                            f"{msg['name']}: \u00ab{msg['message'][:180]}\u00bb"
                        )
                    break

    return [
        {'name': anx, 'count': count, 'quotes': quotes.get(anx, [])}
        for anx, count in counter.most_common()
    ]


def _generate_portraits(
    jtbd_results: list[dict],
    prof_results: list[dict],
    anx_results: list[dict],
    total_people: int,
) -> list[dict]:
    """Generate 3 audience portraits by clustering top jobs + professions."""
    # Portrait 1: Creators — want to build and earn
    # Portrait 2: Business owners — want to automate
    # Portrait 3: Career changers — want a new life

    top_jobs = [j['name'] for j in jtbd_results[:3]] if jtbd_results else []
    top_profs = [p['name'] for p in prof_results[:5]] if prof_results else []
    top_fears = [a['name'] for a in anx_results[:3]] if anx_results else []

    portraits = [
        {
            'title': 'Хочу создать и заработать',
            'icon': '🔧',
            'share': '~40%',
            'desc': f'~{int(total_people * 0.4)}+ человек',
            'tags': ['наёмный работник', '30-55 лет', 'есть идея', 'нет техзнаний'],
            'tag_colors': ['green', 'green', 'blue', 'yellow'],
            'who': (
                'Инженер, медсестра, водитель, продавец — работает в найме или на '
                'фрилансе. Увидел возможности ИИ и хочет создать бота/приложение, '
                'чтобы заработать первые деньги. Техзнаний ноль или минимум.'
            ),
            'wants': [
                'Создать конкретный продукт (бот, приложение) под свою нишу',
                'Заработать первые 10-30 тыс руб за время практикума',
                'Получить пошаговую систему «сделал → продал → получил деньги»',
                'Работать удалённо, из дома',
            ],
            'pains': [
                'Не знает КАК зарабатывать на вайбкодинге — нет схемы',
                'Самостоятельно — затыки, хотя у ведущего всё просто',
                'Не получается вынести прототип за пределы студии',
                'Не понимает про хостинг, домены, API, серверы',
            ],
            'needs': [
                'Пошаговая инструкция: промпт → прототип → рабочая ссылка → клиент',
                'Ведение за руку — не «вот вам урок», а «делаем вместе»',
                'Конкретный результат за 3 дня, не теория',
            ],
        },
        {
            'title': 'У меня бизнес — хочу автоматизировать',
            'icon': '🏪',
            'share': '~25%',
            'desc': f'~{int(total_people * 0.25)}+ человек',
            'tags': ['владелец бизнеса', '35-55 лет', 'есть клиенты', 'нет времени'],
            'tag_colors': ['orange', 'orange', 'blue', 'yellow'],
            'who': (
                'Владелец малого бизнеса — суши-бар, ремонт, юрфирма, салон красоты. '
                'Уже есть клиенты и продукт. Но много рутины, дорогие разработчики, '
                'нет автоматизации. Хочет бота-автоответчика, CRM, калькулятор.'
            ),
            'wants': [
                'Автоматизировать операционку — бот вместо менеджера',
                'Масштабировать бизнес без найма новых людей',
                'Создать инструмент для клиентов (калькулятор, каталог, бот)',
                'Сделать самому, а не платить 200-500 тыс разработчикам',
            ],
            'pains': [
                'Много рутины — не хватает рук и времени',
                'Разработчики дорого и долго, результат непредсказуемый',
                'Не может довести прототип до рабочего продукта',
                'Не понимает куда разместить, как привязать домен',
            ],
            'needs': [
                'Готовые шаблоны под бизнес-ниши (общепит, ремонт, услуги)',
                'Полный цикл: от идеи до работающей ссылки, без программистов',
                'Понимание стоимости и ROI — «окупится за N дней»',
            ],
        },
        {
            'title': 'Хочу сменить жизнь',
            'icon': '🔄',
            'share': '~20%',
            'desc': 'пенсионеры + безработные + уставшие',
            'tags': ['пенсионер / безработный', '45-65+ лет', 'минимум дохода', 'максимум мотивации'],
            'tag_colors': ['pink', 'pink', 'blue', 'yellow'],
            'who': (
                'Пенсионер, безработный или уставший от найма. Ищет новый источник '
                'дохода, новую профессию. Технически не подкован, но очень мотивирован. '
                'Готов учиться, если объяснят понятно.'
            ),
            'wants': [
                'Новая профессия, которая кормит',
                'Работа из дома, без начальника',
                'Понять свою нишу — чем может быть полезен',
                'Простые понятные инструкции без IT-жаргона',
            ],
            'pains': [
                'Маленькая пенсия / нет дохода',
                'Страх «я слишком стар / не разберусь»',
                'Не понимает с чего начать и кому это нужно',
                'Боится вложить деньги и не получить результат',
            ],
            'needs': [
                'Истории успеха от таких же пенсионеров / начинающих',
                'Доступная цена или рассрочка',
                'Наставник, который не бросит после оплаты',
            ],
        },
    ]
    return portraits


def _generate_recommendations(
    jtbd_results: list[dict],
    anx_results: list[dict],
    product_results: list[dict],
) -> list[dict]:
    """Generate 5-7 offer recommendations based on analysis data."""
    recs = []

    # Rec 1: Language
    if jtbd_results:
        top_job = jtbd_results[0]
        recs.append({
            'title': f'Говори «{top_job["name"].upper()}», не «НАУЧИТЬСЯ»',
            'text': (
                f'«{top_job["name"]}» — Job #1 ({top_job["people"]} человек). '
                f'Люди приходят за результатом, не за процессом.'
            ),
            'action': 'В каждом слайде начинай с результата в деньгах, не с процесса обучения.',
        })

    # Rec 2: Product specifics
    if product_results:
        top_prod = product_results[0]
        recs.append({
            'title': f'Покажи {top_prod["name"]} — это хит',
            'text': (
                f'{top_prod["name"]} — {top_prod["count"]} упоминаний. '
                f'Аудитория хочет конкретный продукт, не абстрактные навыки.'
            ),
            'action': 'Демонстрируй создание конкретного продукта в прямом эфире — это конвертит.',
        })

    # Rec 3: Fears
    if anx_results:
        top_fear = anx_results[0]
        recs.append({
            'title': f'Закрой страх: {top_fear["name"]}',
            'text': (
                f'{top_fear["count"]} упоминаний этого страха. '
                f'Люди боятся — покажи что получится.'
            ),
            'action': 'Истории успеха от реальных участников. Скриншоты результатов. «Если получилось у Алмаза за 1 вечер — получится и у тебя».',
        })

    # Rec 4: Path from prototype to production
    recs.append({
        'title': 'Покажи путь: от промпта до рабочей ссылки',
        'text': (
            'Главная боль — прототип есть, а рабочего продукта нет. '
            '«15 приложений в студии и ни одного за её пределами».'
        ),
        'action': 'Полный цикл в эфире: создать → задеплоить → дать ссылку. Это закрывает сомнения.',
    })

    # Rec 5: Money math
    recs.append({
        'title': 'Считай деньги вместе с аудиторией',
        'text': (
            'Сколько стоит 1 бот для клиента? 10-30 тыс. Сколько нужно клиентов? 3-5 в месяц. '
            'Это 30-150 тыс/мес без офиса.'
        ),
        'action': 'Калькулятор окупаемости прямо в эфире. Покажи ROI за 1 месяц.',
    })

    # Rec 6: Professions
    recs.append({
        'title': 'Называй их профессии, не абстрактную «аудиторию»',
        'text': (
            'Медсестра, водитель, пенсионер, бухгалтер — люди хотят слышать '
            'свою профессию. Это включает внимание.'
        ),
        'action': 'В слайдах: «Если вы юрист — вот бот для консультаций. Если повар — вот калькулятор для кейтеринга».',
    })

    # Rec 7: Urgency without pressure
    recs.append({
        'title': 'Создай срочность через стоимость ожидания',
        'text': (
            'Каждый месяц без навыка = упущенные клиенты. '
            'Не давление, а математика.'
        ),
        'action': '«Каждый месяц без бота — это 3 клиента, которые ушли к конкуренту с автоответчиком».',
    })

    return recs


def analyze_day(messages: list[dict]) -> dict:
    """
    Run full JTBD analysis on a list of cleaned messages.

    Args:
        messages: List of dicts with keys: time, sender_id, name, message

    Returns:
        Structured dict with stats, jtbd, professions, products,
        anxieties, portraits, recommendations.
    """
    jtbd_config = _load_json('jtbd_categories.json')
    prof_config = _load_json('professions.json')
    product_config = _load_json('products.json')
    anx_config = _load_json('anxieties.json')

    total_people = len(set(m['sender_id'] for m in messages))

    jtbd = _analyze_jtbd(messages, jtbd_config)
    professions = _analyze_professions(messages, prof_config)
    products = _analyze_products(messages, product_config)
    anxieties = _analyze_anxieties(messages, anx_config)
    portraits = _generate_portraits(jtbd, professions, anxieties, total_people)
    recommendations = _generate_recommendations(jtbd, anxieties, products)

    return {
        'stats': {
            'total_messages': len(messages),
            'unique_people': total_people,
        },
        'jtbd': jtbd,
        'professions': professions,
        'products': products,
        'anxieties': anxieties,
        'portraits': portraits,
        'recommendations': recommendations,
    }
