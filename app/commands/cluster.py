#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ..managers.cluster import ClusterManager
from ..ui.common import print_output, select_from_list, get_number


class ClusterCommands:
    """Команды для работы с кластерами."""

    def __init__(self, executor):
        self.manager = ClusterManager(executor)

    def show_cluster_list(self):
        """Получает сырой список кластеров и вызывает его вывод."""
        out, err = self.manager.get_cluster_list()
        print_output(out, err, "Список кластеров")

    def update_session_lifetime(self):
        """Обновляет период перезапуска рабочих сеансов
        и вызывает вывод обновленной информации."""
        clusters = self.manager.get_cluster_list_parsed()
        cluster = select_from_list(clusters, "cluster")
        if not cluster:
            return

        lifetime = get_number("Введите период перезапуска рабочих сеансов (мин)")

        cluster_uuid = cluster[0]
        err = self.manager.update_session_lifetime(cluster_uuid, lifetime)
        out = self.manager.get_cluster(cluster_uuid)
        print_output(out, err, "Обновление периода перезапуска рабочих сеансов")
