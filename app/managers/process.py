#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .admin import AdminManager


class ProcessManager:
    """Реализация работы с процессами."""

    def __init__(self, executor):
        self.executor = executor
        admin_manager = AdminManager()
        user, pwd = admin_manager.get_admin_information()
        print(user, pwd)
        self.auth_string = f"--cluster-user={user} --cluster-pwd={pwd}"

    def get_process_list_parsed(self, cluster_uuid):
        """Возвращает обработанный список процессов."""
        out, _ = self.executor.run_command(
            f"process list --cluster={cluster_uuid} {self.auth_string}")
        return self.executor.parse_process(out)

    def get_process_list(self, cluster_uuid):
        """Возвращает сырой список процессов."""
        out, err = self.executor.run_command(
            f"process list --cluster={cluster_uuid} {self.auth_string}")
        return out, err
