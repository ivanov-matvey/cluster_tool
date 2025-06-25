#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ..managers.cluster import ClusterManager
from ..managers.server import ServerManager
from ..ui.common import select_from_list, print_output


class ServerCommands:
    """Команды для работы с серверами."""

    def __init__(self, executor):
        self.server_manager = ServerManager(executor)
        self.cluster_manager = ClusterManager(executor)

    def show_server_list(self):
        """Получает обработанный список серверов и вызывает его вывод."""
        clusters = self.cluster_manager.get_cluster_list_parsed()
        cluster = select_from_list(clusters, "cluster")
        if not cluster:
            return

        cluster_uuid = cluster[0]
        out, err = self.server_manager.get_server_list(cluster_uuid)
        print_output(out, err, "Список серверов")

    def show_server_info(self):
        """Получает информацию о сервере и вызывает ее вывод."""
        clusters = self.cluster_manager.get_cluster_list_parsed()
        cluster = select_from_list(clusters, "cluster")
        if not cluster:
            return

        cluster_uuid = cluster[0]
        servers = self.server_manager.get_server_list_parsed(cluster_uuid)
        server = select_from_list(servers, "server")
        if not server:
            return

        server_uuid = server[0]
        out, err = self.server_manager.get_server_info(cluster_uuid, server_uuid)
        print_output(out, err, "Информация о рабочем сервере")
