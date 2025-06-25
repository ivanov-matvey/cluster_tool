#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import platform
import paramiko

from .executors.local import LocalExecutor
from .executors.remote import RemoteExecutor
from .commands.main import MainCommands
from .ui.common import get_ssh_credentials, print_error, print_success, \
    print_info, print_list, get_value


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


def _run_menu(commands, mode_name, ras_host=""):
    """Запускает интерактивное меню."""
    actions = (
        "Показать список кластеров",
        "Показать список информационных баз",
        "Показать рабочие процессы",
        "Показать информацию о рабочем сервере",
        "Показать информацию об информационной базе",
        "Создать информационную базу",
        "Удалить информационную базу"
        "Показать список сеансов",
        "Информация о сеансах",
        "Информация лицензиях сеансов",
        "Обновить период перезапуска рабочих сеансов",
        "Завершить сеанс",
        "Назад"
    )

    while True:
        print_list(f"Меню ({mode_name} режим)", actions)
        choice = get_value("Ваш выбор")

        match choice:
            case "1":
                commands.show_cluster_list()
            case "2":
                commands.show_infobases()
            case "3":
                commands.show_processes()
            case "4":
                commands.show_server_info()
            case "5":
                commands.show_infobase_info(ras_host)
            case "6":
                commands.create_infobase()
            case "7":
                commands.drop_infobase()
            case "8":
                commands.show_sessions()
            case "9":
                commands.show_session_info()
            case "10":
                commands.show_session_info(with_licenses=True)
            case "11":
                commands.update_session_lifetime()
            case "12":
                commands.terminate_session()
            case "0":
                break
            case _:
                print("Некорректный ввод. Попробуйте снова.\n")
