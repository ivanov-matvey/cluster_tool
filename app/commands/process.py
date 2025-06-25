#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ..managers.process import ProcessManager
from ..managers.cluster import ClusterManager
from ..ui.common import select_from_list, print_output


class ProcessCommands:
    """Команды для работы с процессами."""

    def __init__(self, executor):
        self.process_manager = ProcessManager(executor)
        self.cluster_manager = ClusterManager(executor)

    def show_process_list(self):
        """Получает сырой список процессов и вызывает его вывод."""
        clusters = self.cluster_manager.get_cluster_list_parsed()
        cluster = select_from_list(clusters, "cluster")
        if not cluster:
            return

        cluster_uuid = cluster[0]
        out, err = self.process_manager.get_process_list(cluster_uuid)
        print_output(out, err, "Список процессов")
