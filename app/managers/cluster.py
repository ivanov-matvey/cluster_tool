#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class ClusterManager:
    """Реализация работы с кластерами."""

    def __init__(self, executor):
        self.executor = executor

    def get_cluster_list_parsed(self):
        """Возвращает обработанный список кластеров."""
        raw_output, err = self.executor.run_command("cluster list")
        if err:
            return []

        clusters = self.executor.parse_cluster(raw_output)
        result = []
        for uuid, name in clusters:
            port = self.executor._get_cluster_port(uuid)
            result.append((uuid, name, port))
        return result

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
