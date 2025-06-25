#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ..managers.infobase import InfobaseManager
from ..managers.cluster import ClusterManager
from ..ui.common import select_from_list, print_output, \
    collect_create_infobase_params, collect_delete_infobase_params


class InfobaseCommands:
    """Команды для работы с информационными базами."""

    def __init__(self, executor):
        self.infobase_manager = InfobaseManager(executor)
        self.cluster_manager = ClusterManager(executor)


    def show_infobase_list(self):
        """Получает сырой список информационных баз и вызывает его вывод."""
        clusters = self.cluster_manager.get_cluster_list_parsed()
        cluster = select_from_list(clusters, "cluster")
        if not cluster:
            return

        cluster_uuid = cluster[0]
        out, err = self.infobase_manager.get_infobase_list(cluster_uuid)
        print_output(out, err, "Список информационных баз")


    def show_infobase_info(self, ras_host=""):
        """Получает информацию об информационной базе и вызывает ее вывод."""
        clusters = self.cluster_manager.get_cluster_list_parsed()
        cluster = select_from_list(clusters, "cluster")
        if not cluster:
            return

        cluster_uuid = cluster[0]
        infobases = self.infobase_manager.get_infobase_list_parsed(cluster_uuid)
        infobase = select_from_list(infobases, "infobase")
        if not infobase:
            return

        infobase_uuid = infobase[0]
        out, err = self.infobase_manager.get_infobase_info(cluster_uuid,
                                                           infobase_uuid,
                                                           ras_host)
        print_output(out, err, "Информация об информационной базе")


    def create_infobase(self):
        """Создает информационную базу и вызывает вывод результата."""
        clusters = self.cluster_manager.get_cluster_list_parsed()
        cluster = select_from_list(clusters, "cluster")
        if not cluster:
            return

        cluster_uuid = cluster[0]
        params = collect_create_infobase_params()
        out, err = self.infobase_manager.create_infobase(cluster_uuid, params)
        print_output(out, err, "Создание информационной базы")

    def delete_infobase(self):
        """Удаляет информационную базу и вызывает вывод результата."""
        clusters = self.cluster_manager.get_cluster_list_parsed()
        cluster = select_from_list(clusters, "cluster")
        if not cluster:
            return

        cluster_uuid = cluster[0]
        infobases = self.infobase_manager.get_infobase_list_parsed(cluster_uuid)
        infobase = select_from_list(infobases, "infobase")
        if not infobase:
            return

        infobase_uuid = infobase[0]
        extra_flags = collect_delete_infobase_params()
        out, err = self.infobase_manager.drop_infobase(cluster_uuid,
                                                       infobase_uuid,
                                                       extra_flags)
        print_output(out, err, "Удаление информационной базы")
