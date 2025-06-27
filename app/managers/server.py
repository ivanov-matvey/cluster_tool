#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .admin import AdminManager


class ServerManager:
    """Реализация работы с серверами."""

    def __init__(self, executor):
        self.executor = executor
        admin_manager = AdminManager()
        user, pwd = admin_manager.get_admin_information()
        print(user, pwd)
        self.auth_string = f"--cluster-user={user} --cluster-pwd={pwd}"

    def get_server_list_parsed(self, cluster_uuid):
        """Возвращает сырой список серверов."""
        out, _ = self.executor.run_command(
            f"server list --cluster={cluster_uuid} {self.auth_string}")
        return self.executor.parse_server(out)

    def get_server_list(self, cluster_uuid):
        """Возвращает сырой список серверов."""
        out, err = self.executor.run_command(
            f"server list --cluster={cluster_uuid} {self.auth_string}")
        return out, err

    def get_server_info(self, cluster_uuid, server_uuid):
        """Возвращает информацию о сервере."""
        out, err = self.executor.run_command(
            f"server info --cluster={cluster_uuid} --server={server_uuid} {self.auth_string}"
        )
        return out, err
