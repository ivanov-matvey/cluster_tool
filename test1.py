#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import paramiko
import getpass
import platform
import subprocess
import os
import re
from typing import List, Tuple, Optional

from config import PATH_RAC


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

def show_process_list(out: str) -> None:
    print("\n===== Рабочие серверы / процессы =====\n")
    print(out or "Процессов не найдено.")

def parse_servers(rac_output: str) -> List[Tuple[str, str]]:
    """
    Разбирает вывод «rac server list …» и возвращает [(uuid, name), …].
    У 1С имя рабочего сервера выводится в поле 'name'.
    """
    servers: List[Tuple[str, str]] = []
    uuid = name = None
    re_uuid = re.compile(r"^(?:server|uuid)\s*:\s*(\S+)", re.I)
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
            servers.append((uuid, name))
            uuid = name = None

    return servers

def collect_infobase_params() -> str:
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

    name = input("Имя ИБ (--name): ").strip()
    dbms = input("Тип СУБД (--dbms): ").strip()
    db_server = input("Сервер БД (--db-server): ").strip()
    db_name = input("Имя БД (--db-name): ").strip()
    locale = input("Локаль (--locale): ").strip()
    db_user = input("Пользователь БД (--db-user): ").strip()
    db_pwd = input("Пароль БД (--db-pwd): ").strip()
    descr = input("Описание (--descr): ").strip()
    date_offset = input("Смещение даты (--date-offset, опционально): ").strip()
    sec_level = input("Уровень безопасности (--security-level, опционально): ").strip()
    sched_deny = input("Блокировка регл. заданий on|off (--scheduled-jobs-deny): ").strip()

    args = [
        "infobase create",
        "--create-database",
        f"--name=\"{name}\"",
        f"--dbms={dbms}",
        f"--db-server={db_server}",
        f"--db-name={db_name}",
        f"--locale={locale}",
        f"--db-user={db_user}",
        f"--db-pwd={db_pwd}",
        f"--descr=\"{descr}\""
    ]

    if date_offset:
        args.append(f"--date-offset={date_offset}")
    if sec_level:
        args.append(f"--security-level={sec_level}")
    if sched_deny in ("on", "off"):
        args.append(f"--scheduled-jobs-deny={sched_deny}")

    return " ".join(args)


def collect_drop_params() -> Tuple[str, str, str, List[str]]:
    print("\nВведите параметры для удаления информационной базы.")
    print("Пример:\n"
          "  Удалить БД (yes/no): yes\n"
          "  Очистить БД (yes/no): no\n")

    drop_db = input("Удалить базу данных (--drop-database)? (yes/no): ").strip().lower()
    clear_db = input("Очистить базу данных (--clear-database)? (yes/no): ").strip().lower()

    extra_args = []
    if drop_db == "yes":
        extra_args.append("--drop-database")
    if clear_db == "yes":
        extra_args.append("--clear-database")

    return extra_args


# ──────────────────────────────────────────────────────────────────────────────
# УДАЛЁННЫЕ КОМАНДЫ (SSH)
# ──────────────────────────────────────────────────────────────────────────────

def _run_remote(
    ssh_client: paramiko.SSHClient,
    sudo_pwd: str,
    rac_args: str,
    ras_address: str = "",   # добавляем параметр с дефолтом пустой строки
) -> Tuple[str, str]:
    ras_part = f"{ras_address} " if ras_address else ""
    cmd = f"sudo -S -p '' {PATH_RAC} {ras_part}{rac_args}"
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

def show_processes_for_cluster_remote(
    ssh_client: paramiko.SSHClient,
    sudo_pwd: str,
    cluster_uuid: str,
) -> None:

    out, err = _run_remote(
        ssh_client,
        sudo_pwd,
        f"process list --cluster={cluster_uuid}",
    )

    if err:
        print("\n===== STDERR =====\n" + err)

    show_process_list(out)

def get_servers_remote(
    ssh_client: paramiko.SSHClient,
    sudo_pwd: str,
    cluster_uuid: str,
) -> List[Tuple[str, str]]:
    """[(uuid, name), …] для выбранного кластера (удалённо)."""
    out, _ = _run_remote(ssh_client, sudo_pwd, f"server list --cluster={cluster_uuid}")
    return parse_servers(out)

