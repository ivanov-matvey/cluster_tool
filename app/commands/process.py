#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ..managers.process import ProcessManager
from ..managers.cluster import ClusterManager
from ..ui.common import select_from_list, print_process_list


class ProcessCommands:
    """Команды для работы с процессами."""

    def __init__(self, executor):
        self.process_manager = ProcessManager(executor)

    def show_processes(self):
        """Показывает процессы для выбранного кластера."""
        cluster_manager = ClusterManager(self.process_manager.executor)
        clusters = cluster_manager.get_clusters()
        cluster = select_from_list(clusters, "кластер")
        if not cluster:
            return

        cluster_uuid = cluster[0]
        out, err = self.process_manager.get_processes_raw(cluster_uuid)

        if err:
            print("\n===== STDERR =====\n" + err)

        print_process_list(out)
