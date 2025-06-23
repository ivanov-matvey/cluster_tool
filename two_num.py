#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import paramiko
import getpass
import platform
import subprocess
import os
import re
from typing import List, Tuple, Optional

PATH_RAC = "/opt/1cv8/x86_64/8.3.25.1286/rac"   # базовый путь к rac


# ──────────────────────────────────────────────────────────────────────────────
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ──────────────────────────────────────────────────────────────────────────────

def parse_infobases(rac_output: str) -> List[Tuple[str, str, str]]:
    """
    Возвращает список кортежей (uuid, name, descr).
    Значение descr может быть пустой строкой.
    """
    ibases: List[Tuple[str, str, str]] = []
    uuid = name = descr = None

    re_uuid  = re.compile(r"^infobase\s*:\s*(\S+)", re.I)
    re_name  = re.compile(r"^name\s*:\s*\"?(.*?)\"?\s*$", re.I)
    re_descr = re.compile(r"^descr\s*:\s*\"?(.*?)\"?\s*$", re.I)

    for raw in rac_output.splitlines():
        line = raw.strip()
        if not line:
            continue

        if (m := re_uuid.match(line)):
            uuid = m.group(1).strip()
        elif (m := re_name.match(line)):
            name = m.group(1).strip()
        elif (m := re_descr.match(line)):
            descr = m.group(1).strip()

        # когда собрали все три поля — добавляем и обнуляем
        if uuid and name is not None and descr is not None:
            ibases.append((uuid, name, descr))
            uuid = name = descr = None

    return ibases

def parse_clusters(rac_output: str) -> List[Tuple[str, str]]:
    """
    Разбирает вывод «rac cluster list» и возвращает
    список (uuid, name), устойчивый к пробелам и кавычкам.
    """
    clusters: List[Tuple[str, str]] = []
    uuid: Optional[str] = None
    name: Optional[str] = None

    re_uuid = re.compile(r"^(?:cluster|uuid)\s*:\s*(\S+)", re.I)
    re_name = re.compile(r"^name\s*:\s*\"?(.*?)\"?\s*$", re.I)

    for raw in rac_output.splitlines():
        line = raw.strip()
        if not line:
            continue

        if (m := re_uuid.match(line)):
            uuid = m.group(1).strip()
        elif (m := re_name.match(line)):
            name = m.group(1).strip()

        if uuid and name is not None:
            clusters.append((uuid, name))
            uuid = name = None

    return clusters

# ──────────────────────────────────────────────────────────────────────────────
# УДАЛЁННЫЕ КОМАНДЫ (SSH)
# ──────────────────────────────────────────────────────────────────────────────

def _run_remote(
    ssh_client: paramiko.SSHClient,
    sudo_pwd: str,
    rac_args: str,
) -> Tuple[str, str]:
    """
    Выполняет команду rac на удалённом сервере через sudo
    и возвращает (stdout, stderr).
    """
    cmd = f"sudo -S -p '' {PATH_RAC} {rac_args}"
    stdin, stdout, stderr = ssh_client.exec_command(cmd, get_pty=True)
    stdin.write(sudo_pwd + "\n")
    stdin.flush()

    out = stdout.read().decode().replace(sudo_pwd, "")  # стираем эхо-пароль
    err = stderr.read().decode()
    return out, err


def execute_cluster_list_remote(
    ssh_client: paramiko.SSHClient,
    sudo_pwd: str,
) -> None:
    """Показывает полный вывод rac cluster list (удалённо)."""
    out, err = _run_remote(ssh_client, sudo_pwd, "cluster list")

    print("\n===== Список кластеров 1С =====\n")
    print(out or "<пустой вывод>")
    if err:
        print("\n===== STDERR =====\n" + err)


def get_clusters_remote(
    ssh_client: paramiko.SSHClient,
    sudo_pwd: str,
) -> List[Tuple[str, str]]:
    """Возвращает [(uuid, name), …] для удалённого сервера."""
    out, _ = _run_remote(ssh_client, sudo_pwd, "cluster list")
    return parse_clusters(out)


def show_infobases_for_cluster_remote(
    ssh_client: paramiko.SSHClient,
    sudo_pwd: str,
    cluster_uuid: str,
) -> None:
    out, err = _run_remote(
        ssh_client,
        sudo_pwd,
        f"infobase summary list --cluster={cluster_uuid}",
    )

    if err:
        # сначала ошибки, чтобы их не «потерять»
        print("\n===== STDERR =====\n" + err)

    infobases = parse_infobases(out)

    if not infobases:          # пункт 3: нет инфобаз
        print("\nИнформационные базы отсутствуют.\n")
        return

    print("\n===== Информационные базы =====\n")
    for i, (uuid, name, descr) in enumerate(infobases, 1):
        print(f"{i}) {name} — {uuid}")
        print(f"    descr: {descr or '<пусто>'}")



# ──────────────────────────────────────────────────────────────────────────────
# ЛОКАЛЬНЫЕ КОМАНДЫ
# ──────────────────────────────────────────────────────────────────────────────

def check_rac_exists() -> bool:
    return os.path.isfile(PATH_RAC)


