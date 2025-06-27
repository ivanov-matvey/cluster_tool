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

    rac_version = None
    if hasattr(commands.executor, "get_rac_version"):
        rac_version = commands.executor.get_rac_version()

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
        "Информация об аккаунте администратора кластеров",
        "Обновить аккаунт администратора кластеров",
        "Тест множественный выбор",
        "Топ по сессиям",
        "Назад",
    )

    while True:
        menu_title = f"Меню ({mode_name} режим) | Версия 1С: {rac_version if rac_version else 'неизвестна'}"
        choice = menu_with_arrows(menu_title, actions)

        match choice:
            case 0:
                commands.show_cluster_list()
            case 1:
                commands.show_infobase_list()
            case 2:
                commands.show_process_list()
            case 3:
                commands.show_server_list()
            case 4:
                commands.show_session_list()
            case 5:
                commands.show_infobase_info()
            case 6:
                commands.show_server_info()
            case 7:
                commands.show_session_info()
            case 8:
                commands.show_session_licenses_info()
            case 9:
                commands.create_infobase()
            case 10:
                commands.delete_infobase()
            case 11:
                commands.update_session_lifetime()
            case 12:
                commands.delete_session()
            case 13:
                commands.show_admin_information()
            case 14:
                commands.update_admin_information()
            case 15:
                commands.test_menu()
            case 16:
                commands.show_session_top()
            case 17:
                break
            case "cansel":
                break

        print("\nНажмите Enter для возврата в меню...")
        input()
