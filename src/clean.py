"""
CSV cleaner module for webinar chat analysis.
Filters noise, greetings, short messages, moderators.
"""

import csv
import re
from pathlib import Path


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

MIN_MESSAGE_LENGTH = 15


def _is_noise(message: str) -> bool:
    """Check if a message is noise (too short, greeting, emoji-only, etc.)."""
    msg = message.strip()
    if not msg:
        return True

    for pattern in NOISE_PATTERNS:
        if re.match(pattern, msg, re.IGNORECASE):
            return True

    # Strip emoji/punctuation, check length
    text_only = re.sub(r'[^\w\s]', '', msg)
    text_only = re.sub(r'\s+', ' ', text_only).strip()
    if len(text_only) < MIN_MESSAGE_LENGTH:
        return True

    # Greeting check
    msg_lower = msg.lower().strip('!., \n\r\t')
    msg_clean = re.sub(r'[^\w\s]', '', msg_lower).strip()
    for greeting in GREETING_WORDS:
        if msg_clean == greeting or (
            msg_clean.startswith(greeting) and len(msg_clean) < len(greeting) + 15
        ):
            return True

    return False


def _is_moderator(name: str, moderator_names: list[str]) -> bool:
    """Check if sender is a moderator."""
    name_lower = name.lower()
    return any(mod.lower() in name_lower for mod in moderator_names)


def _clean_text(message: str) -> str:
    """Normalize a message: collapse repeats, extra whitespace."""
    msg = re.sub(r'(.)\1{4,}', r'\1', message)
    msg = re.sub(r'([!?.]){3,}', r'\1', msg)
    msg = re.sub(r'\s+', ' ', msg).strip()
    return msg


def clean_messages(
    input_path: str | Path,
    moderator_names: list[str] | None = None,
) -> list[dict]:
    """
    Load a CSV chat export and return cleaned messages.

    Args:
        input_path: Path to CSV with columns:
            Время | id отправителя | Имя | id получателя | Сообщение
        moderator_names: Names to filter out (partial match).

    Returns:
        List of dicts with keys: time, sender_id, name, message
    """
    if moderator_names is None:
        moderator_names = ['Модератор Полина', 'Модератор']

    input_path = Path(input_path)
    messages: list[dict] = []

    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header

        for row in reader:
            if len(row) < 5:
                continue

            time_str, sender_id, name, _receiver_id, message = (
                row[0], row[1], row[2], row[3], row[4]
            )

            if _is_moderator(name, moderator_names):
                continue

            if _is_noise(message):
                continue

            cleaned = _clean_text(message)
            if not cleaned:
                continue

            messages.append({
                'time': time_str,
                'sender_id': sender_id,
                'name': name,
                'message': cleaned,
            })

    return messages
