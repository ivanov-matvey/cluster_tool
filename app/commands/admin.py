#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ..managers.admin import AdminManager
from ..managers.cluster import ClusterManager
from ..ui.common import print_output, get_string, get_password, print_error, \
    select_from_list


class AdminCommands:
    """Команды для работы с админом."""

    def __init__(self, executor):
        self.admin_manager = AdminManager(executor)
        self.cluster_manager = ClusterManager(executor)

    def show_admin_information(self):
        out = self.admin_manager.get_admin_information()
        err = None
        if out is None:
            err = "Администратор не зарегистрирован."
        print_output(out, err, "Администратор кластеров")


    def show_admin_list(self):
        """Получает сырой список администраторов и вызывает его вывод."""
        clusters = self.cluster_manager.get_cluster_list_parsed()
        cluster = select_from_list(clusters, "cluster")
        if not cluster:
            return

        cluster_uuid = cluster[0]
        out, err = self.admin_manager.get_admin_list(cluster_uuid)
        print_output(out, err, "Список администраторов")


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
            self.admin_manager.update_admin_information(username, password)
        except Exception as e:
            err = str(e)

        result = f"Администратор обновлён: {username}"
        print_output(result, err, "Обновление администратора кластеров")