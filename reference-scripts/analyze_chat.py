"""
Скрипт очистки и подготовки чата вебинара для анализа ЦА.
Убирает мусор, оставляет содержательные сообщения.
"""

import csv
import re
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).parent.parent
INPUT_FILE = BASE_DIR / "Выгрузка из чата.csv"
OUTPUT_FILE = BASE_DIR / "Материалы" / "chat_cleaned.md"

# Паттерны мусорных сообщений
NOISE_PATTERNS = [
    r'^[\+\!\.\,\?\s]+$',                    # только +, !, ., пробелы
    r'^[^\w\s]*$',                             # только эмодзи/символы
    r'^\s*$',                                  # пустые
    r'^https?://',                             # ссылки
    r'aiquiz\.aibasis',                        # ссылки на анкету
]

# Приветствия и прощания (точное или начало)
GREETING_WORDS = [
    'привет', 'здравствуйте', 'добрый вечер', 'добрый день', 'доброй ночи',
    'здравия', 'всем привет', 'приветствую', 'хай', 'hello', 'hi',
    'пока', 'до свидания', 'до завтра', 'до встречи', 'всем пока',
    'спасибо', 'благодарю', 'спасибо за эфир', 'спасибо большое',
    'класс', 'огонь', 'супер', 'круто', 'ого', 'вау', 'ура',
    'да', 'нет', 'ок', 'хорошо', 'понятно', 'ясно', 'точно',
]

# Имена модераторов/ведущих
MODERATOR_NAMES = ['Модератор Полина', 'Модератор']

MIN_MESSAGE_LENGTH = 15  # минимальная длина содержательного сообщения


def is_noise(message: str) -> bool:
    """Проверяет, является ли сообщение мусором."""
    msg = message.strip()

    # Пустое
    if not msg:
        return True

    # Паттерны мусора
    for pattern in NOISE_PATTERNS:
        if re.match(pattern, msg, re.IGNORECASE):
            return True

    # Слишком короткое
    # Убираем эмодзи и спецсимволы для подсчёта длины
    text_only = re.sub(r'[^\w\s]', '', msg)
    text_only = re.sub(r'\s+', ' ', text_only).strip()
    if len(text_only) < MIN_MESSAGE_LENGTH:
        return True

    # Приветствия (если сообщение по сути только приветствие)
    msg_lower = msg.lower().strip('!., \n\r\t')
    # Убираем эмодзи для сравнения
    msg_clean = re.sub(r'[^\w\s]', '', msg_lower).strip()
    for greeting in GREETING_WORDS:
        if msg_clean == greeting or msg_clean.startswith(greeting) and len(msg_clean) < len(greeting) + 15:
            return True

    return False


def is_moderator(name: str) -> bool:
    """Проверяет, является ли отправитель модератором."""
    return any(mod.lower() in name.lower() for mod in MODERATOR_NAMES)


def clean_message(message: str) -> str:
    """Очищает сообщение от лишних символов."""
    # Убираем множественные эмодзи (оставляем одиночные)
    msg = re.sub(r'(.)\1{4,}', r'\1', message)
    # Убираем множественные знаки препинания
    msg = re.sub(r'([!?.]){3,}', r'\1', msg)
    # Убираем лишние пробелы
    msg = re.sub(r'\s+', ' ', msg).strip()
    return msg


def main():
    messages = []
    total = 0
    moderator_count = 0
    noise_count = 0

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)  # пропускаем заголовок

        for row in reader:
            if len(row) < 5:
                continue
            total += 1

            time, sender_id, name, receiver_id, message = row[0], row[1], row[2], row[3], row[4]

            # Если сообщение на нескольких строках, объединяем
            # CSV reader уже обрабатывает это

            if is_moderator(name):
                moderator_count += 1
                continue

            if is_noise(message):
                noise_count += 1
                continue

            cleaned = clean_message(message)
            if cleaned:
                messages.append({
                    'time': time,
                    'name': name,
                    'message': cleaned,
                })

    # Статистика
    print(f"Всего сообщений: {total}")
    print(f"Модератор: {moderator_count}")
    print(f"Мусор (приветствия, +, эмодзи): {noise_count}")
    print(f"Содержательных: {len(messages)}")
    print(f"Процент полезных: {len(messages)/total*100:.1f}%")

    # Уникальные участники
    unique_names = set(m['name'] for m in messages)
    print(f"Уникальных участников (с содержательными сообщениями): {len(unique_names)}")

    # Сохраняем в файл
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("# Очищенный чат вебинара — содержательные сообщения\n\n")
        f.write(f"**Всего сообщений:** {total}\n")
        f.write(f"**После очистки:** {len(messages)}\n")
        f.write(f"**Уникальных участников:** {len(unique_names)}\n\n")
        f.write("---\n\n")

        for m in messages:
            f.write(f"**[{m['time']}] {m['name']}:** {m['message']}\n\n")

    print(f"\nСохранено в: {OUTPUT_FILE}")


if __name__ == '__main__':
    main()
