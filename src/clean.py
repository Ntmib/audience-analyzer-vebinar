"""
CSV cleaner module for webinar chat analysis.
Supports multiple input formats: chat, survey, sales.
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
MIN_MESSAGE_LENGTH_SOFT = 5  # for survey/sales — shorter but still meaningful


def _is_noise(message: str, strict: bool = True) -> bool:
    """Check if a message is noise (too short, greeting, emoji-only, etc.).

    Args:
        message: Text to check.
        strict: If True, use aggressive filtering (chat mode).
                If False, lighter filtering (survey/sales mode).
    """
    msg = message.strip()
    if not msg:
        return True

    for pattern in NOISE_PATTERNS:
        if re.match(pattern, msg, re.IGNORECASE):
            return True

    # Strip emoji/punctuation, check length
    text_only = re.sub(r'[^\w\s]', '', msg)
    text_only = re.sub(r'\s+', ' ', text_only).strip()

    min_len = MIN_MESSAGE_LENGTH if strict else MIN_MESSAGE_LENGTH_SOFT
    if len(text_only) < min_len:
        return True

    # Greeting check (only in strict mode)
    if strict:
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


def _detect_text_column(headers: list[str], rows: list[list[str]]) -> int | None:
    """Auto-detect the column with the longest average text content.

    Used for survey and sales CSVs where the text column name varies.
    Returns column index or None.
    """
    if not rows or not headers:
        return None

    # First, try to match by known column name patterns
    text_col_patterns = [
        r'(?:ответ|текст|комментарий|сообщение|отзыв|причина|возражение|описание)',
        r'(?:comment|text|message|answer|response|feedback|reason)',
    ]
    for i, h in enumerate(headers):
        h_lower = h.lower().strip()
        for pattern in text_col_patterns:
            if re.search(pattern, h_lower):
                return i

    # Fallback: find column with longest average text
    avg_lengths = []
    for col_idx in range(len(headers)):
        texts = []
        for row in rows:
            if col_idx < len(row):
                texts.append(len(row[col_idx].strip()))
            else:
                texts.append(0)
        avg_len = sum(texts) / len(texts) if texts else 0
        avg_lengths.append(avg_len)

    if not avg_lengths:
        return None

    max_avg = max(avg_lengths)
    if max_avg < 3:
        return None

    return avg_lengths.index(max_avg)


def _detect_name_column(headers: list[str]) -> int | None:
    """Auto-detect the name column in a CSV."""
    name_patterns = [
        r'(?:имя|name|фио|клиент|участник|пользователь|ник)',
    ]
    for i, h in enumerate(headers):
        h_lower = h.lower().strip()
        for pattern in name_patterns:
            if re.search(pattern, h_lower):
                return i
    return None


def _detect_manager_column(headers: list[str]) -> int | None:
    """Auto-detect the manager column in a sales CSV."""
    patterns = [r'(?:менеджер|manager|сотрудник|оператор|продавец)']
    for i, h in enumerate(headers):
        h_lower = h.lower().strip()
        for pattern in patterns:
            if re.search(pattern, h_lower):
                return i
    return None


# ──────────────────── Chat cleaner (existing logic) ────────────────────

def clean_chat(
    input_path: str | Path,
    moderators: list[str] | None = None,
) -> list[dict]:
    """
    Load a CSV chat export and return cleaned messages.

    Args:
        input_path: Path to CSV with columns:
            Время | id отправителя | Имя | id получателя | Сообщение
        moderators: Names to filter out (partial match).

    Returns:
        List of dicts with keys: time, sender_id, name, message
    """
    if moderators is None:
        moderators = []

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

            if moderators and _is_moderator(name, moderators):
                continue

            if _is_noise(message, strict=True):
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


# ──────────────────── Survey cleaner ────────────────────

def clean_survey(input_path: str | Path) -> list[dict]:
    """
    Load a survey CSV and return cleaned responses.

    Auto-detects text and name columns.

    Returns:
        List of dicts with keys: name, message
    """
    input_path = Path(input_path)
    messages: list[dict] = []

    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader, None)
        if not headers:
            return []

        rows = list(reader)

    text_col = _detect_text_column(headers, rows)
    name_col = _detect_name_column(headers)

    if text_col is None:
        return []

    for row in rows:
        if text_col >= len(row):
            continue

        message = row[text_col].strip()
        if _is_noise(message, strict=False):
            continue

        cleaned = _clean_text(message)
        if not cleaned:
            continue

        name = ''
        if name_col is not None and name_col < len(row):
            name = row[name_col].strip()

        messages.append({
            'name': name or 'Аноним',
            'message': cleaned,
        })

    return messages


# ──────────────────── Sales cleaner ────────────────────

def clean_sales(input_path: str | Path) -> list[dict]:
    """
    Load a sales CSV (Google Sheets export) and return cleaned entries.

    Auto-detects text, name, and manager columns.

    Returns:
        List of dicts with keys: name, message, manager (optional)
    """
    input_path = Path(input_path)
    messages: list[dict] = []

    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader, None)
        if not headers:
            return []

        rows = list(reader)

    text_col = _detect_text_column(headers, rows)
    name_col = _detect_name_column(headers)
    manager_col = _detect_manager_column(headers)

    if text_col is None:
        return []

    for row in rows:
        if text_col >= len(row):
            continue

        message = row[text_col].strip()
        if _is_noise(message, strict=False):
            continue

        cleaned = _clean_text(message)
        if not cleaned:
            continue

        name = ''
        if name_col is not None and name_col < len(row):
            name = row[name_col].strip()

        entry = {
            'name': name or 'Аноним',
            'message': cleaned,
        }

        if manager_col is not None and manager_col < len(row):
            entry['manager'] = row[manager_col].strip()

        messages.append(entry)

    return messages


# ──────────────────── Format detection ────────────────────

def detect_format(input_path: str | Path) -> str:
    """
    Auto-detect CSV format: 'chat', 'survey', or 'sales'.

    Detection logic:
    - chat: has 5+ columns, headers match chat pattern (Время, id, Имя, Сообщение)
    - sales: headers contain manager/менеджер + возражение/причина
    - survey: everything else with text content

    Returns:
        'chat', 'survey', or 'sales'
    """
    input_path = Path(input_path)

    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader, None)
        if not headers:
            return 'survey'  # fallback

    headers_lower = [h.lower().strip() for h in headers]
    headers_joined = ' '.join(headers_lower)

    # Chat: has columns like "время", "id отправителя", "имя", "сообщение"
    chat_markers = ['время', 'id отправител', 'имя', 'сообщени']
    chat_score = sum(1 for m in chat_markers if any(m in h for h in headers_lower))
    if chat_score >= 3 or (len(headers) >= 5 and 'id' in headers_joined and 'сообщени' in headers_joined):
        return 'chat'

    # Sales: has manager column + objection/reason column
    sales_markers = ['менеджер', 'manager', 'оператор', 'продавец', 'сотрудник']
    has_manager = any(m in headers_joined for m in sales_markers)
    sales_text_markers = ['возражени', 'причина', 'отказ', 'комментарий', 'feedback']
    has_sales_text = any(m in headers_joined for m in sales_text_markers)
    if has_manager and has_sales_text:
        return 'sales'
    if has_manager:
        return 'sales'

    # Default: survey
    return 'survey'


# ──────────────────── Auto cleaner ────────────────────

def clean_auto(
    input_path: str | Path,
    moderators: list[str] | None = None,
) -> tuple[str, list[dict]]:
    """
    Auto-detect format and clean a CSV file.

    Returns:
        Tuple of (format_name, cleaned_messages)
    """
    fmt = detect_format(input_path)

    if fmt == 'chat':
        return fmt, clean_chat(input_path, moderators=moderators)
    elif fmt == 'sales':
        return fmt, clean_sales(input_path)
    else:
        return fmt, clean_survey(input_path)


# ──────────────────── Legacy alias ────────────────────

def clean_messages(
    input_path: str | Path,
    moderator_names: list[str] | None = None,
) -> list[dict]:
    """Legacy alias for clean_chat. Kept for backwards compatibility."""
    return clean_chat(input_path, moderators=moderator_names)
