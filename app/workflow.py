#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import paramiko
import platform


from .executors.local import LocalExecutor
from .executors.remote import RemoteExecutor
from .commands.main import MainCommands
from .ui.common import get_ssh_credentials, print_error, print_success, \
    print_info, menu_with_arrows


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
        _run_menu(commands, "удалённый")
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


def _run_menu(commands, mode_name):
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
        "Тест множественный выбор",
        "Назад",
    )

    while True:
        choice = menu_with_arrows(f"Меню ({mode_name} режим", actions)

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
            commands.show_infobase_info()
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
            commands.test_menu()
        elif choice == 14:
            break

        print("\nНажмите Enter для возврата в меню...")
        input()
