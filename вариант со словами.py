import paramiko
import getpass
import platform
import subprocess
import os
from typing import Optional

PATH_RAC = "/opt/1cv8/x86_64/8.3.25.1286/rac"  # базовый путь к rac


# -----------------------------------------------------------------------------
# Утилиты
# -----------------------------------------------------------------------------

def check_rac_exists() -> bool:
    """Проверяет, существует ли бинарь rac по стандартному пути."""
    return os.path.isfile(PATH_RAC)


def normalize_choice(raw: str) -> str:
    """Приводит ввод пользователя к унифицированному действию."""
    choice = raw.strip().lower()
    mapping = {
        # list clusters
        "1": "list", "list": "list", "clusters": "list", "cluster list": "list",
        "список": "list", "список кластеров": "list",
        # back/exit
        "0": "back", "exit": "back", "back": "back", "назад": "back", "выход": "back",
    }
    return mapping.get(choice, "")


# -----------------------------------------------------------------------------
# Удалённый режим (SSH на другой сервер)
# -----------------------------------------------------------------------------

def execute_cluster_list_remote(ssh_client: paramiko.SSHClient, sudo_password: str) -> None:
    """Запускает `rac cluster list` через sudo на удалённом сервере."""
    command = f"sudo -S -p '' {PATH_RAC} cluster list"

    stdin, stdout, stderr = ssh_client.exec_command(command, get_pty=True)
    stdin.write(sudo_password + "\n")
    stdin.flush()

    out = stdout.read().decode()
    err = stderr.read().decode()

    print("\n===== Результат выполнения команды =====\n")
    print(out if out else "<пустой вывод>")
    if err:
        print("\n===== STDERR =====\n" + err)


def remote_workflow() -> None:
    """Оркестр логики подключения по SSH и выполнения команд."""
    print("\n*** Подключение к серверу 1С по SSH ***\n")
    host = input("IP-адрес сервера: ").strip()
    user = input("Имя пользователя (логин): ").strip()

    try:
        password = getpass.getpass("Пароль: ")
    except Exception:
        password = input("Пароль (будет видно): ")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(hostname=host, username=user, password=password, timeout=10)
    except Exception as exc:
        print("\nНе удалось подключиться:", exc)
        return

    print("\nУспешно подключено!\n")

    while True:
        print(
            "Меню (удалённый режим):\n"
            "  1 / список — Показать список кластеров 1С\n"
            "  0 / назад  — Назад"
        )
        raw = input("Ваш выбор: ")
        action = normalize_choice(raw)

        if action == "list":
            execute_cluster_list_remote(client, password)
        elif action == "back":
            break
        else:
            print("Некорректный ввод. Попробуйте снова.\n")

    client.close()
    print("\nСоединение закрыто.\n")


# -----------------------------------------------------------------------------
# Локальный режим (выполнение на текущем компьютере)
# -----------------------------------------------------------------------------

def execute_cluster_list_local() -> None:
    """Выполняет команду rac cluster list локально (без sudo)."""
    if not check_rac_exists():
        print(f"rac не найден по пути {PATH_RAC}. Установите пакет 1С или исправьте путь.")
        return

    cmd = f"{PATH_RAC} cluster list"
    proc = subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    print("\n===== Результат выполнения команды =====\n")
    print(proc.stdout.decode() or "<пустой вывод>")
    if proc.stderr:
        print("\n===== STDERR =====\n" + proc.stderr.decode())


def local_workflow() -> None:
    """Оркестр логики локального выполнения."""
    if platform.system().lower() != "linux":
        print(
            "Вы выбрали режим \"Локально\", но текущая система не Linux. "
            "Запустите этот скрипт на Astra Linux или выберите режим \"Продолжить здесь\"."
        )
        return

    while True:
        print(
            "Меню (локальный режим):\n"
            "  1 / список — Показать список кластеров 1С\n"
            "  0 / назад  — Назад"
        )
        raw = input("Ваш выбор: ")
        action = normalize_choice(raw)

        if action == "list":
            execute_cluster_list_local()
        elif action == "back":
            break
        else:
            print("Некорректный ввод. Попробуйте снова.\n")


# -----------------------------------------------------------------------------
# Точка входа
# -----------------------------------------------------------------------------

def main() -> None:
    while True:
        print(
            "\n=== Выберите режим работы ===\n"
            "  1 — Продолжить здесь (SSH к удалённому серверу)\n"
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