def show_server_info_remote(
    ssh_client: paramiko.SSHClient,
    sudo_pwd: str,
    cluster_uuid: str,
    server_uuid: str,
) -> None:
    out, err = _run_remote(
        ssh_client,
        sudo_pwd,
        f"server info --cluster={cluster_uuid} --server={server_uuid}",
    )
    if err:
        print("\n===== STDERR =====\n" + err)
    print("\n===== Информация о рабочем сервере =====\n")
    print(out or "<пустой вывод>")

def show_infobase_info_remote(
    ssh_client: paramiko.SSHClient,
    sudo_pwd: str,
    cluster_uuid: str,
    infobase_uuid: str,
    ras_host: str,  # ← добавляем сюда IP
) -> None:
    ras_address = f"{ras_host}:1545"
    out, err = _run_remote(
        ssh_client,
        sudo_pwd,
        f"infobase summary info --cluster={cluster_uuid} --infobase={infobase_uuid}",
        ras_address=ras_address  # ← передаём как первый аргумент
    )
    if err:
        print("\n===== STDERR =====\n" + err)
    print("\n===== Информация об инфобазе =====\n")
    print(out or "<пустой вывод>")


def create_infobase_remote(ssh_client: paramiko.SSHClient, sudo_pwd: str):
    clusters = get_clusters_remote(ssh_client, sudo_pwd)
    if not clusters:
        print("Кластеры не найдены.")
        return

    print("\nВыберите кластер:")
    for i, (uuid, name) in enumerate(clusters, 1):
        print(f"  {i}) {name} — {uuid}")
    sel = input("\nНомер кластера: ").strip()
    if not sel.isdigit() or not (1 <= int(sel) <= len(clusters)):
        print("Неверный выбор.")
        return

    cluster_uuid = clusters[int(sel) - 1][0]
    args = collect_infobase_params()
    out, err = _run_remote(ssh_client, sudo_pwd, f"{args} --cluster={cluster_uuid}")
    print("\n===== STDOUT =====\n" + out)
    if err:
        print("\n===== STDERR =====\n" + err)


def drop_infobase_remote(ssh_client: paramiko.SSHClient, sudo_pwd: str):
    clusters = get_clusters_remote(ssh_client, sudo_pwd)
    if not clusters:
        print("Кластеры не найдены.")
        return

    print("\nВыберите кластер:")
    for i, (uuid, name) in enumerate(clusters, 1):
        print(f"  {i}) {name} — {uuid}")
    sel = input("Номер кластера: ").strip()
    if not sel.isdigit() or not (1 <= int(sel) <= len(clusters)):
        print("Неверный выбор.")
        return
    cluster_uuid = clusters[int(sel) - 1][0]

    out, _ = _run_remote(ssh_client, sudo_pwd, f"infobase summary list --cluster={cluster_uuid}")
    infobases = parse_infobases(out)
    if not infobases:
        print("Инфобазы не найдены.")
        return

    print("\nВыберите инфобазу:")
    for i, (uuid, name, _) in enumerate(infobases, 1):
        print(f"  {i}) {name} — {uuid}")
    sel_ib = input("Номер инфобазы: ").strip()
    if not sel_ib.isdigit() or not (1 <= int(sel_ib) <= len(infobases)):
        print("Неверный выбор.")
        return
    ib_uuid = infobases[int(sel_ib) - 1][0]

    extra_flags = collect_drop_params()

    args = [
        f"infobase drop --cluster={cluster_uuid} --infobase={ib_uuid}"
    ] + extra_flags

    out, err = _run_remote(ssh_client, sudo_pwd, " ".join(args))
    print("\n===== STDOUT =====\n" + out)
    if err:
        print("\n===== STDERR =====\n" + err)




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

def show_processes_for_cluster_local(cluster_uuid: str) -> None:
    if not check_rac_exists():
        print(f"rac не найден по пути {PATH_RAC}")
        return

    out, err = _run_local(f"process list --cluster={cluster_uuid}")

    if err:
        print("\n===== STDERR =====\n" + err)

    show_process_list(out)

def get_servers_local(cluster_uuid: str) -> List[Tuple[str, str]]:
    if not check_rac_exists():
        return []
    out, _ = _run_local(f"server list --cluster={cluster_uuid}")
    return parse_servers(out)

def show_server_info_local(cluster_uuid: str, server_uuid: str) -> None:
    if not check_rac_exists():
        print(f"rac не найден по пути {PATH_RAC}")
        return
    out, err = _run_local(f"server info --cluster={cluster_uuid} --server={server_uuid}")
    if err:
        print("\n===== STDERR =====\n" + err)
    print("\n===== Информация о рабочем сервере =====\n")
    print(out or "<пустой вывод>")

