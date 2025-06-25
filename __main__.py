#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import platform

from .app.config import TITLE_LENGTH
from .app.ui.common import print_center_text, print_list
from .app.workflow import remote_workflow, local_workflow


if platform.system() == "Windows":
    import msvcrt
else:
    import tty
    import termios

def clear_screen():
    os.system("cls" if platform.system() == "Windows" else "clear")

if platform.system() == "Windows":
    import msvcrt
else:
    import tty
    import termios
    import select

def get_key():
    if platform.system() == "Windows":
        key = msvcrt.getch()
        if key == b'\xe0':
            key = msvcrt.getch()
            return key
        return key
    else:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            rlist, _, _ = select.select([fd], [], [], 0.1)
            if rlist:
                first_char = sys.stdin.read(1)
                if first_char == '\x1b':
                    next_two = sys.stdin.read(2)
                    return first_char + next_two
                else:
                    return first_char
            else:
                return None  # клавиша не нажата
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def menu_with_arrows(title, options):
    selected = 0
    while True:
        clear_screen()
        print_center_text(title, TITLE_LENGTH)
        print()
        for i, option in enumerate(options):
            prefix = "➤ " if i == selected else "  "
            print(f"{prefix}{option}")
        print("\n(Навигация: стрелки ↑↓, Enter — выбрать)")

        key = get_key()

        if platform.system() == "Windows":
            if key == b'H':  # стрелка вверх
                selected = (selected - 1) % len(options)
            elif key == b'P':  # стрелка вниз
                selected = (selected + 1) % len(options)
            elif key == b'\r':  # Enter
                return selected
        else:
            if key == '\x1b[A':  # стрелка вверх
                selected = (selected - 1) % len(options)
            elif key == '\x1b[B':  # стрелка вниз
                selected = (selected + 1) % len(options)
            elif key == '\n':  # Enter
                return selected


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
