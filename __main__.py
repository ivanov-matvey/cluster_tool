#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .app.workflow import remote_workflow, local_workflow


def main():
    """Главная функция - точка входа в приложение."""
    print("Добро пожаловать в утилиту управления 1С!")

    while True:
        print(
            "\nВыберите режим работы:\n"
            "  1 — Удалённо (через SSH)\n"
            "  2 — Локально (на Astra Linux)\n"
            "  0 — Выход"
        )

        choice = input("Ваш выбор: ").strip()

        if choice == "1":
            remote_workflow()
        elif choice == "2":
            local_workflow()
        elif choice == "0":
            print("До свидания!")
            break
        else:
            print("Некорректный ввод. Попробуйте снова.")


if __name__ == "__main__":
    main()
