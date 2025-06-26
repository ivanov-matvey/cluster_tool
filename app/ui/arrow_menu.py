#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import platform
import sys
import os


if platform.system() == "Windows":
    import msvcrt
else:
    import tty
    import termios
    import select


def _clear_screen():
    os.system("cls" if platform.system() == "Windows" else "clear")


def _get_key():
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
                return None
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def menu_with_arrows(title, options):
    selected = 0
    while True:
        _clear_screen()
        print(f"{title}\n")
        for i, option in enumerate(options):
            prefix = "➤" if i == selected else " "
            print(f"{prefix} {option}")
        print("\n(Навигация: стрелки ↑↓, Enter — выбрать)")

        key = _get_key()

        if key in {'\x1b[A', b'H'}:  # Стрелка вверх
            selected = (selected - 1) % len(options)
        elif key in {'\x1b[B', b'P'}:  # Стрелка вниз
            selected = (selected + 1) % len(options)
        elif key in {'\n', b'\r'}:  # Enter
            return selected


def menu_with_arrows_multiple(title, options):
    selected = 0
    selected_list = []
    while True:
        _clear_screen()
        print(f"{title}\n")
        for i, option in enumerate(options):
            prefix = "➤" if i == selected else " "
            is_selected = "[*]" if i in selected_list else "[ ]"
            print(f"{prefix} {is_selected} {option}")
        print("\n(Навигация: стрелки ↑↓, Enter — выбрать)")

        key = _get_key()

        if key in {'\x1b[A', b'H'}:  # Стрелка вверх
            selected = (selected - 1) % len(options)
        elif key in {'\x1b[B', b'P'}:  # Стрелка вниз
            selected = (selected + 1) % len(options)
        elif (key in {'\x20', b' '}) and (selected not in selected_list):  # Пробел (поставить выделение)
            selected_list.append(selected)
        elif (key in {'\x20', b' '}) and (selected in selected_list):  # Пробел (снять выделение)
            selected_list.remove(selected)
        elif key in {'\n', b'\r'}:  # Enter
            print(f"Выбраны пункты: {selected_list}")
            return selected_list
