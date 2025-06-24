#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import platform
import paramiko


from .executors.local import LocalExecutor
from .executors.remote import RemoteExecutor
from .commands.main import MainCommands
from .ui.common import get_ssh_credentials


def remote_workflow():
    """SSH-режим."""
    host, user, pwd = get_ssh_credentials()

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(hostname=host, username=user, password=pwd, timeout=10)
    except Exception as exc:
        print("\nНе удалось подключиться:", exc)
        return

    print("\nУспешно подключено!\n")

    executor = RemoteExecutor(client, pwd)
    commands = MainCommands(executor)

    try:
        _run_menu(commands, "удалённый", host)
    finally:
        client.close()
        print("\nСоединение закрыто.\n")


def local_workflow():
    """Локальный режим."""
    if platform.system().lower() != "linux":
        print(
            "Вы выбрали режим «Локально», но текущая ОС не Linux. "
            "Запустите этот скрипт на Astra Linux или используйте удалённый режим."
        )
        return

    executor = LocalExecutor()
    commands = MainCommands(executor)
    _run_menu(commands, "локальный")


def _run_menu(commands, mode_name, ras_host=""):
    """Запускает интерактивное меню."""
    while True:
        print(
            f"Меню ({mode_name} режим):\n"
            "  1 — Показать список кластеров 1С\n"
            "  2 — Показать информационные базы\n"
            "  3 — Показать рабочие серверы / процессы\n"
            "  4 — Показать информацию о рабочем сервере\n"
            "  5 — Получить информацию об инфобазе\n"
            "  6 — Создать информационную базу\n"
            "  7 — Удалить информационную базу\n"
            "  8 — Показать список сеансов\n"
            "  9 — Информация о сеансах\n"
            "  10 — Информация лицензиях сеансов\n"
            "  11 — Обновить период перезапуска рабочих сеансов\n"
            "  12 — Завершить сессию\n"
            "  0 — Назад"
        )
        choice = input("Ваш выбор: ").strip()

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
