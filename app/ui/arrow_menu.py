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
            prefix = "➤ " if i == selected else "  "
            print(f"{prefix}{option}")
        print("\n(Навигация: стрелки ↑↓, Enter — выбрать)")

        key = _get_key()

        if platform.system() == "Windows":
            if key == b'H':  # Стрелка вверх
                selected = (selected - 1) % len(options)
            elif key == b'P':  # Стрелка вниз
                selected = (selected + 1) % len(options)
            elif key == b'\r':  # Enter
                return selected
        else:
            if key == '\x1b[A':  # Стрелка вверх
                selected = (selected - 1) % len(options)
            elif key == '\x1b[B':  # Стрелка вниз
                selected = (selected + 1) % len(options)
            elif key == '\n':  # Enter
                return selected
