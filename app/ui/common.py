#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import getpass
import platform
import sys
import os

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


def print_output(out, err, title="Результат"):
    """Выводит stdout и stderr с заголовком."""
    print_center_text(title)
    if err:
        print_error(err)
        return
    print(out or "<пустой вывод>")


def print_error(message):
    """Выводит сообщение об ошибке."""
    print(f"\n> (x) {message}\n")


def print_success(message):
    """Выводит сообщение об успехе."""
    print(f"\n> (+) {message}\n")


def print_info(message):
    """Выводит информационное сообщение."""
    print(f"\n> (i) {message}\n")


def print_center_text(text):
    """Выводит текст по центру с '-' по краям."""
    title_length = 80
    if title_length <= len(text):
        print(text)
        return

    total_dashes = title_length - len(text)
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
    """Получает от пользователя число и возвращает его как int."""
    while True:
        val = input(f"{title}: ").strip()
        if val.isdigit():
            return int(val)
        else:
            print("Ошибка: введите целое число.")

def get_string(title):
    """Получает от пользователя непустую строку."""
    while True:
        val = input(f"{title}: ").strip()
        if val:
            return val
        else:
            print("Ошибка: строка не может быть пустой.")

def get_password(title):
    """Получает от пользователя пароль без отображения на экране."""
    while True:
        val = getpass.getpass(f"{title}: ").strip()
        if val:
            return val
        else:
            print("Ошибка: пароль не может быть пустым.")


def get_ssh_credentials():
    """Собирает данные для SSH-подключения."""
    print_center_text("Подключение к серверу 1С по SSH")
    host = input("IP-адрес сервера: ").strip()
    user = input("Имя пользователя (логин): ").strip()

    try:
        pwd = getpass.getpass("Пароль: ")
    except Exception:
        pwd = input("Пароль (будет видно): ")

    return host, user, pwd


def collect_create_infobase_params():
    """Собирает параметры для создания информационной базы с меню выбора."""
    options = [
        "Продолжить создание",
        "Назад"
    ]
    choice = menu_with_arrows("Вы перешли в режим создания информационной базы. Продолжить?", options)

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

    drop_db = input(
        "Удалить базу данных (--drop-database)? (y/n): ").strip().lower()
    clear_db = input(
        "Очистить базу данных (--clear-database)? (y/n): ").strip().lower()

    extra_args = []
    if drop_db in {"y", "Y"}:
        extra_args.append("--drop-database")
    if clear_db in {"y", "Y"}:
        extra_args.append("--clear-database")

    return extra_args


def collect_update_admin_params():
    """Собирает параметры для обновления администратора кластеров."""


def select_from_list(items, item_type_key="cluster"):
    """Универсальная функция выбора элемента из списка с навигацией стрелками."""

    item_type = ITEM_TYPES.get(item_type_key)

    if not items:
        print_error(f"{item_type['plural']} не найдены.")
        return None

    options = [(str(i + 1), *item) for i, item in enumerate(items)]

    choice = menu_with_arrows(f"Выберите {item_type['acc']}", options)
    if choice == "cancel":
        return None

    return items[choice]


if platform.system() == "Windows":
    import msvcrt
else:
    import tty
    import termios
    import select


def _clear_screen():
    os.system("cls" if platform.system() == "Windows" else "clear")


def _get_key():
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
        _clear_screen()
        print_center_text(title)
        for i, option in enumerate(options):
            prefix = "➤" if i == selected else " "
            if isinstance(option, (list, tuple)):
                first, *rest = option
                rest_str = " — ".join(map(str, rest))
                print(f"{prefix} {first}. {rest_str}")
            else:
                print(f"{prefix} {option}")
        print("\n(Навигация: стрелки ↑↓, Enter — выбрать, Backspace — назад)")

        key = _get_key()

        if key in {'\x1b[A', b'H'}:  # Стрелка вверх
            selected = (selected - 1) % len(options)
        elif key in {'\x1b[B', b'P'}:  # Стрелка вниз
            selected = (selected + 1) % len(options)
        elif key in {'\n', b'\r'}:  # Enter
            return selected
        elif key in {b'\x08', b'\x7f', '\x08', '\x7f'}:  # Backspace
            return "cancel"


def menu_with_arrows_multiple(title, options):
    selected = 0
    selected_list = []
    while True:
        _clear_screen()
        print_center_text(title)
        for i, option in enumerate(options):
            prefix = "➤" if i == selected else " "
            is_selected = "[*]" if i in selected_list else "[ ]"
            if isinstance(option, (list, tuple)):
                first, *rest = option
                rest_str = " — ".join(map(str, rest))
                print(f"{prefix} {is_selected} {first}. {rest_str}")
            else:
                print(f"{prefix} {is_selected} {option}")
        print("\n(Навигация: стрелки ↑↓, Пробел — выбрать, Enter — подтвердить выбор, Backspace — назад)")

        key = _get_key()

        if key in {'\x1b[A', b'H'}:  # Стрелка вверх
            selected = (selected - 1) % len(options)
        elif key in {'\x1b[B', b'P'}:  # Стрелка вниз
            selected = (selected + 1) % len(options)
        elif (key in {'\x20', b' '}) and (selected not in selected_list):  # Пробел (поставить выделение)
            selected_list.append(selected)
        elif (key in {'\x20', b' '}) and (selected in selected_list):  # Пробел (снять выделение)
            selected_list.remove(selected)
        elif key in {'\n', b'\r'}:  # Enter
            print(f"Выбраны пункты: {selected_list}")
            return selected_list
        elif key in {b'\x08', b'\x7f', '\x08', '\x7f'}:  # Backspace
            return "cancel"
