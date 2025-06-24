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

    def get_cluster_raw_list(self):
        """Возвращает сырой вывод команды cluster list."""
        out, err = self.executor.run_command("cluster list")
        return out, err