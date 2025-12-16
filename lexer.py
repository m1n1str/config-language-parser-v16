
"""
Лексер для варианта 16
Токенизатор разбивает текст на лексемы
"""

import ply.lex as lex

tokens = (
    'NUMBER',
    'STRING',
    'IDENTIFIER',
    'LBRACE',
    'RBRACE',
    'ARROW',
    'COMMA',
    'DEFINE',
    'DOLLAR',
    'LPAREN',
    'RPAREN',
)

t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_ARROW = r'=>'
t_COMMA = r','
t_DOLLAR = r'\$'
t_LPAREN = r'\('
t_RPAREN = r'\)'

def t_NUMBER(t):
    r'[+-]?\d+\.\d+'
    try:
        t.value = float(t.value)
    except ValueError:
        print(f"Ошибка преобразования числа: {t.value}")
        t.value = 0.0
    return t

def t_STRING(t):
    r'@"[^"]*"'
    t.value = t.value[2:-1]
    return t

def t_IDENTIFIER(t):
    r'[_a-z]+'
    return t

def t_DEFINE(t):
    r'define'
    return t

def t_COMMENT_SINGLE(t):
    r'C\s+[^\n]*'
    pass

def t_COMMENT_MULTI(t):
    r'--\[\[[\s\S]*?\]\]'
    pass

t_ignore = ' \t\r'

def t_error(t):
    print(f"Неизвестный символ: '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()

if __name__ == '__main__':
    test_data = """{ port => 8080.0 }"""
    lexer.input(test_data)
    for token in lexer:
        print(token)