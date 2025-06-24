#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class ServerManager:
    """Бизнес-логика для работы с серверами."""

    def __init__(self, executor):
        self.executor = executor

    def get_servers(self, cluster_uuid):
        """Возвращает список серверов для кластера [(uuid, name), ...]."""
        out, _ = self.executor.run_command(
            f"server list --cluster={cluster_uuid}")
        return self.executor.parse_server(out)

    def get_server_info_raw(self, cluster_uuid, server_uuid):
        """Возвращает сырую информацию о сервере."""
        out, err = self.executor.run_command(
            f"server info --cluster={cluster_uuid} --server={server_uuid}"
        )
        return out, err
