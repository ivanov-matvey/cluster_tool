#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import platform
import paramiko
import sys
import os
import platform


from .executors.local import LocalExecutor
from .executors.remote import RemoteExecutor
from .commands.main import MainCommands
from .ui.common import get_ssh_credentials, print_error, print_success, \
    print_info, print_list, get_number


def remote_workflow():
    """SSH-режим."""
    host, user, pwd = get_ssh_credentials()

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(hostname=host, username=user, password=pwd, timeout=10)
    except Exception as exception:
        print_error(f"Не удалось подключиться: {exception}")
        return

    print_success("Успешно подключено")

    executor = RemoteExecutor(client, pwd)
    commands = MainCommands(executor)

    try:
        _run_menu(commands, "удалённый", host)
    finally:
        client.close()
        print_info("Соединение закрыто")


def local_workflow():
    """Локальный режим."""
    if platform.system().lower() != "linux":
        print_error(
            f"Вы выбрали режим «Локально», но текущая ОС не Linux.\n"
            "Запустите этот скрипт на Linux или используйте удалённый режим."
        )
        return

    executor = LocalExecutor()
    commands = MainCommands(executor)
    _run_menu(commands, "локальный")


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
                return None  # клавиша не нажата
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


def _run_menu(commands, mode_name, ras_host=""):
    """Запускает интерактивное меню с управлением стрелками и Enter."""
    actions = (
        "Список кластеров",
        "Список информационных баз",
        "Список рабочих процессов",
        "Список серверов",
        "Список сеансов",
        "Информация об информационной базе",
        "Информация о сервере",
        "Информация о сеансе",
        "Информация о лицензиях сеансов",
        "Создать информационную базу",
        "Удалить информационную базу",
        "Обновить период перезапуска рабочих сеансов",
        "Завершить сеанс",
        "Назад",
    )

    while True:
        choice = menu_with_arrows(f"Меню ({mode_name} режим)", actions)

        # По индексу вызываем методы команд (замена match с строками на индексы)
        if choice == 0:
            commands.show_cluster_list()
        elif choice == 1:
            commands.show_infobase_list()
        elif choice == 2:
            commands.show_process_list()
        elif choice == 3:
            commands.show_server_list()
        elif choice == 4:
            commands.show_session_list()
        elif choice == 5:
            commands.show_infobase_info(ras_host)
        elif choice == 6:
            commands.show_server_info()
        elif choice == 7:
            commands.show_session_info()
        elif choice == 8:
            commands.show_session_licenses_info()
        elif choice == 9:
            commands.create_infobase()
        elif choice == 10:
            commands.delete_infobase()
        elif choice == 11:
            commands.update_session_lifetime()
        elif choice == 12:
            commands.delete_session()
        elif choice == 13:
            break  # Выход из меню

        print("\nНажмите Enter для возврата в меню...")
        input()
