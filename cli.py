#!/usr/bin/env python3
"""
CLI интерфейс для парсера конфигураций (вариант 16)
Вход: файл (--input)
Выход: JSON в stdout
"""

import sys
import json
import argparse
from parser import ConfigParser


def main():
    parser = argparse.ArgumentParser(
        description='Конвертер учебного конфигурационного языка в JSON (вариант 16)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python cli.py --input config.conf
  python cli.py --input server.conf > output.json
        """
    )

    parser.add_argument(
        '--input',
        required=True,
        help='Путь к входному файлу с конфигурацией'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Включить отладочный вывод'
    )

    args = parser.parse_args()

    # Чтение файла
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            config_text = f.read()
    except FileNotFoundError:
        print(f"Ошибка: файл '{args.input}' не найден", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка чтения файла: {e}", file=sys.stderr)
        sys.exit(1)

    # Парсинг
    config_parser = ConfigParser()

    try:
        if args.debug:
            print("=== ОТЛАДОЧНЫЙ РЕЖИМ ===", file=sys.stderr)
            print(f"Файл: {args.input}", file=sys.stderr)
            print(f"Размер: {len(config_text)} символов", file=sys.stderr)

        result = config_parser.parse(config_text)

        # Вывод в формате JSON
        json_output = json.dumps(result, indent=2, ensure_ascii=False)
        print(json_output)

    except SyntaxError as e:
        print(f"Синтаксическая ошибка: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка при обработке: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()