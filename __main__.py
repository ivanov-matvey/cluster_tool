#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .app.config import TITLE_LENGTH
from .app.ui.common import print_center_text, print_list
from .app.workflow import remote_workflow, local_workflow


def main():
    """Главное меню."""
    print_center_text("Добро пожаловать в утилиту управления 1С", TITLE_LENGTH)

    actions = (
        "Удалённо (через SSH)",
        "Локально (на Astra Linux)",
        "Выход",
    )

    while True:
        print_list("Выберите режим работы", actions)

        choice = input("Ваш выбор: ").strip()

        if choice == "1":
            remote_workflow()
        elif choice == "2":
            local_workflow()
        elif choice == "0":
            print("\nПриложение остановлено.")
            break
        else:
            print("Некорректный ввод. Попробуйте снова.")


if __name__ == "__main__":
    main()