def _run_local(rac_args: str) -> Tuple[str, str]:
    """
    Выполняет локальную команду rac и возвращает (stdout, stderr).
    Запускается **без sudo** — если требуется, запусти скрипт под sudo.
    """
    result = subprocess.run(
        f"{PATH_RAC} {rac_args}",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.decode(), result.stderr.decode()


def execute_cluster_list_local() -> None:
    if not check_rac_exists():
        print(f"rac не найден по пути {PATH_RAC}")
        return

    out, err = _run_local("cluster list")
    print("\n===== Список кластеров 1С =====\n")
    print(out or "<пустой вывод>")
    if err:
        print("\n===== STDERR =====\n" + err)


def get_clusters_local() -> List[Tuple[str, str]]:
    if not check_rac_exists():
        return []
    out, _ = _run_local("cluster list")
    return parse_clusters(out)


def show_infobases_for_cluster_local(cluster_uuid: str) -> None:
    if not check_rac_exists():
        print(f"rac не найден по пути {PATH_RAC}")
        return

    out, err = _run_local(f"infobase summary list --cluster={cluster_uuid}")

    if err:
        print("\n===== STDERR =====\n" + err)

    infobases = parse_infobases(out)

    if not infobases:
        print("\nИнформационные базы отсутствуют.\n")
        return

    print("\n===== Информационные базы =====\n")
    for i, (uuid, name, descr) in enumerate(infobases, 1):
        print(f"{i}) {name} — {uuid}")
        print(f"    descr: {descr or '<пусто>'}")




# ──────────────────────────────────────────────────────────────────────────────
# ORCHESTRATION: REMOTE WORKFLOW
# ──────────────────────────────────────────────────────────────────────────────

def remote_workflow() -> None:
    """SSH-режим."""
    print("\n*** Подключение к серверу 1С по SSH ***\n")
    host = input("IP-адрес сервера: ").strip()
    user = input("Имя пользователя (логин): ").strip()

    try:
        pwd = getpass.getpass("Пароль: ")
    except Exception:
        pwd = input("Пароль (будет видно): ")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(hostname=host, username=user, password=pwd, timeout=10)
    except Exception as exc:
        print("\nНе удалось подключиться:", exc)
        return

    print("\nУспешно подключено!\n")

    while True:
        print(
            "Меню (удалённый режим):\n"
            "  1 — Показать список кластеров 1С\n"
            "  2 — Показать информационные базы\n"
            "  0 — Назад"
        )
        choice = input("Ваш выбор: ").strip()

        if choice == "1":
            execute_cluster_list_remote(client, pwd)

        elif choice == "2":
            clusters = get_clusters_remote(client, pwd)
            if not clusters:
                print("Кластеры не найдены.")
                continue

            print("\nВыберите кластер:")
            for i, (uuid, name) in enumerate(clusters, 1):
                print(f"  {i}) {name} — {uuid}")

            sel = input("\nВведите номер кластера: ").strip()
            if not sel.isdigit() or not (1 <= int(sel) <= len(clusters)):
                print("Неверный выбор.")
                continue

            uuid = clusters[int(sel) - 1][0]
            show_infobases_for_cluster_remote(client, pwd, uuid)

        elif choice == "0":
            break
        else:
            print("Некорректный ввод. Попробуйте снова.\n")

    client.close()
    print("\nСоединение закрыто.\n")


# ──────────────────────────────────────────────────────────────────────────────
# ORCHESTRATION: LOCAL WORKFLOW
# ──────────────────────────────────────────────────────────────────────────────

def local_workflow() -> None:
    """Локальный режим."""
    if platform.system().lower() != "linux":
        print(
            "Вы выбрали режим «Локально», но текущая ОС не Linux. "
            "Запустите этот скрипт на Astra Linux или используйте удалённый режим."
        )
        return

    while True:
        print(
            "Меню (локальный режим):\n"
            "  1 — Показать список кластеров 1С\n"
            "  2 — Показать информационные базы\n"
            "  0 — Назад"
        )
        choice = input("Ваш выбор: ").strip()

        if choice == "1":
            execute_cluster_list_local()

        elif choice == "2":
            clusters = get_clusters_local()
            if not clusters:
                print("Кластеры не найдены.")
                continue

            print("\nВыберите кластер:")
            for i, (uuid, name) in enumerate(clusters, 1):
                print(f"  {i}) {name} — {uuid}")

            sel = input("\nВведите номер кластера: ").strip()
            if not sel.isdigit() or not (1 <= int(sel) <= len(clusters)):
                print("Неверный выбор.")
                continue

            uuid = clusters[int(sel) - 1][0]
            show_infobases_for_cluster_local(uuid)

        elif choice == "0":
            break
        else:
            print("Некорректный ввод. Попробуйте снова.\n")


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    while True:
        print(
            "\n=== Выберите режим работы ===\n"
            "  1 — Подключиться по SSH (удалённо)\n"
            "  2 — Локально (на этой машине)\n"
            "  0 — Выход"
        )
        mode = input("Ваш выбор: ").strip()

        if mode == "1":
            remote_workflow()
        elif mode == "2":
            local_workflow()
        elif mode == "0":
            print("До свидания!")
            break
        else:
            print("Некорректный ввод. Попробуйте снова.\n")


if __name__ == "__main__":
    main()
