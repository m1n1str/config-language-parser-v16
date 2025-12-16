#!/usr/bin/env python3
"""
Парсер (вариант 16)
Базовая версия: числа, строки, словари, комментарии
"""

import json
import re


class ConfigParser:
    def __init__(self):
        self.text = ""
        self.pos = 0
        self.line = 1
        self.column = 1

    def parse(self, text):
        """Основной метод парсинга"""
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1

        self._skip_whitespace_and_comments()

        if self._peek() != '{':
            raise SyntaxError(f"Ожидалось '{{' в начале конфигурации (строка {self.line}, столбец {self.column})")

        result = self._parse_dict()

        self._skip_whitespace_and_comments()
        if self.pos < len(self.text):
            raise SyntaxError(f"Лишние символы в конце файла: '{self.text[self.pos:]}'")

        return result

    def _parse_dict(self):
        """Парсинг словаря { key => value, ... }"""
        if not self._consume('{'):
            raise SyntaxError(f"Ожидалось '{{' (строка {self.line}, столбец {self.column})")

        result = {}

        self._skip_whitespace_and_comments()

        while self._peek() != '}':
            # Ключ (идентификатор)
            key = self._parse_identifier()

            self._skip_whitespace_and_comments()

            # Стрелка =>
            if not self._consume('=>'):
                raise SyntaxError(f"Ожидалось '=>' после ключа '{key}' (строка {self.line}, столбец {self.column})")

            self._skip_whitespace_and_comments()

            # Значение
            value = self._parse_value()
            result[key] = value

            self._skip_whitespace_and_comments()

            # Запятая или конец
            if self._peek() == ',':
                self._consume(',')
                self._skip_whitespace_and_comments()

        if not self._consume('}'):
            raise SyntaxError(f"Ожидалось '}}' (строка {self.line}, столбец {self.column})")

        return result

    def _parse_identifier(self):
        """Парсинг идентификатора [_a-z]+"""
        start_pos = self.pos

        # Первый символ должен быть _ или буква
        if self.pos < len(self.text) and (self.text[self.pos] == '_' or self.text[self.pos].islower()):
            self.pos += 1
            self.column += 1

            # Остальные символы
            while self.pos < len(self.text) and (
                    self.text[self.pos] == '_' or self.text[self.pos].islower() or self.text[self.pos].isdigit()):
                self.pos += 1
                self.column += 1

            return self.text[start_pos:self.pos]
        else:
            raise SyntaxError(
                f"Ожидался идентификатор (начинается с _ или маленькой буквы) (строка {self.line}, столбец {self.column})")

    def _parse_value(self):
        """Парсинг значения: число, строка или словарь"""
        if self._peek() == '@':
            return self._parse_string()
        elif self._peek() in '+-' or self._peek().isdigit():
            return self._parse_number()
        elif self._peek() == '{':
            return self._parse_dict()
        else:
            raise SyntaxError(
                f"Неизвестное значение, начинается с '{self._peek()}' (строка {self.line}, столбец {self.column})")

    def _parse_string(self):
        """Парсинг строки @"текст" """
        if not self._consume('@"'):
            raise SyntaxError(f"Ожидалось '@\"' (строка {self.line}, столбец {self.column})")

        start_pos = self.pos

        while self.pos < len(self.text) and self.text[self.pos] != '"':
            if self.text[self.pos] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.pos += 1

        if self.pos >= len(self.text):
            raise SyntaxError(f"Незакрытая строка (строка {self.line})")

        value = self.text[start_pos:self.pos]

        if not self._consume('"'):
            raise SyntaxError(f"Ожидалось '\"' в конце строки (строка {self.line}, столбец {self.column})")

        return value

    def _parse_number(self):
        """Парсинг числа [+-]?\d+\.\d+ """
        pattern = r'[+-]?\d+\.\d+'
        match = re.match(pattern, self.text[self.pos:])

        if not match:
            raise SyntaxError(f"Ожидалось число формата [+-]?\d+\.\d+ (строка {self.line}, столбец {self.column})")

        number_str = match.group(0)
        self.pos += len(number_str)
        self.column += len(number_str)

        try:
            return float(number_str)
        except ValueError:
            raise SyntaxError(f"Некорректное число: {number_str} (строка {self.line}, столбец {self.column})")

    def _skip_whitespace_and_comments(self):
        """Пропуск пробелов и комментариев"""
        while self.pos < len(self.text):
            # Пробелы и переводы строк
            if self.text[self.pos] in ' \t\r':
                self.pos += 1
                self.column += 1
            elif self.text[self.pos] == '\n':
                self.pos += 1
                self.line += 1
                self.column = 1

            # Однострочный комментарий C ...
            elif self.text[self.pos] == 'C' and (self.pos + 1 < len(self.text)) and self.text[self.pos + 1] in ' \t':
                self.pos += 2
                self.column += 2
                while self.pos < len(self.text) and self.text[self.pos] != '\n':
                    self.pos += 1
                    self.column += 1

            # Многострочный комментарий --[[ ... ]]
            elif self.pos + 4 <= len(self.text) and self.text[self.pos:self.pos + 4] == '--[[':
                self.pos += 4
                self.column += 4

                while self.pos + 2 <= len(self.text) and self.text[self.pos:self.pos + 2] != ']]':
                    if self.text[self.pos] == '\n':
                        self.line += 1
                        self.column = 1
                    else:
                        self.column += 1
                    self.pos += 1

                if self.pos + 2 > len(self.text):
                    raise SyntaxError("Незакрытый многострочный комментарий")

                self.pos += 2
                self.column += 2
            else:
                break

    def _peek(self, length=1):
        """Посмотреть следующий символ без продвижения"""
        if self.pos + length <= len(self.text):
            return self.text[self.pos:self.pos + length]
        return ''

    def _consume(self, expected):
        """Съесть ожидаемый символ/строку"""
        if self.pos + len(expected) <= len(self.text) and self.text[self.pos:self.pos + len(expected)] == expected:
            for char in expected:
                if char == '\n':
                    self.line += 1
                    self.column = 1
                else:
                    self.column += 1
            self.pos += len(expected)
            return True
        return False


# Тестовая функция
def test_basic():
    """Тест базового функционала"""
    print("=ТЕСТ БАЗОВОГО ПАРСЕРА=")

    parser = ConfigParser()

    # Тест 1: Простой словарь
    test1 = """{ port => 8080.0, host => @"localhost" }"""
    print("Тест 1 - Простой словарь:")
    try:
        result = parser.parse(test1)
        print("Успешно:", json.dumps(result, indent=2, ensure_ascii=False))
    except SyntaxError as e:
        print(f" Ошибка: {e}")

    # Тест 2: С комментариями
    test2 = """C Это комментарий
{
    C Ещё комментарий
    port => 8080.0,
    host => @"server"
}"""
    print("\nТест 2 - С комментариями:")
    try:
        result = parser.parse(test2)
        print("Успешно:", json.dumps(result, indent=2, ensure_ascii=False))
    except SyntaxError as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    test_basic()