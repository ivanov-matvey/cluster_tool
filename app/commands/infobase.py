#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ..managers.infobase import InfobaseManager
from ..managers.cluster import ClusterManager
from ..ui.common import select_from_list, print_infobases, print_output, \
    collect_infobase_params, collect_drop_params


class InfobaseCommands:
    """Команды для работы с инфобазами."""

    def __init__(self, executor):
        self.infobase_manager = InfobaseManager(executor)

    def show_infobases(self):
        """Показывает информационные базы для выбранного кластера."""
        cluster_manager = ClusterManager(self.infobase_manager.executor)
        clusters = cluster_manager.get_clusters()
        cluster = select_from_list(clusters, "кластер")
        if not cluster:
            return

        cluster_uuid = cluster[0]
        infobases = self.infobase_manager.get_infobases(cluster_uuid)
        print_infobases(infobases)

    def show_infobase_info(self, ras_host=""):
        """Показывает информацию об инфобазе."""
        cluster_manager = ClusterManager(self.infobase_manager.executor)
        clusters = cluster_manager.get_clusters()
        cluster = select_from_list(clusters, "кластер")
        if not cluster:
            return

        cluster_uuid = cluster[0]
        infobases = self.infobase_manager.get_infobases(cluster_uuid)
        infobase = select_from_list(infobases, "информационная база")
        if not infobase:
            return

        infobase_uuid = infobase[0]
        out, err = self.infobase_manager.get_infobase_info_raw(cluster_uuid,
                                                               infobase_uuid,
                                                               ras_host)
        print_output(out, err, "Информация об инфобазе")

    def create_infobase(self):
        """Создает информационную базу."""
        cluster_manager = ClusterManager(self.infobase_manager.executor)
        clusters = cluster_manager.get_clusters()
        cluster = select_from_list(clusters, "кластер")
        if not cluster:
            return

        cluster_uuid = cluster[0]
        params = collect_infobase_params()
        out, err = self.infobase_manager.create_infobase(cluster_uuid, params)
        print_output(out, err, "Создание инфобазы")

    def drop_infobase(self):
        """Удаляет информационную базу."""
        cluster_manager = ClusterManager(self.infobase_manager.executor)
        clusters = cluster_manager.get_clusters()
        cluster = select_from_list(clusters, "кластер")
        if not cluster:
            return

        cluster_uuid = cluster[0]
        infobases = self.infobase_manager.get_infobases(cluster_uuid)
        infobase = select_from_list(infobases, "информационная база")
        if not infobase:
            return

        infobase_uuid = infobase[0]
        extra_flags = collect_drop_params()
        out, err = self.infobase_manager.drop_infobase(cluster_uuid,
                                                       infobase_uuid,
                                                       extra_flags)
        print_output(out, err, "Удаление инфобазы")
