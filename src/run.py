#!/usr/bin/env python3
"""
CLI entry point for audience analyzer.

Usage:
    python src/run.py input/chat_day1.csv [input/chat_day2.csv]
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

from clean import clean_messages
from analyze import analyze_day
from build_html import build_dashboard


def main():
    if len(sys.argv) < 2 or '--help' in sys.argv or '-h' in sys.argv:
        print("Анализатор аудитории вебинара")
        print()
        print("Использование:")
        print("  python src/run.py <chat_day1.csv> [chat_day2.csv]")
        print()
        print("Примеры:")
        print("  python src/run.py input/chat_day1.csv")
        print("  python src/run.py input/chat_day1.csv input/chat_day2.csv")
        print()
        print("Результат сохраняется в output/dashboard.html")
        sys.exit(0)

    csv_path_1 = Path(sys.argv[1])
    csv_path_2 = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    if not csv_path_1.exists():
        print(f"Файл не найден: {csv_path_1}")
        sys.exit(1)

    if csv_path_2 and not csv_path_2.exists():
        print(f"Файл не найден: {csv_path_2}")
        sys.exit(1)

    # Step 1: Clean
    print(f"[1/4] Очистка чата: {csv_path_1.name}")
    messages_1 = clean_messages(csv_path_1)
    print(f"      Содержательных сообщений: {len(messages_1)}")
    print(f"      Уникальных участников: {len(set(m['sender_id'] for m in messages_1))}")

    messages_2 = None
    if csv_path_2:
        print(f"[1/4] Очистка чата: {csv_path_2.name}")
        messages_2 = clean_messages(csv_path_2)
        print(f"      Содержательных сообщений: {len(messages_2)}")
        print(f"      Уникальных участников: {len(set(m['sender_id'] for m in messages_2))}")

    # Step 2: Analyze
    print("[2/4] JTBD-анализ день 1...")
    day1_data = analyze_day(messages_1)

    day2_data = None
    if messages_2:
        print("[2/4] JTBD-анализ день 2...")
        day2_data = analyze_day(messages_2)

    # Step 3: Build HTML
    print("[3/4] Сборка HTML-дашборда...")
    html = build_dashboard(day1_data, day2_data)

    # Step 4: Save
    output_dir = PROJECT_ROOT / 'output'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / 'dashboard.html'
    output_path.write_text(html, encoding='utf-8')

    print(f"[4/4] Готово!")
    print()
    print(f"Дашборд: {output_path}")
    print()

    # Summary
    s = day1_data['stats']
    print("=== СВОДКА ===")
    print(f"День 1: {s['total_messages']} сообщений, {s['unique_people']} участников")

    if day2_data:
        s2 = day2_data['stats']
        print(f"День 2: {s2['total_messages']} сообщений, {s2['unique_people']} участников")

    print()
    print("ТОП-5 Jobs:")
    for j in day1_data.get('jtbd', [])[:5]:
        print(f"  {j['name']}: {j['count']} упоминаний / {j['people']} чел.")

    print()
    print("ТОП-3 Страхи:")
    for a in day1_data.get('anxieties', [])[:3]:
        print(f"  {a['name']}: {a['count']}")

    print()
    print("ТОП-5 Продукты:")
    for p in day1_data.get('products', [])[:5]:
        print(f"  {p['name']}: {p['count']}")


if __name__ == '__main__':
    main()