def show_infobase_info_local(
    cluster_uuid: str,
    infobase_uuid: str,
    ras_host: str = "192.168.91.200",
) -> None:
    if not check_rac_exists():
        print(f"rac не найден по пути {PATH_RAC}")
        return

    cmd = f"infobase info --cluster={cluster_uuid} --infobase={infobase_uuid}"
    if ras_host:
        cmd += f" --ras={ras_host}:1545"

    out, err = _run_local(cmd)
    if err:
        print("\n===== STDERR =====\n" + err)
    print("\n===== Информация об инфобазе =====\n")
    print(out or "<пустой вывод>")



def create_infobase_local():
    if not check_rac_exists():
        print(f"rac не найден по пути {PATH_RAC}")
        return
    clusters = get_clusters_local()
    if not clusters:
        print("Кластеры не найдены.")
        return

    print("\nВыберите кластер:")
    for i, (uuid, name) in enumerate(clusters, 1):
        print(f"  {i}) {name} — {uuid}")
    sel = input("\nНомер кластера: ").strip()
    if not sel.isdigit() or not (1 <= int(sel) <= len(clusters)):
        print("Неверный выбор.")
        return

    cluster_uuid = clusters[int(sel) - 1][0]
    args = collect_infobase_params()
    out, err = _run_local(f"{args} --cluster={cluster_uuid}")
    print("\n===== STDOUT =====\n" + out)
    if err:
        print("\n===== STDERR =====\n" + err)


