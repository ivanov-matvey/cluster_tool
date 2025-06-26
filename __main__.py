#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .app.ui.common import menu_with_arrows
from .app.workflow import remote_workflow, local_workflow


def main():
    actions = (
        "Удалённо (через SSH)",
        "Локально (на Astra Linux)",
        "Выход",
    )

    while True:
        choice = menu_with_arrows("Добро пожаловать в утилиту управления 1С", actions)

        match choice:
            case 0:
                remote_workflow()
            case 1:
                local_workflow()
            case 2:
                print("\nПриложение остановлено.")
                break


if __name__ == "__main__":
    main()
