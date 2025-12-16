#!/usr/bin/env python3
"""
Тесты для парсера конфигураций (вариант 16)
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parser import ConfigParser


def run_test(name, config_text, should_pass=True):
    """Запуск одного теста"""
    print(f"\n{'=' * 60}")
    print(f"ТЕСТ: {name}")
    print(f"{'=' * 60}")

    if not should_pass:
        print("Ожидается ошибка:")

    parser = ConfigParser()

    try:
        result = parser.parse(config_text)
        if should_pass:
            print("✓ Успешно пройден")
            print("Результат:", json.dumps(result, indent=2, ensure_ascii=False))
            return True
        else:
            print("✗ ОШИБКА: Ожидалась ошибка, но парсинг прошёл успешно")
            return False
    except SyntaxError as e:
        if should_pass:
            print(f"✗ ОШИБКА: {e}")
            return False
        else:
            print(f"✓ Ожидаемая ошибка: {e}")
            return True
    except Exception as e:
        print(f"✗ НЕОЖИДАННАЯ ОШИБКА: {e}")
        return False


def test_basic():
    """Базовые тесты"""
    tests = [
        ("Пустой словарь", "{}", True),
        ("Простой словарь", '{ port => 8080.0 }', True),
        ("Несколько пар", '{ a => 1.0, b => 2.0, c => 3.0 }', True),
        ("Строки", '{ name => @"test", value => 10.0 }', True),
        ("Вложенный словарь", '{ server => { port => 80.0 } }', True),
        ("Без закрывающей скобки", '{ port => 8080.0', False),
        ("Без =>", '{ port 8080.0 }', False),
        ("Неправильный идентификатор", '{ Port => 8080.0 }', False),
        ("Идентификатор с цифрами", '{ port_123 => 8080.0 }', True),
        ("Только подчёркивание", '{ _ => 1.0 }', True),
    ]

    print("=== БАЗОВЫЕ ТЕСТЫ ===")
    results = []
    for name, config, should_pass in tests:
        results.append(run_test(name, config, should_pass))

    return all(results)


def test_comments():
    """Тесты комментариев"""
    tests = [
        ("С однострочным комментарием", 'C комментарий\n{ port => 80.0 }', True),
        ("Комментарий в строке", '{ C тут комментарий\nport => 80.0 }', True),
        ("Многострочный комментарий", '--[[ много\nстрочный\nкомментарий ]] { port => 80.0 }', True),
        ("Несколько комментариев", 'C первый\n--[[ второй ]]\n{ x => 1.0 }', True),
    ]

    print("\n=== ТЕСТЫ КОММЕНТАРИЕВ ===")
    results = []
    for name, config, should_pass in tests:
        results.append(run_test(name, config, should_pass))

    return all(results)


def test_constants():
    """Тесты констант"""
    tests = [
        ("Простая константа", '(define port 80.0) { p => $port$ }', True),
        ("Константа-строка", '(define host @"localhost") { h => $host$ }', True),
        ("Несколько констант", '(define a 1.0)(define b 2.0) { sum => $a$, diff => $b$ }', True),
        ("Константа в словаре", '(define port 80.0) { server => { p => $port$ } }', True),
        ("Неопределённая константа", '{ x => $undefined$ }', False),
        ("Константа с подчёркиванием", '(define max_value 100.0) { val => $max_value$ }', True),
        ("Переопределение константы", '(define x 1.0)(define x 2.0) { v => $x$ }', True),
    ]

    print("\n=== ТЕСТЫ КОНСТАНТ ===")
    results = []
    for name, config, should_pass in tests:
        results.append(run_test(name, config, should_pass))

    return all(results)


def test_edge_cases():
    """Крайние случаи"""
    tests = [
        ("Отрицательное число", '{ x => -3.14 }', True),
        ("Положительное число", '{ x => +2.5 }', True),
        ("Сложный идентификатор", '{ _var_name123 => 1.0 }', True),
        ("Много вложенности", '{ a => { b => { c => { d => 1.0 } } } }', True),
        ("Пустая строка", '{ x => @"" }', True),
        ("Строка с кавычкой", '{ x => @"символ \\"кавычки\\"" }', True),
        ("Большое число", '{ x => 999999.999999 }', True),
        ("Ноль", '{ x => 0.0 }', True),
    ]

    print("\n=== КРАЙНИЕ СЛУЧАИ ===")
    results = []
    for name, config, should_pass in tests:
        results.append(run_test(name, config, should_pass))

    return all(results)


def test_real_examples():
    """Тесты реальных примеров из файлов"""
    print("\n=== ТЕСТЫ РЕАЛЬНЫХ ПРИМЕРОВ ===")

    parser = ConfigParser()
    results = []

    # Тест 1: server.conf
    try:
        with open('example_server.conf', 'r', encoding='utf-8') as f:
            server_config = f.read()

        result = parser.parse(server_config)
        print("✓ example_server.conf: Успешно")
        print(f"  Ключи верхнего уровня: {list(result.keys())}")
        results.append(True)
    except Exception as e:
        print(f"✗ example_server.conf: Ошибка - {e}")
        results.append(False)

    # Тест 2: game.conf
    try:
        with open('example_game.conf', 'r', encoding='utf-8') as f:
            game_config = f.read()

        result = parser.parse(game_config)
        print("✓ example_game.conf: Успешно")
        print(f"  Ключи верхнего уровня: {list(result.keys())}")
        results.append(True)
    except Exception as e:
        print(f"✗ example_game.conf: Ошибка - {e}")
        results.append(False)

    # Тест 3: app.conf
    try:
        with open('example_app.conf', 'r', encoding='utf-8') as f:
            app_config = f.read()

        result = parser.parse(app_config)
        print("✓ example_app.conf: Успешно")
        print(f"  Ключи верхнего уровня: {list(result.keys())}")
        results.append(True)
    except Exception as e:
        print(f"✗ example_app.conf: Ошибка - {e}")
        results.append(False)

    return all(results)


def main():
    """Основная функция тестирования"""
    print("ЗАПУСК ТЕСТОВ ДЛЯ ПАРСЕРА КОНФИГУРАЦИЙ (ВАРИАНТ 16)")
    print("=" * 60)

    all_passed = True
    total_tests = 0
    passed_tests = 0

    # Запускаем все тесты
    test_suites = [
        ("Базовые", test_basic),
        ("Комментарии", test_comments),
        ("Константы", test_constants),
        ("Крайние случаи", test_edge_cases),
        ("Реальные примеры", test_real_examples),
    ]

    for suite_name, suite_func in test_suites:
        print(f"\n>>> ЗАПУСК СЮИТЫ: {suite_name}")
        if suite_func():
            passed_tests += 1
        total_tests += 1

    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print(f"Пройдено тестовых наборов: {passed_tests}/{total_tests}")

    if passed_tests == total_tests:
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        return 0
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ!")
        return 1


if __name__ == "__main__":
    sys.exit(main())