#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class ClusterManager:
    """Бизнес-логика для работы с кластерами."""

    def __init__(self, executor):
        self.executor = executor

    def get_clusters(self):
        """Возвращает список кластеров [(uuid, name), ...]."""
        out, _ = self.executor.run_command("cluster list")
        return self.executor.parse_cluster(out)

    def get_cluster(self, cluster_uuid):
        """Возвращает информацию о кластере [(uuid, name), ...]."""
        out, _ = self.executor.run_command(f"cluster info --cluster={cluster_uuid}")
        return self.executor.parse_cluster_with_lifetime(out)

    def get_cluster_raw_list(self):
        """Возвращает сырой вывод команды cluster list."""
        out, err = self.executor.run_command("cluster list")
        return out, err

    def update_session_lifetime(self, cluster_uuid, lifetime):
        """Обновляет период перезапуска рабочих сеансов"""
        self.executor.run_command(
            f"cluster update --cluster={cluster_uuid} --lifetime-limit={lifetime}"
        )
