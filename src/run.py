#!/usr/bin/env python3
"""
CLI entry point for audience analyzer.

Supports:
    python src/run.py input/2026-03-24/       # single launch folder
    python src/run.py input/                   # all launches
    python src/run.py input/chat.csv           # legacy single CSV
    python src/run.py --add input/2026-03-24/ new_data.csv
"""

import json
import sys
from pathlib import Path

# Ensure project root is on sys.path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

from clean import clean_chat, clean_survey, clean_sales, clean_auto, detect_format
from analyze import analyze_day
from build_html import build_dashboard


# ──────────────────── Launch discovery ────────────────────

def is_launch_folder(path: Path) -> bool:
    """Check if a directory is a launch folder (contains launch.json)."""
    return (path / 'launch.json').exists()


def find_launches(root: Path) -> list[Path]:
    """Find all launch folders under root, sorted by name."""
    launches = []
    for item in sorted(root.iterdir()):
        if item.is_dir() and is_launch_folder(item):
            launches.append(item)
    return launches


def load_launch_meta(launch_dir: Path) -> dict:
    """Load launch.json metadata."""
    meta_path = launch_dir / 'launch.json'
    with open(meta_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def classify_csv_files(launch_dir: Path) -> dict[str, list[Path]]:
    """Classify CSV files in a launch folder by type.

    Returns dict with keys: 'chat', 'survey', 'sales'
    Each value is a sorted list of Paths.
    """
    result = {'chat': [], 'survey': [], 'sales': []}

    csv_files = sorted(launch_dir.glob('*.csv'))
    for csv_path in csv_files:
        name_lower = csv_path.stem.lower()

        # Classify by filename convention first
        if name_lower.startswith('chat') or name_lower.startswith('day'):
            result['chat'].append(csv_path)
        elif name_lower.startswith('survey') or name_lower.startswith('anketa') or 'анкет' in name_lower:
            result['survey'].append(csv_path)
        elif name_lower.startswith('sales') or name_lower.startswith('prodazh') or 'продаж' in name_lower:
            result['sales'].append(csv_path)
        else:
            # Fallback: auto-detect format
            fmt = detect_format(csv_path)
            result[fmt].append(csv_path)

    return result


# ──────────────────── Processing ────────────────────

def process_launch(launch_dir: Path) -> dict:
    """Process a single launch folder.

    Returns:
        dict with keys: meta, sources, analysis
        - meta: launch.json content
        - sources: dict of {source_type: [{file, format, count, messages}]}
        - analysis: dict of {source_key: analyze_day() result}
    """
    meta = load_launch_meta(launch_dir)
    moderators = meta.get('moderators', [])
    classified = classify_csv_files(launch_dir)

    sources = {}
    analysis = {}
    all_messages = []

    # Process chat files (day1, day2, ...)
    for i, chat_path in enumerate(classified['chat'], 1):
        key = f'chat_day{i}'
        messages = clean_chat(chat_path, moderators=moderators)
        sources[key] = {
            'file': chat_path.name,
            'format': 'chat',
            'count': len(messages),
        }
        if messages:
            analysis[key] = analyze_day(messages)
            all_messages.extend(messages)
        print(f"      {chat_path.name}: {len(messages)} сообщений (чат)")

    # Process survey files
    for i, survey_path in enumerate(classified['survey'], 1):
        key = f'survey_{i}' if len(classified['survey']) > 1 else 'survey'
        messages = clean_survey(survey_path)
        # Add sender_id for analyze_day compatibility
        for j, m in enumerate(messages):
            if 'sender_id' not in m:
                m['sender_id'] = f'survey_{j}'
            if 'time' not in m:
                m['time'] = ''
        sources[key] = {
            'file': survey_path.name,
            'format': 'survey',
            'count': len(messages),
        }
        if messages:
            analysis[key] = analyze_day(messages)
            all_messages.extend(messages)
        print(f"      {survey_path.name}: {len(messages)} ответов (анкета)")

    # Process sales files
    for i, sales_path in enumerate(classified['sales'], 1):
        key = f'sales_{i}' if len(classified['sales']) > 1 else 'sales'
        messages = clean_sales(sales_path)
        # Add sender_id for analyze_day compatibility
        for j, m in enumerate(messages):
            if 'sender_id' not in m:
                m['sender_id'] = f'sales_{j}'
            if 'time' not in m:
                m['time'] = ''
        sources[key] = {
            'file': sales_path.name,
            'format': 'sales',
            'count': len(messages),
        }
        if messages:
            analysis[key] = analyze_day(messages)
            all_messages.extend(messages)
        print(f"      {sales_path.name}: {len(messages)} записей (продажи)")

    # Combined analysis if multiple sources
    if len(analysis) > 1 and all_messages:
        analysis['combined'] = analyze_day(all_messages)

    return {
        'meta': meta,
        'sources': sources,
        'analysis': analysis,
        'launch_id': launch_dir.name,
    }


# ──────────────────── CLI: add CSV to launch ────────────────────

def add_csv_to_launch(launch_dir: Path, csv_path: Path):
    """Copy/move a CSV file into a launch folder."""
    import shutil
    if not is_launch_folder(launch_dir):
        print(f"Ошибка: {launch_dir} не является папкой запуска (нет launch.json)")
        sys.exit(1)
    if not csv_path.exists():
        print(f"Файл не найден: {csv_path}")
        sys.exit(1)

    dest = launch_dir / csv_path.name
    shutil.copy2(csv_path, dest)
    fmt = detect_format(dest)
    print(f"Добавлен {csv_path.name} → {launch_dir.name}/ (формат: {fmt})")


# ──────────────────── Output ────────────────────

def save_launch_data(launch_result: dict, output_dir: Path):
    """Save launch analysis data as JSON."""
    data_dir = output_dir / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)

    launch_id = launch_result['launch_id']
    out_path = data_dir / f'{launch_id}.json'

    # Prepare serializable data
    data = {
        'meta': launch_result['meta'],
        'sources': launch_result['sources'],
        'analysis': {},
    }
    for key, analysis in launch_result['analysis'].items():
        data['analysis'][key] = analysis

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return out_path


