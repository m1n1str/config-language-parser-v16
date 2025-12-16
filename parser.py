#!/usr/bin/env python3
"""
Парсер для учебного конфигурационного языка (вариант 16)
Полная версия с поддержкой констант и обработкой ошибок
"""

import json
import re


class ConfigParser:
    def __init__(self):
        self.constants = {}

    def parse(self, text):
        """Основной метод парсинга"""
        # 1. Собираем константы
        self._extract_constants(text)

        # 2. Удаляем комментарии
        text = self._remove_comments_safe(text)

        # 3. Удаляем define из текста
        text = re.sub(r'\(define[^)]+\)', '', text)

        # 4. Парсим основной словарь
        result = self._parse_main_dict(text)

        return result

    def _remove_comments_safe(self, text):
        """Удаляем комментарии, но не внутри строк"""
        result = []
        i = 0
        in_string = False

        while i < len(text):
            # Проверяем начало строки @"
            if text[i:i + 2] == '@"' and not in_string:
                in_string = True
                result.append(text[i])
                i += 1
                continue

            # Конец строки
            if text[i] == '"' and in_string:
                in_string = False

            # Комментарии только вне строк
            if not in_string:
                # Однострочный комментарий C
                if text[i] == 'C' and (i + 1 < len(text)) and text[i + 1] in ' \t\n':
                    # Пропускаем до конца строки
                    while i < len(text) and text[i] != '\n':
                        i += 1
                    continue

                # Многострочный комментарий --[[
                if text[i:i + 4] == '--[[':
                    # Пропускаем до ]]
                    i += 4
                    while i < len(text) and text[i:i + 2] != ']]':
                        i += 1
                    i += 2  # Пропускаем ]]
                    continue

            result.append(text[i])
            i += 1

        return ''.join(result)

    def _extract_constants(self, text):
        """Извлекаем константы (define ...)"""
        self.constants = {}

        i = 0
        while i < len(text):
            if text[i:i + 7] == '(define':
                i += 7

                # Пропускаем пробелы
                while i < len(text) and text[i] in ' \t\n\r':
                    i += 1

                # Имя константы
                name_start = i
                while i < len(text) and (text[i].isalpha() or text[i] == '_' or text[i].isdigit()):
                    i += 1
                const_name = text[name_start:i]

                if not const_name or not re.match(r'^[_a-z][_a-z0-9]*$', const_name):
                    raise SyntaxError(f"Неправильное имя константы: {const_name}")

                # Пропускаем пробелы
                while i < len(text) and text[i] in ' \t\n\r':
                    i += 1

                # Значение константы
                value_start = i

                # Строка
                if text[i:i + 2] == '@"':
                    i += 2
                    while i < len(text) and text[i] != '"':
                        i += 1
                    const_value = text[value_start + 2:i]
                    i += 1  # Пропускаем "

                # Число
                else:
                    start_num = i
                    if text[i] in '+-':
                        i += 1

                    while i < len(text) and (text[i].isdigit() or text[i] == '.'):
                        i += 1

                    num_str = text[start_num:i]
                    if not re.match(r'^[+-]?\d+\.\d+$', num_str):
                        raise SyntaxError(f"Некорректное число в define: {num_str}")

                    const_value = float(num_str)

                # Сохраняем константу
                self.constants[const_name] = const_value

                # Ищем закрывающую скобку
                while i < len(text) and text[i] != ')':
                    i += 1
                i += 1
            else:
                i += 1

    def _parse_main_dict(self, text):
        """Парсим основной словарь"""
        # Ищем первый словарь { ... }
        start = text.find('{')
        if start == -1:
            return {}

        # Находим парную закрывающую скобку
        depth = 0
        end = start

        for i in range(start, len(text)):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break

        if depth != 0:
            raise SyntaxError("Непарные фигурные скобки")

        dict_text = text[start:end]
        return self._parse_dict(dict_text)

    def _parse_dict(self, text):
        """Парсим словарь"""
        if not text or text[0] != '{' or text[-1] != '}':
            return {}

        content = text[1:-1].strip()
        if not content:
            return {}

        result = {}
        i = 0

        while i < len(content):
            # Пропускаем пробелы
            while i < len(content) and content[i] in ' \t\n\r':
                i += 1

            if i >= len(content):
                break

            # Ключ
            key_start = i
            while i < len(content) and (content[i].isalpha() or content[i] == '_' or content[i].isdigit()):
                i += 1
            key = content[key_start:i]

            if not key:
                # Если пустой ключ, пропускаем
                i += 1
                continue

            # Проверяем ключ
            if not re.match(r'^[_a-z][_a-z0-9]*$', key):
                raise SyntaxError(f"Неправильный идентификатор: {key}")

            # Пропускаем пробелы
            while i < len(content) and content[i] in ' \t\n\r':
                i += 1

            # Проверяем =>
            if i + 2 > len(content) or content[i:i + 2] != '=>':
                raise SyntaxError(f"Ожидалось => после ключа {key}")
            i += 2

            # Пропускаем пробелы
            while i < len(content) and content[i] in ' \t\n\r':
                i += 1

            # Значение
            value_start = i

            # Константа
            if content[i] == '$':
                i += 1
                const_start = i
                while i < len(content) and content[i] != '$':
                    i += 1
                const_name = content[const_start:i]

                if i >= len(content):
                    raise SyntaxError(f"Незакрытая константа: ${const_name}")

                if const_name not in self.constants:
                    raise SyntaxError(f"Неопределённая константа: ${const_name}$")

                value = self.constants[const_name]
                i += 1  # Пропускаем $

            # Строка
            elif content[i:i + 2] == '@"':
                i += 2
                str_start = i
                while i < len(content) and content[i] != '"':
                    i += 1

                if i >= len(content):
                    raise SyntaxError("Незакрытая строка")

                value = content[str_start:i]
                i += 1  # Пропускаем "

            # Словарь
            elif content[i] == '{':
                depth = 1
                dict_start = i
                i += 1

                while i < len(content) and depth > 0:
                    if content[i] == '{':
                        depth += 1
                    elif content[i] == '}':
                        depth -= 1
                    i += 1

                if depth > 0:
                    raise SyntaxError("Непарные фигурные скобки")

                dict_text = content[dict_start:i]
                value = self._parse_dict(dict_text)

            # Число или true/false
            else:
                val_start = i
                while i < len(content) and content[i] not in ',}':
                    i += 1

                val_str = content[val_start:i].strip()

                # Булевы значения
                if val_str == 'true':
                    value = True
                elif val_str == 'false':
                    value = False
                # Число
                elif re.match(r'^[+-]?\d+\.\d+$', val_str):
                    value = float(val_str)
                else:
                    raise SyntaxError(f"Непонятное значение: {val_str}")

            # Сохраняем пару
            result[key] = value

            # Пропускаем пробелы
            while i < len(content) and content[i] in ' \t\n\r':
                i += 1

            # Запятая
            if i < len(content) and content[i] == ',':
                i += 1

        return result


# CLI интерфейс
def main_cli():
    """CLI для тестирования"""
    import sys

    if len(sys.argv) < 2:
        print("Использование: python parser.py <файл_конфигурации>")
        print("Пример: python parser.py example_server.conf")
        sys.exit(1)

    filename = sys.argv[1]

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            config_text = f.read()
    except FileNotFoundError:
        print(f"Ошибка: файл '{filename}' не найден")
        sys.exit(1)

    parser = ConfigParser()

    try:
        result = parser.parse(config_text)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except SyntaxError as e:
        print(f"Синтаксическая ошибка: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Тестовый пример
    test_config = """
    (define port 8080.0)
    (define host @"localhost")

    {
        server => {
            port => $port$,
            host => $host$
        }
    }
    """

    parser = ConfigParser()

    try:
        result = parser.parse(test_config)
        print("✅ Тест пройден успешно!")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Ошибка: {e}")

