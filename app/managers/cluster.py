#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class ClusterManager:
    """Реализация работы с кластерами."""

    def __init__(self, executor):
        self.executor = executor

    def get_cluster_list_parsed(self):
        """Возвращает обработанный список кластеров."""
        out, _ = self.executor.run_command("cluster list")
        return self.executor.parse_cluster(out)

    def get_cluster_list(self):
        """Возвращает сырой список кластеров."""
        out, err = self.executor.run_command("cluster list")
        return out, err

    def get_cluster(self, cluster_uuid):
        """Возвращает сырую информацию о кластере."""
        out, _ = self.executor.run_command(f"cluster info --cluster={cluster_uuid}")
        return self.executor.parse_cluster_with_lifetime(out)

    def update_session_lifetime(self, cluster_uuid, lifetime):
        """Обновляет период перезапуска рабочих сеансов"""
        self.executor.run_command(
            f"cluster update --cluster={cluster_uuid} --lifetime-limit={lifetime}"
        )