def print_summary(launch_result: dict):
    """Print summary stats for a launch."""
    meta = launch_result['meta']
    print(f"\n=== {meta.get('name', launch_result['launch_id'])} ===")
    print(f"    Даты: {meta.get('dates', 'N/A')}")

    for key, src in launch_result['sources'].items():
        print(f"    {key}: {src['count']} записей ({src['format']})")

    # Print top jobs from combined or first analysis
    analysis = launch_result['analysis']
    main_key = 'combined' if 'combined' in analysis else next(iter(analysis), None)
    if main_key and main_key in analysis:
        a = analysis[main_key]
        print(f"\n    ТОП-5 Jobs:")
        for j in a.get('jtbd', [])[:5]:
            print(f"      {j['name']}: {j['count']} упоминаний / {j['people']} чел.")

        print(f"\n    ТОП-3 Страхи:")
        for anx in a.get('anxieties', [])[:3]:
            print(f"      {anx['name']}: {anx['count']}")


# ──────────────────── Main modes ────────────────────

def mode_legacy(csv_path: Path):
    """Legacy mode: single CSV → single analysis."""
    print(f"[1/4] Очистка: {csv_path.name}")
    fmt, messages = clean_auto(csv_path)
    print(f"      Формат: {fmt}")
    print(f"      Содержательных сообщений: {len(messages)}")

    if not messages:
        print("Нет содержательных сообщений для анализа.")
        sys.exit(0)

    # Add sender_id if missing (non-chat formats)
    for i, m in enumerate(messages):
        if 'sender_id' not in m:
            m['sender_id'] = f'{fmt}_{i}'
        if 'time' not in m:
            m['time'] = ''

    unique = len(set(m['sender_id'] for m in messages))
    print(f"      Уникальных участников: {unique}")

    print("[2/4] JTBD-анализ...")
    day_data = analyze_day(messages)

    print("[3/4] Сборка HTML-дашборда...")
    html = build_dashboard(day_data)

    output_dir = PROJECT_ROOT / 'output'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / 'dashboard.html'
    output_path.write_text(html, encoding='utf-8')

    print(f"[4/4] Готово!")
    print(f"\nДашборд: {output_path}")

    s = day_data['stats']
    print(f"\n=== СВОДКА ===")
    print(f"Сообщений: {s['total_messages']}, участников: {s['unique_people']}")

    print("\nТОП-5 Jobs:")
    for j in day_data.get('jtbd', [])[:5]:
        print(f"  {j['name']}: {j['count']} упоминаний / {j['people']} чел.")


