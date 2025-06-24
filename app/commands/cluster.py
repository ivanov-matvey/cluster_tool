#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ..managers.cluster import ClusterManager
from ..ui.common import print_output, select_from_list


class ClusterCommands:
    """Команды для работы с кластерами."""

    def __init__(self, executor):
        self.manager = ClusterManager(executor)

    def show_cluster_list(self):
        """Показывает полный вывод rac cluster list."""
        out, err = self.manager.get_cluster_raw_list()
        print_output(out, err, "Список кластеров 1С")

    def update_session_lifetime(self):
        """Обновляет период перезапуска рабочих сеансов."""
        clusters = self.manager.get_clusters()
        cluster = select_from_list(clusters, "кластер")
        if not cluster:
            return

        lifetime = input("Введите период перезапуска рабочих сеансов (мин): ")

        cluster_uuid = cluster[0]
        err = self.manager.update_session_lifetime(cluster_uuid, lifetime)
        out = self.manager.get_cluster(cluster_uuid)
        # СДЕЛАТЬ НОРМАЛЬНЫЙ ВЫВОД
        print_output(out, err, "Обновление периода перезапуска рабочих сеансов")
