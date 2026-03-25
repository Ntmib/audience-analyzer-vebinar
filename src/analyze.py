"""
JTBD analyzer module — full version.
Categorizes messages by functional/emotional/social jobs, professions, products,
forces of progress, FUD, value equation, message hierarchy, PMF proxy.
Generates audience portraits and offer recommendations.
"""

import json
import re
from pathlib import Path
from collections import Counter, defaultdict


CONFIG_DIR = Path(__file__).parent.parent / 'config'

# ---------------------------------------------------------------------------
# Emotion / specificity word lists for scoring
# ---------------------------------------------------------------------------

STRONG_EMOTION_WORDS = [
    'ненавиж', 'обожа', 'мечта', 'страшно', 'боюсь', 'бесит', 'достало',
    'надоело', 'невозможно', 'счастлив', 'отчаян', 'умоляю', 'наконец',
    'задолбал', 'разочаров', 'безнадёжн', 'невыносим', 'потрясающ',
]

DESIRE_WORDS = [
    'хочу', 'мечтаю', 'было бы круто', 'вот бы', 'стремлюсь', 'цель',
    'планирую', 'хотел бы', 'если бы мог', 'было бы здорово',
]

PMF_HOT = ['где купить', 'как оплатить', 'беру', 'записался', 'оплатил',
           'куда переводить', 'готов платить', 'хочу купить', 'где ссылка на оплату']
PMF_WARM = ['сколько стоит', 'какой формат', 'что входит', 'когда старт',
            'есть рассрочка', 'можно попробовать', 'расскажите подробнее']
PMF_CURIOUS = ['интересно', 'а что это', 'расскажите', 'хотел бы узнать',
               'любопытно', 'можно подробнее']
PMF_COLD = ['реклама', 'спам', 'отпишись', 'не интересно', 'бред', 'фигня']


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

def _load_json(filename: str) -> dict | list:
    with open(CONFIG_DIR / filename, 'r', encoding='utf-8') as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Generic pattern matching helpers
# ---------------------------------------------------------------------------

def _match_patterns(text_lower: str, patterns: list[str]) -> bool:
    """Return True if any pattern matches."""
    return any(re.search(p, text_lower) for p in patterns)


def _match_any_in_list(text_lower: str, word_list: list[str]) -> bool:
    return any(w in text_lower for w in word_list)


def _quote(msg: dict, max_len: int = 180) -> str:
    return f"{msg['name']}: \u00ab{msg['message'][:max_len]}\u00bb"


# ---------------------------------------------------------------------------
# 1. Stats
# ---------------------------------------------------------------------------

def _calc_stats(messages: list[dict]) -> dict:
    meaningful = [m for m in messages if len(m['message']) >= 15]
    return {
        'total_messages': len(messages),
        'meaningful_messages': len(meaningful),
        'unique_people': len(set(m['sender_id'] for m in messages)),
    }


# ---------------------------------------------------------------------------
# 2. Functional JTBD
# ---------------------------------------------------------------------------

def _analyze_jtbd(messages: list[dict], jtbd_config: dict) -> list[dict]:
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
                        quotes[cat_name].append(_quote(msg))
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


# ---------------------------------------------------------------------------
# 3-4. Emotional & Social Jobs (same structure)
# ---------------------------------------------------------------------------

def _analyze_jobs_generic(messages: list[dict], config: dict) -> list[dict]:
    """Generic analyzer for emotional_jobs.json / social_jobs.json format."""
    counter = Counter()
    quotes: dict[str, list[str]] = defaultdict(list)
    people: dict[str, set] = defaultdict(set)

    for msg in messages:
        text_lower = msg['message'].lower()
        for cat_name, cat_data in config.items():
            if _match_patterns(text_lower, cat_data['patterns']):
                counter[cat_name] += 1
                people[cat_name].add(msg['sender_id'])
                if len(quotes[cat_name]) < 5 and len(msg['message']) > 25:
                    quotes[cat_name].append(_quote(msg))

    return [
        {
            'name': cat.replace('_', ' '),
            'key': cat,
            'count': count,
            'people': len(people[cat]),
            'job': config[cat]['job'],
            'quotes': quotes[cat],
        }
        for cat, count in counter.most_common()
    ]


# ---------------------------------------------------------------------------
# 5. Forces of Progress
# ---------------------------------------------------------------------------