def mode_single_launch(launch_dir: Path):
    """Process a single launch folder."""
    print(f"[1/3] Обработка запуска: {launch_dir.name}")
    result = process_launch(launch_dir)

    analysis = result['analysis']
    if not analysis:
        print("Нет данных для анализа.")
        sys.exit(0)

    # Build dashboard from available data
    print("[2/3] Сборка HTML-дашборда...")

    # Use chat days for build_dashboard (day1/day2 comparison)
    day1_key = 'chat_day1'
    day2_key = 'chat_day2'

    # If no chat data, use combined or first available
    if day1_key not in analysis:
        main_key = 'combined' if 'combined' in analysis else next(iter(analysis))
        day1_data = analysis[main_key]
        day2_data = None
    else:
        day1_data = analysis[day1_key]
        day2_data = analysis.get(day2_key)

    html = build_dashboard(day1_data, day2_data)

    output_dir = PROJECT_ROOT / 'output'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / 'dashboard.html'
    output_path.write_text(html, encoding='utf-8')

    # Save JSON data
    json_path = save_launch_data(result, output_dir)

    print(f"[3/3] Готово!")
    print(f"\nДашборд: {output_path}")
    print(f"Данные: {json_path}")
    print_summary(result)


def mode_all_launches(input_dir: Path):
    """Process all launch folders under input/."""
    launches = find_launches(input_dir)
    if not launches:
        print(f"Не найдено папок запусков в {input_dir}")
        print("Каждая папка запуска должна содержать launch.json")
        sys.exit(1)

    print(f"Найдено запусков: {len(launches)}")
    print()

    all_results = []
    for launch_dir in launches:
        print(f"── {launch_dir.name} ──")
        result = process_launch(launch_dir)
        all_results.append(result)
        print()

    output_dir = PROJECT_ROOT / 'output'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save individual JSON data for each launch
    for result in all_results:
        save_launch_data(result, output_dir)

    # Build dashboard from first launch with data (or latest)
    # For multi-launch: use last launch as primary
    primary = all_results[-1] if all_results else None
    if primary:
        analysis = primary['analysis']
        day1_key = 'chat_day1'
        day2_key = 'chat_day2'

        if day1_key not in analysis:
            main_key = 'combined' if 'combined' in analysis else next(iter(analysis), None)
            if main_key:
                day1_data = analysis[main_key]
            else:
                day1_data = None
            day2_data = None
        else:
            day1_data = analysis[day1_key]
            day2_data = analysis.get(day2_key)

        if day1_data:
            print("Сборка HTML-дашборда...")
            html = build_dashboard(day1_data, day2_data)
            output_path = output_dir / 'dashboard.html'
            output_path.write_text(html, encoding='utf-8')
            print(f"Дашборд: {output_path}")

    # Print summaries
    print("\n" + "=" * 50)
    for result in all_results:
        print_summary(result)

    data_dir = output_dir / 'data'
    json_files = list(data_dir.glob('*.json'))
    print(f"\nJSON данные: {data_dir}/ ({len(json_files)} файлов)")


# ──────────────────── Entry point ────────────────────

def main():
    if len(sys.argv) < 2 or '--help' in sys.argv or '-h' in sys.argv:
        print("Анализатор аудитории вебинара")
        print()
        print("Использование:")
        print("  python src/run.py input/2026-03-24/     # один запуск")
        print("  python src/run.py input/                # все запуски")
        print("  python src/run.py input/chat.csv        # один CSV (legacy)")
        print("  python src/run.py --add input/2026-03-24/ new.csv  # добавить CSV")
        print()
        print("Результат: output/dashboard.html + output/data/*.json")
        sys.exit(0)

    # --add mode
    if sys.argv[1] == '--add':
        if len(sys.argv) < 4:
            print("Использование: python src/run.py --add <launch_dir> <csv_file>")
            sys.exit(1)
        add_csv_to_launch(Path(sys.argv[2]), Path(sys.argv[3]))
        sys.exit(0)

    target = Path(sys.argv[1])

    if not target.exists():
        print(f"Путь не найден: {target}")
        sys.exit(1)

    # Mode 1: Single CSV file (legacy)
    if target.is_file():
        mode_legacy(target)
        return

    # Mode 2: Launch folder (has launch.json)
    if target.is_dir() and is_launch_folder(target):
        mode_single_launch(target)
        return

    # Mode 3: Root input directory (contains launch subfolders)
    if target.is_dir():
        launches = find_launches(target)
        if launches:
            mode_all_launches(target)
        else:
            # Maybe it's a directory with CSVs but no launch.json?
            csv_files = list(target.glob('*.csv'))
            if csv_files:
                print(f"Папка {target.name} не содержит launch.json")
                print(f"Найдено {len(csv_files)} CSV файлов без метаданных.")
                print(f"Создайте launch.json или укажите конкретный CSV файл.")
            else:
                print(f"В {target} нет ни launch.json, ни CSV файлов.")
            sys.exit(1)
        return

    print(f"Неизвестный тип пути: {target}")
    sys.exit(1)


if __name__ == '__main__':
    main()