def drop_infobase_local():
    clusters = get_clusters_local()
    if not clusters:
        print("Кластеры не найдены.")
        return

    print("\nВыберите кластер:")
    for i, (uuid, name) in enumerate(clusters, 1):
        print(f"  {i}) {name} — {uuid}")
    sel = input("Номер кластера: ").strip()
    if not sel.isdigit() or not (1 <= int(sel) <= len(clusters)):
        print("Неверный выбор.")
        return
    cluster_uuid = clusters[int(sel) - 1][0]

    out, _ = _run_local(f"infobase summary list --cluster={cluster_uuid}")
    infobases = parse_infobases(out)
    if not infobases:
        print("Инфобазы не найдены.")
        return

    print("\nВыберите инфобазу:")
    for i, (uuid, name, _) in enumerate(infobases, 1):
        print(f"  {i}) {name} — {uuid}")
    sel_ib = input("Номер инфобазы: ").strip()
    if not sel_ib.isdigit() or not (1 <= int(sel_ib) <= len(infobases)):
        print("Неверный выбор.")
        return
    ib_uuid = infobases[int(sel_ib) - 1][0]

    extra_flags = collect_drop_params()

    args = [
        f"infobase drop --cluster={cluster_uuid} --infobase={ib_uuid}"
    ] + extra_flags

    out, err = _run_local(" ".join(args))
    print("\n===== STDOUT =====\n" + out)
    if err:
        print("\n===== STDERR =====\n" + err)

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
            "  3 — Показать рабочие серверы / процессы\n"
            "  4 — Показать информацию о рабочем сервере\n"
            "  5 — Получить информацию об инфобазе\n"
            "  6 — Создать информационную базу\n"
            "  7 — Удалить информационную базу\n"
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


        elif choice == "3":

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

            show_processes_for_cluster_remote(client, pwd, uuid)

        elif choice == "4":
            clusters = get_clusters_remote(client, pwd)
            if not clusters:
                print("Кластеры не найдены.")
                continue

            print("\nВыберите кластер:")
            for i, (uuid, name) in enumerate(clusters, 1):
                print(f"  {i}) {name} — {uuid}")

            sel = input("\nНомер кластера: ").strip()
            if not sel.isdigit() or not (1 <= int(sel) <= len(clusters)):
                print("Неверный выбор.")
                continue

            cluster_uuid = clusters[int(sel) - 1][0]
            servers = get_servers_remote(client, pwd, cluster_uuid)
            if not servers:
                print("Рабочие серверы не найдены.")
                continue

            print("\nВыберите рабочий сервер:")
            for i, (srv_uuid, srv_name) in enumerate(servers, 1):
                print(f"  {i}) {srv_name} — {srv_uuid}")

            sel_srv = input("\nНомер сервера: ").strip()
            if not sel_srv.isdigit() or not (1 <= int(sel_srv) <= len(servers)):
                print("Неверный выбор.")
                continue

            server_uuid = servers[int(sel_srv) - 1][0]
            show_server_info_remote(client, pwd, cluster_uuid, server_uuid)

        elif choice == "5":
            clusters = get_clusters_remote(client, pwd)
            if not clusters:
                print("Кластеры не найдены.")
                continue

            print("\nВыберите кластер:")
            for i, (uuid, name) in enumerate(clusters, 1):
                print(f"  {i}) {name} — {uuid}")
            sel = input("\nНомер кластера: ").strip()
            if not sel.isdigit() or not (1 <= int(sel) <= len(clusters)):
                print("Неверный выбор.")
                continue

            cluster_uuid = clusters[int(sel) - 1][0]
            out, _ = _run_remote(client, pwd, f"infobase summary list --cluster={cluster_uuid}")
            infobases = parse_infobases(out)
            if not infobases:
                print("Инфобазы не найдены.")
                continue

            print("\nВыберите информационную базу:")
            for i, (uuid, name, _) in enumerate(infobases, 1):
                print(f"  {i}) {name} — {uuid}")
            sel_ib = input("\nНомер инфобазы: ").strip()
            if not sel_ib.isdigit() or not (1 <= int(sel_ib) <= len(infobases)):
                print("Неверный выбор.")
                continue

            infobase_uuid = infobases[int(sel_ib) - 1][0]
            show_infobase_info_remote(client, pwd, cluster_uuid, infobase_uuid, host)

        elif choice == "6":
            create_infobase_remote(client, pwd)

        elif choice == "7":
            drop_infobase_remote(client, pwd)


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
            "  3 — Показать рабочие серверы / процессы\n"
            "  4 — Показать информацию о рабочем сервере\n"
            "  5 — Получить информацию об инфобазе\n"
            "  6 — Создать информационную базу\n"
            "  7 — Удалить информационную базу\n"
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


        elif choice == "3":

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

            show_processes_for_cluster_local(uuid)

        elif choice == "4":
            clusters = get_clusters_local()
            if not clusters:
                print("Кластеры не найдены.")
                continue

            print("\nВыберите кластер:")
            for i, (uuid, name) in enumerate(clusters, 1):
                print(f"  {i}) {name} — {uuid}")

            sel = input("\nНомер кластера: ").strip()
            if not sel.isdigit() or not (1 <= int(sel) <= len(clusters)):
                print("Неверный выбор.")
                continue

            cluster_uuid = clusters[int(sel) - 1][0]
            servers = get_servers_local(cluster_uuid)
            if not servers:
                print("Рабочие серверы не найдены.")
                continue

            print("\nВыберите рабочий сервер:")
            for i, (srv_uuid, srv_name) in enumerate(servers, 1):
                print(f"  {i}) {srv_name} — {srv_uuid}")

            sel_srv = input("\nНомер сервера: ").strip()
            if not sel_srv.isdigit() or not (1 <= int(sel_srv) <= len(servers)):
                print("Неверный выбор.")
                continue

            server_uuid = servers[int(sel_srv) - 1][0]
            show_server_info_local(cluster_uuid, server_uuid)

        elif choice == "5":
            clusters = get_clusters_local()
            if not clusters:
                print("Кластеры не найдены.")
                continue

            print("\nВыберите кластер:")
            for i, (uuid, name) in enumerate(clusters, 1):
                print(f"  {i}) {name} — {uuid}")
            sel = input("\nНомер кластера: ").strip()
            if not sel.isdigit() or not (1 <= int(sel) <= len(clusters)):
                print("Неверный выбор.")
                continue

            cluster_uuid = clusters[int(sel) - 1][0]
            out, _ = _run_local(f"infobase summary list --cluster={cluster_uuid}")
            infobases = parse_infobases(out)
            if not infobases:
                print("Инфобазы не найдены.")
                continue

            print("\nВыберите информационную базу:")
            for i, (uuid, name, _) in enumerate(infobases, 1):
                print(f"  {i}) {name} — {uuid}")
            sel_ib = input("\nНомер инфобазы: ").strip()
            if not sel_ib.isdigit() or not (1 <= int(sel_ib) <= len(infobases)):
                print("Неверный выбор.")
                continue

            infobase_uuid = infobases[int(sel_ib) - 1][0]
            show_infobase_info_local(cluster_uuid, infobase_uuid)

        elif choice == "6":
            create_infobase_local()

        elif choice == "7":
            drop_infobase_local()


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


if __name__ == "__main__.py":
    main()
