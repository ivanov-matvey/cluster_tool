#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import getpass


def get_ssh_credentials():
    """Собирает данные для SSH-подключения."""
    print("\n*** Подключение к серверу 1С по SSH ***\n")
    host = input("IP-адрес сервера: ").strip()
    user = input("Имя пользователя (логин): ").strip()

    try:
        pwd = getpass.getpass("Пароль: ")
    except Exception:
        pwd = input("Пароль (будет видно): ")

    return host, user, pwd


def collect_infobase_params():
    """Собирает параметры для создания информационной базы."""
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
        'date_offset': input(
            "Смещение даты (--date-offset, опционально): ").strip(),
        'sec_level': input(
            "Уровень безопасности (--security-level, опционально): ").strip(),
        'sched_deny': input(
            "Блокировка регл. заданий on|off (--scheduled-jobs-deny): ").strip()
    }


def collect_drop_params():
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


def select_from_list(items, item_type="элемент"):
    """Универсальная функция выбора элемента из списка."""
    if not items:
        print(f"{item_type.capitalize()}ы не найдены.")
        return None

    print(f"\nВыберите {item_type}:")
    for i, item in enumerate(items, 1):
        print(f"  {i}) {item[1]} — {item[0]}")  # (uuid, name)

    sel = input(f"\nНомер {item_type}а: ").strip()
    if not sel.isdigit() or not (1 <= int(sel) <= len(items)):
        print("Неверный выбор.")
        return None

    return items[int(sel) - 1]


def print_output(out, err, title="Результат"):
    """Выводит stdout и stderr с заголовком."""
    print(f"\n===== {title} =====\n")
    print(out or "<пустой вывод>")
    if err:
        print("\n===== STDERR =====\n" + err)


def print_infobases(infobases):
    """Выводит список информационных баз."""
    if not infobases:
        print("\nИнформационные базы отсутствуют.\n")
        return

    print("\n===== Информационные базы =====\n")
    for i, (uuid, name, descr) in enumerate(infobases, 1):
        print(f"{i}) {name} — {uuid}")
        print(f"    descr: {descr or '<пусто>'}")


def print_process_list(out):
    """Выводит список процессов."""
    print("\n===== Рабочие серверы / процессы =====\n")
    print(out or "Процессов не найдено.")
