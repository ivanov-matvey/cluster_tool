#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .admin import AdminManager


class SessionManager:
    """Реализация работы с сессиями."""

    def __init__(self, executor):
        self.executor = executor
        admin_manager = AdminManager(executor)
        user, pwd = admin_manager.get_admin_information()
        print(user, pwd)
        self.auth_string = f"--cluster-user={user} --cluster-pwd={pwd}"

    def get_session_list_parsed(self, cluster_uuid):
        """Возвращает обработанный список сессий."""
        out, _ = self.executor.run_command(
            f"session list --cluster={cluster_uuid} {self.auth_string}"
        )
        return self.executor.parse_session(out)

    def get_session_list(self, cluster_uuid):
        """Возвращает сырой список сессий."""
        out, err = self.executor.run_command(
            f"session list --cluster={cluster_uuid} {self.auth_string}"
        )
        return out, err

    def get_session_info(self, cluster_uuid, session_uuid):
        """Возвращает сырую информацию о сессии."""
        out, err = self.executor.run_command(
            f"session info --session={session_uuid} --cluster={cluster_uuid} {self.auth_string}"
        )
        return out, err

    def get_session_licenses_info(self, cluster_uuid, session_uuid):
        """Возвращает сырую информацию о лицензиях сессии."""
        out, err = self.executor.run_command(
            f"session info --session={session_uuid} --cluster={cluster_uuid} --licenses {self.auth_string}"
        )
        return out, err

    def delete_session(self, cluster_uuid, session_uuid):
        """Удаляет сессию."""
        out, err = self.executor.run_command(
            f"session terminate --session={session_uuid} --cluster={cluster_uuid} {self.auth_string}"
        )
        return out, err
