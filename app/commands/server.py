#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ..managers.cluster import ClusterManager
from ..managers.server import ServerManager
from ..ui.common import select_from_list, print_output


class ServerCommands:
    """Команды для работы с серверами."""

    def __init__(self, executor):
        self.server_manager = ServerManager(executor)

    def show_server_info(self):
        """Показывает информацию о рабочем сервере."""
        cluster_manager = ClusterManager(self.server_manager.executor)
        clusters = cluster_manager.get_clusters()
        cluster = select_from_list(clusters, "кластер")
        if not cluster:
            return

        cluster_uuid = cluster[0]
        servers = self.server_manager.get_servers(cluster_uuid)
        server = select_from_list(servers, "рабочий сервер")
        if not server:
            return

        server_uuid = server[0]
        out, err = self.server_manager.get_server_info_raw(cluster_uuid, server_uuid)
        print_output(out, err, "Информация о рабочем сервере")