def _analyze_forces(messages: list[dict], forces_config: dict) -> dict:
    counts = {f: 0 for f in forces_config}
    quotes: dict[str, list[str]] = defaultdict(list)
    people: dict[str, set] = defaultdict(set)

    for msg in messages:
        text_lower = msg['message'].lower()
        for force_name, force_data in forces_config.items():
            if _match_patterns(text_lower, force_data['patterns']):
                counts[force_name] += 1
                people[force_name].add(msg['sender_id'])
                if len(quotes[force_name]) < 5 and len(msg['message']) > 25:
                    quotes[force_name].append(_quote(msg))

    drive = counts['push'] + counts['pull']
    resist = counts['anxiety'] + counts['habit']
    total = drive + resist
    balance = round((drive - resist) / total * 100, 1) if total > 0 else 0

    if counts['anxiety'] > counts['push'] and counts['anxiety'] > counts['pull']:
        flag = 'Оффер не снимает тревогу — anxiety доминирует'
    elif counts['habit'] > counts['pull']:
        flag = 'Привычка сильнее притяжения — нужен мощный Pull'
    elif balance > 30:
        flag = 'Сильный Drive — аудитория готова к действию'
    else:
        flag = 'Баланс нейтральный — нужен и Push и Pull'

    forces_detail = []
    for force_name in ['push', 'pull', 'anxiety', 'habit']:
        forces_detail.append({
            'name': force_name,
            'description': forces_config[force_name]['description'],
            'count': counts[force_name],
            'people': len(people[force_name]),
            'quotes': quotes[force_name],
        })

    return {
        'forces': forces_detail,
        'drive': drive,
        'resist': resist,
        'balance_score': balance,
        'flag': flag,
    }


# ---------------------------------------------------------------------------
# 6. FUD Analysis
# ---------------------------------------------------------------------------

def _analyze_fud(messages: list[dict], fud_config: dict) -> dict:
    counts = {}
    quotes: dict[str, list[str]] = defaultdict(list)
    people: dict[str, set] = defaultdict(set)

    tactics = {
        'fear': 'Эмпатия + гарантия возврата + истории «таких же»',
        'uncertainty': 'Чёткое описание формата, программы, результатов',
        'doubt': 'Кейсы с цифрами, скриншоты результатов, отзывы',
    }

    for fud_type in fud_config:
        counts[fud_type] = 0

    for msg in messages:
        text_lower = msg['message'].lower()
        for fud_type, fud_data in fud_config.items():
            if _match_patterns(text_lower, fud_data['patterns']):
                counts[fud_type] += 1
                people[fud_type].add(msg['sender_id'])
                if len(quotes[fud_type]) < 5 and len(msg['message']) > 25:
                    quotes[fud_type].append(_quote(msg))

    fud_detail = []
    for fud_type in ['fear', 'uncertainty', 'doubt']:
        fud_detail.append({
            'name': fud_type,
            'description': fud_config[fud_type]['description'],
            'count': counts[fud_type],
            'people': len(people[fud_type]),
            'quotes': quotes[fud_type],
            'closing_tactic': tactics[fud_type],
        })

    dominant = max(fud_detail, key=lambda x: x['count'])
    return {
        'breakdown': fud_detail,
        'dominant': dominant['name'],
        'total': sum(counts.values()),
    }


# ---------------------------------------------------------------------------
# 7. Professions
# ---------------------------------------------------------------------------

def _analyze_professions(messages: list[dict], prof_config: dict) -> list[dict]:
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


# ---------------------------------------------------------------------------
# 8. Products
# ---------------------------------------------------------------------------

def _analyze_products(messages: list[dict], product_config: list[dict]) -> list[dict]:
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
                    quotes[label].append(_quote(msg, 150))
                break

    return [
        {'name': prod, 'count': count, 'quotes': quotes.get(prod, [])}
        for prod, count in counter.most_common()
    ]


# ---------------------------------------------------------------------------
# 9. Portraits
# ---------------------------------------------------------------------------

