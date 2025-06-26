#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import getpass

import sys
import os
import platform

from ..config import TITLE_LENGTH


ITEM_TYPES = {
    "cluster": {
        "nom": "кластер",    # кто? что?
        "acc": "кластер",    # кого? что?
        "gen": "кластера",   # кого? чего?
        "plural": "кластеры"
    },
    "infobase": {
        "nom": "инфобаза",
        "acc": "инфобазу",
        "gen": "инфобазы",
        "plural": "инфобазы"
    },
    "process": {
        "nom": "процесс",
        "acc": "процесс",
        "gen": "процесса",
        "plural": "процессы"
    },
    "server": {
        "nom": "сервер",
        "acc": "сервер",
        "gen": "сервера",
        "plural": "сервера"
    },
    "session": {
        "nom": "сеанс",
        "acc": "сеанс",
        "gen": "сеанса",
        "plural": "сеансы"
    }
}


def get_ssh_credentials():
    """Собирает данные для SSH-подключения."""
    print_center_text("Подключение к серверу 1С по SSH", TITLE_LENGTH)
    host = input("IP-адрес сервера: ").strip()
    user = input("Имя пользователя (логин): ").strip()

    try:
        pwd = getpass.getpass("Пароль: ")
    except Exception:
        pwd = input("Пароль (будет видно): ")

    return host, user, pwd


def collect_create_infobase_params():
    """Собирает параметры для создания информационной базы с меню выбора."""

    choice = menu_with_arrows(
        "Вы перешли в режим создания информационной базы. Что хотите сделать?",
        ["Продолжить создание", "Назад"]
    )

    if choice == 1:
        print("Выход в главное меню.")
        return None


    print("\nВведите параметры для создания информационной базы.")
    print("Пример заполнения:\n"
          "  Имя ИБ:           MyBase\n"
          "  Тип СУБД:         PostgreSQL\n"
          "  Сервер БД:        localhost\n"
          "  Имя БД:           mybase_db\n"
          "  Локаль:           ru_RU\n"
          "  Пользователь БД:  postgres\n"
          "  Пароль БД:        mysecretpass\n"
          "  Описание:         Тестовая база\n"
          "  Смещение даты:    0 (можно пропустить)\n"
          "  Уровень безопасности: 0 (можно пропустить)\n"
          "  Блокировка регл. заданий: off\n")

    return {
        'name': input("Имя ИБ (--name): ").strip(),
        'dbms': input("Тип СУБД (--dbms): ").strip(),
        'db_server': input("Сервер БД (--db-server): ").strip(),
        'db_name': input("Имя БД (--db-name): ").strip(),
        'locale': input("Локаль (--locale): ").strip(),
        'db_user': input("Пользователь БД (--db-user): ").strip(),
        'db_pwd': input("Пароль БД (--db-pwd): ").strip(),
        'descr': input("Описание (--descr): ").strip(),
        'date_offset': input("Смещение даты (--date-offset, опционально): ").strip(),
        'sec_level': input("Уровень безопасности (--security-level, опционально): ").strip(),
        'sched_deny': input("Блокировка регл. заданий on|off (--scheduled-jobs-deny): ").strip()
    }




def collect_delete_infobase_params():
    """Собирает параметры для удаления информационной базы."""
    print("\nВведите параметры для удаления информационной базы.")
    print("Пример:\n"
          "  Удалить БД (yes/no): yes\n"
          "  Очистить БД (yes/no): no\n")

    drop_db = input(
        "Удалить базу данных (--drop-database)? (yes/no): ").strip().lower()
    clear_db = input(
        "Очистить базу данных (--clear-database)? (yes/no): ").strip().lower()

    extra_args = []
    if drop_db == "yes":
        extra_args.append("--drop-database")
    if clear_db == "yes":
        extra_args.append("--clear-database")

    return extra_args



if platform.system() == "Windows":
    import msvcrt
else:
    import tty
    import termios

def clear_screen():
    os.system("cls" if platform.system() == "Windows" else "clear")

if platform.system() == "Windows":
    import msvcrt
else:
    import tty
    import termios
    import select

def get_key():
    if platform.system() == "Windows":
        key = msvcrt.getch()
        if key == b'\xe0':
            key = msvcrt.getch()
            return key
        return key
    else:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            rlist, _, _ = select.select([fd], [], [], 0.1)
            if rlist:
                first_char = sys.stdin.read(1)
                if first_char == '\x1b':
                    next_two = sys.stdin.read(2)
                    return first_char + next_two
                else:
                    return first_char
            else:
                return None
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def menu_with_arrows(title, options):
    selected = 0
    while True:
        clear_screen()
        print(f"{title}\n")
        for i, option in enumerate(options):
            prefix = "➤ " if i == selected else "  "
            print(f"{prefix}{option}")
        print("\n(Навигация: стрелки ↑↓, Enter — выбрать)")

        key = get_key()

        if platform.system() == "Windows":
            if key == b'H':  # стрелка вверх
                selected = (selected - 1) % len(options)
            elif key == b'P':  # стрелка вниз
                selected = (selected + 1) % len(options)
            elif key == b'\r':  # Enter
                return selected
        else:
            if key == '\x1b[A':  # стрелка вверх
                selected = (selected - 1) % len(options)
            elif key == '\x1b[B':  # стрелка вниз
                selected = (selected + 1) % len(options)
            elif key == '\n':  # Enter
                return selected

def select_from_list(items, item_type_key="cluster"):
    """Универсальная функция выбора элемента из списка с навигацией стрелками."""

    item_type = ITEM_TYPES.get(item_type_key)

    if not items:
        print_error(f"{item_type['plural']} не найдены.")
        return None

    # Формируем список строк для вывода с индексами (например, для читаемости)
    options = [f"{i+1}. {item}" for i, item in enumerate(items)]

    choice = menu_with_arrows(f"Выберите {item_type['acc']}", options)
    # choice — индекс выбранного элемента

    # Проверка не нужна, т.к. menu_with_arrows не выходит за границы
    return items[choice]



def print_output(out, err, title="Результат"):
    """Выводит stdout и stderr с заголовком."""
    print_center_text(title, TITLE_LENGTH)
    print(out or "<пустой вывод>")
    if err:
        print_error(err)


def print_error(message):
    """Выводит сообщение об ошибке."""
    print(f"\n> (x) {message}\n")


def print_success(message):
    """Выводит сообщение об успехе."""
    print(f"\n> (+) {message}\n")


def print_info(message):
    """Выводит информационное сообщение."""
    print(f"\n> (i) {message}\n")


def print_center_text(text, length):
    """Выводит текст по центру с '─' по краям."""
    if length <= len(text):
        print(text)
        return

    total_dashes = length - len(text)
    left_dashes = total_dashes // 2
    right_dashes = total_dashes - left_dashes

    print(f"\n{'-' * left_dashes} {text} {'-' * right_dashes}")


def print_list(title, items):
    print(f"\n{title}:")
    for i, item in enumerate(items, 1):
        if isinstance(item, tuple):
            head = item[0]
            tail = " - ".join(str(x) for x in item[1:])
            print(f"[ {i} ] {head} - {tail}" if tail else f"[ {i} ] {head}")
        else:
            print(f"[ {i} ] {item}")



def get_number(title):
    """Получает от пользователя число и возвращает его."""
    return input(f"{title}: ").strip()
