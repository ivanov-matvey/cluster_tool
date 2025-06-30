#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ..managers.admin import AdminManager
from ..ui.common import print_output, get_string, get_password, print_error


class AdminCommands:
    """Команды для работы с админом."""

    def __init__(self):
        self.manager = AdminManager()

    def show_admin_information(self):
        out = self.manager.get_admin_information()
        err = None
        if out is None:
            err = "Администратор не зарегистрирован."
        print_output(out, err, "Администратор кластеров")

    def update_admin_information(self):
        username = get_string("Введите логин")

        password = ""
        password_confirmed = False
        while not password_confirmed:
            password = get_password("Введите пароль")
            password_confirm = get_password("Подтвердите пароль")
            if password == password_confirm:
                password_confirmed = True
            else:
                print_error("Пароли должны совпадать")

        err = None
        try:
            self.manager.update_admin_information(username, password)
        except Exception as e:
            err = str(e)

        out = self.manager.get_admin_information()
        print_output(out, err, "Обновление администратора кластеров")
