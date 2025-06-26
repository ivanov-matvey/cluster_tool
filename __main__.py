#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .app.ui.common import print_center_text, menu_with_arrows
from .app.workflow import remote_workflow, local_workflow


def main():
    actions = (
        "Удалённо (через SSH)",
        "Локально (на Astra Linux)",
        "Выход",
    )

    while True:
        choice = menu_with_arrows("Добро пожаловать в утилиту управления 1С", actions)

        if choice == 0:
            remote_workflow()
        elif choice == 1:
            local_workflow()
        elif choice == 2:
            print("\nПриложение остановлено.")
            break


if __name__ == "__main__":
    main()