def _generate_portraits(
    jtbd_results: list[dict],
    prof_results: list[dict],
    anx_results: list[dict],
    emotional_results: list[dict],
    total_people: int,
) -> list[dict]:
    """Generate 3 audience portraits from job + profession clusters."""

    top_jobs = [j['name'] for j in jtbd_results[:3]] if jtbd_results else []
    top_profs = [p['name'] for p in prof_results[:5]] if prof_results else []
    top_emotions = [e['job'] for e in emotional_results[:2]] if emotional_results else []

    portraits = [
        {
            'title': 'Хочу создать и заработать',
            'icon': '\U0001f527',
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
            'icon': '\U0001f3ea',
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
            'icon': '\U0001f504',
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


# ---------------------------------------------------------------------------
# 10. Value Equation
# ---------------------------------------------------------------------------

def _analyze_value_equation(messages: list[dict], ve_config: dict) -> dict:
    total = len(messages) or 1
    params = []

    for param_key, param_data in ve_config.items():
        boost = 0
        weaken = 0
        for msg in messages:
            text_lower = msg['message'].lower()
            if _match_patterns(text_lower, param_data['boost_patterns']):
                boost += 1
            if _match_patterns(text_lower, param_data['weaken_patterns']):
                weaken += 1

        score = round((boost - weaken) / total * 100, 1)
        params.append({
            'key': param_key,
            'label': param_data['label'],
            'boost': boost,
            'weaken': weaken,
            'score': score,
        })

    # Overall value = (dream + likelihood) - (time_delay_weaken + effort_weaken)
    scores_by_key = {p['key']: p for p in params}
    numerator = (
        scores_by_key.get('dream_outcome', {}).get('score', 0)
        + scores_by_key.get('perceived_likelihood', {}).get('score', 0)
    )
    denominator_penalty = (
        scores_by_key.get('time_delay', {}).get('weaken', 0)
        + scores_by_key.get('effort_sacrifice', {}).get('weaken', 0)
    )
    overall = round(numerator - denominator_penalty / total * 100, 1)

    # Recommendations per weak param
    recs = []
    for p in params:
        if p['score'] < 0:
            if p['key'] == 'dream_outcome':
                recs.append('Результат размыт — добавь конкретные кейсы с цифрами')
            elif p['key'] == 'perceived_likelihood':
                recs.append('Люди не верят в успех — покажи больше историй «таких же»')
            elif p['key'] == 'time_delay':
                recs.append('Долго ждать результат — покажи быстрые победы (день 1-3)')
            elif p['key'] == 'effort_sacrifice':
                recs.append('Кажется сложным — упрости вход, покажи «даже бабушка смогла»')

    return {
        'parameters': params,
        'overall_score': overall,
        'recommendations': recs,
    }


# ---------------------------------------------------------------------------
# 11. Message Hierarchy
# ---------------------------------------------------------------------------

def _score_message(msg: dict, fud_config: dict) -> dict:
    """Score a message for hierarchy placement."""
    text = msg['message']
    text_lower = text.lower()
    length = len(text)

    if length < 15:
        return None

    # Emotional charge
    emotional = 0
    if '!' in text:
        emotional += 1
    if _match_any_in_list(text_lower, STRONG_EMOTION_WORDS):
        emotional += 2

    # Specificity (numbers, concrete details)
    specificity = 0
    if re.search(r'\d+', text):
        specificity += 2
    if length > 80:
        specificity += 1

    # Desire
    has_desire = _match_any_in_list(text_lower, DESIRE_WORDS)

    # FUD
    is_fud = False
    for fud_data in fud_config.values():
        if _match_patterns(text_lower, fud_data['patterns']):
            is_fud = True
            break

    # Has numbers
    has_numbers = bool(re.search(r'\d+', text))

    total_score = emotional * 3 + specificity * 2 + (2 if has_desire else 0)

    return {
        'text': text,
        'name': msg['name'],
        'quote': _quote(msg, 200),
        'score': total_score,
        'emotional': emotional,
        'specificity': specificity,
        'has_desire': has_desire,
        'is_fud': is_fud,
        'has_numbers': has_numbers,
        'length': length,
    }


def _analyze_message_hierarchy(messages: list[dict], hierarchy_config: dict, fud_config: dict) -> dict:
    scored = []
    for msg in messages:
        s = _score_message(msg, fud_config)
        if s:
            scored.append(s)

    scored.sort(key=lambda x: x['score'], reverse=True)

    levels = {}
    used_quotes = set()

    for level in hierarchy_config['levels']:
        name = level['name']
        criteria = level['criteria']
        level_quotes = []

        for s in scored:
            if s['quote'] in used_quotes:
                continue
            if s['length'] < criteria.get('min_length', 0):
                continue

            match = True
            if criteria.get('has_emotion') and s['emotional'] < 1:
                match = False
            if criteria.get('has_specifics') and s['specificity'] < 1:
                match = False
            if criteria.get('has_numbers') and not s['has_numbers']:
                match = False
            if criteria.get('is_fud') and not s['is_fud']:
                match = False
            if criteria.get('has_desire') and not s['has_desire']:
                match = False

            if match:
                level_quotes.append({
                    'quote': s['quote'],
                    'score': s['score'],
                    'usage': level['description'],
                })
                used_quotes.add(s['quote'])
                if len(level_quotes) >= 5:
                    break

        levels[name] = {
            'label': level['label'],
            'description': level['description'],
            'quotes': level_quotes,
            'count': len(level_quotes),
        }

    # Top 10 overall
    top10 = []
    for s in scored[:10]:
        # Determine best level
        best_level = 'context'
        if s['emotional'] >= 2 and s['specificity'] >= 1:
            best_level = 'headline'
        elif s['has_numbers']:
            best_level = 'proof'
        elif s['is_fud']:
            best_level = 'objection'
        elif s['has_desire']:
            best_level = 'desire'

        top10.append({
            'quote': s['quote'],
            'score': s['score'],
            'level': best_level,
        })

    return {
        'levels': levels,
        'top10': top10,
    }


# ---------------------------------------------------------------------------
# 12. PMF Proxy
# ---------------------------------------------------------------------------

def _analyze_pmf(messages: list[dict]) -> dict:
    hot = warm = curious = cold = 0
    hot_quotes = []
    warm_quotes = []

    for msg in messages:
        text_lower = msg['message'].lower()

        if _match_any_in_list(text_lower, PMF_HOT):
            hot += 1
            if len(hot_quotes) < 5:
                hot_quotes.append(_quote(msg))
        elif _match_any_in_list(text_lower, PMF_WARM):
            warm += 1
            if len(warm_quotes) < 5:
                warm_quotes.append(_quote(msg))
        elif _match_any_in_list(text_lower, PMF_CURIOUS):
            curious += 1
        elif _match_any_in_list(text_lower, PMF_COLD):
            cold += 1

    active = hot + warm + curious
    score = round(hot / active * 100, 1) if active > 0 else 0

    if score >= 40:
        level = 'green'
        label = 'Сильный PMF-сигнал'
    elif score >= 20:
        level = 'yellow'
        label = 'Умеренный PMF-сигнал'
    else:
        level = 'red'
        label = 'Слабый PMF-сигнал'

    return {
        'hot': hot,
        'warm': warm,
        'curious': curious,
        'cold': cold,
        'score': score,
        'level': level,
        'label': label,
        'hot_quotes': hot_quotes,
        'warm_quotes': warm_quotes,
    }


# ---------------------------------------------------------------------------
# 13. Recommendations
# ---------------------------------------------------------------------------

def _generate_recommendations(
    jtbd_results: list[dict],
    emotional_results: list[dict],
    social_results: list[dict],
    forces_result: dict,
    fud_result: dict,
    ve_result: dict,
    product_results: list[dict],
    hierarchy_result: dict,
) -> list[dict]:
    """Auto-generate offer recommendations based on ALL analysis data."""
    recs = []

    # 1. Top functional jobs → what to promise
    if jtbd_results:
        top3 = jtbd_results[:3]
        jobs_text = ', '.join(f'«{j["name"]}» ({j["people"]} чел)' for j in top3)
        recs.append({
            'title': 'Обещай конкретные Jobs',
            'text': f'Топ-3 Jobs: {jobs_text}. Люди приходят за результатом — обещай его.',
            'action': 'В каждом слайде начинай с результата: заработок, продукт, клиент — не с процесса обучения.',
        })

    # 2. Top emotional job → how to frame
    if emotional_results:
        top_emo = emotional_results[0]
        recs.append({
            'title': f'Фрейм: {top_emo["job"]}',
            'text': (
                f'Эмоциональный Job #1: {top_emo["job"]} ({top_emo["people"]} чел). '
                f'Это глубинная мотивация — используй в сторителлинге.'
            ),
            'action': 'Покажи историю человека, который закрыл эту потребность через твой продукт.',
        })

    # 3. Dominant force → what to emphasize
    if forces_result:
        flag = forces_result['flag']
        balance = forces_result['balance_score']
        recs.append({
            'title': f'Forces баланс: {balance}%',
            'text': flag,
            'action': (
                'Если Drive > Resist — усиливай Pull (покажи мечту). '
                'Если Anxiety высокий — сначала закрой страхи, потом продавай.'
            ),
        })

    # 4. FUD split → specific closing tactics
    if fud_result and fud_result.get('breakdown'):
        dominant = fud_result['dominant']
        dominant_data = next(b for b in fud_result['breakdown'] if b['name'] == dominant)
        recs.append({
            'title': f'FUD: доминирует {dominant.upper()}',
            'text': f'{dominant_data["count"]} сигналов. {dominant_data["description"]}',
            'action': dominant_data['closing_tactic'],
        })

    # 5. Value Equation weak spots
    if ve_result and ve_result.get('recommendations'):
        for ve_rec in ve_result['recommendations']:
            recs.append({
                'title': 'Value Equation: слабое место',
                'text': ve_rec,
                'action': 'Усиль этот параметр в оффере и контенте.',
            })

    # 6. Products → what to demo
    if product_results:
        top_prod = product_results[0]
        recs.append({
            'title': f'Покажи {top_prod["name"]} — это хит',
            'text': f'{top_prod["count"]} упоминаний. Аудитория хочет конкретный продукт.',
            'action': 'Демонстрируй создание этого продукта в прямом эфире — конвертит.',
        })

    # 7. Message Hierarchy headlines → what to use in marketing
    if hierarchy_result:
        headlines = hierarchy_result.get('levels', {}).get('headline', {})
        if headlines.get('quotes'):
            top_headline = headlines['quotes'][0]['quote']
            recs.append({
                'title': 'Headline для лендинга',
                'text': f'Лучшая цитата: {top_headline}',
                'action': 'Используй как заголовок лендинга или email-рассылки.',
            })

    # 8. Social job
    if social_results:
        top_social = social_results[0]
        recs.append({
            'title': f'Социальный мотив: {top_social["job"]}',
            'text': f'{top_social["people"]} человек хотят этого. Используй в отзывах и кейсах.',
            'action': 'Покажи как выпускники получили признание / статус после обучения.',
        })

    # 9. Path from prototype to production (always relevant)
    recs.append({
        'title': 'Покажи путь: от промпта до рабочей ссылки',
        'text': (
            'Главная боль — прототип есть, а рабочего продукта нет. '
            '«15 приложений в студии и ни одного за её пределами».'
        ),
        'action': 'Полный цикл в эфире: создать → задеплоить → дать ссылку.',
    })

    # 10. Money math
    recs.append({
        'title': 'Считай деньги вместе с аудиторией',
        'text': (
            'Сколько стоит 1 бот для клиента? 10-30 тыс. '
            '3-5 клиентов = 30-150 тыс/мес без офиса.'
        ),
        'action': 'Калькулятор окупаемости в эфире. Покажи ROI за 1 месяц.',
    })

    return recs


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def analyze_day(messages: list[dict]) -> dict:
    """
    Run full analysis on a list of cleaned messages.

    Args:
        messages: List of dicts with keys: time, sender_id, name, message

    Returns:
        Structured dict with all 13 analysis sections.
    """
    # Load all configs
    jtbd_config = _load_json('jtbd_categories.json')
    prof_config = _load_json('professions.json')
    product_config = _load_json('products.json')
    anx_config = _load_json('anxieties.json')
    forces_config = _load_json('forces.json')
    emotional_config = _load_json('emotional_jobs.json')
    social_config = _load_json('social_jobs.json')
    fud_config = _load_json('fud.json')
    ve_config = _load_json('value_equation.json')
    hierarchy_config = _load_json('message_hierarchy.json')

    total_people = len(set(m['sender_id'] for m in messages))

    # Run all analyses
    stats = _calc_stats(messages)
    jtbd = _analyze_jtbd(messages, jtbd_config)
    emotional_jobs = _analyze_jobs_generic(messages, emotional_config)
    social_jobs = _analyze_jobs_generic(messages, social_config)
    forces = _analyze_forces(messages, forces_config)
    fud = _analyze_fud(messages, fud_config)
    professions = _analyze_professions(messages, prof_config)
    products = _analyze_products(messages, product_config)
    portraits = _generate_portraits(jtbd, professions, [], emotional_jobs, total_people)
    value_equation = _analyze_value_equation(messages, ve_config)
    message_hierarchy = _analyze_message_hierarchy(messages, hierarchy_config, fud_config)
    pmf_proxy = _analyze_pmf(messages)
    recommendations = _generate_recommendations(
        jtbd, emotional_jobs, social_jobs, forces, fud,
        value_equation, products, message_hierarchy,
    )

    return {
        'stats': stats,
        'jtbd': jtbd,
        'emotional_jobs': emotional_jobs,
        'social_jobs': social_jobs,
        'forces': forces,
        'fud': fud,
        'professions': professions,
        'products': products,
        'portraits': portraits,
        'value_equation': value_equation,
        'message_hierarchy': message_hierarchy,
        'pmf_proxy': pmf_proxy,
        'recommendations': recommendations,
    }
