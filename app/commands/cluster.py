#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ..managers.cluster import ClusterManager
from ..ui.common import print_output


class ClusterCommands:
    """Команды для работы с кластерами."""

    def __init__(self, executor):
        self.manager = ClusterManager(executor)

    def show_cluster_list(self):
        """Показывает полный вывод rac cluster list."""
        out, err = self.manager.get_cluster_raw_list()
        print_output(out, err, "Список кластеров 1С")
