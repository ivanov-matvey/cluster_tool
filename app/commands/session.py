#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from ..managers.cluster import ClusterManager
from ..managers.session import SessionManager
from ..ui.common import select_from_list, print_output


class SessionCommands:
    """Команды для работы с сессиями."""

    def __init__(self, executor):
        self.session_manager = SessionManager(executor)
        self.cluster_manager = ClusterManager(executor)

    def show_session_list(self):
        """Получает сырой список сеансов и вызывает их вывод."""
        clusters = self.cluster_manager.get_cluster_list_parsed()
        cluster = select_from_list(clusters, "cluster")
        if not cluster:
            return

        cluster_uuid = cluster[0]
        out, err = self.session_manager.get_session_list(cluster_uuid)
        print_output(out, err, "Список сеансов")


    def show_session_info(self):
        """Получает информацию о сеансе и вызывает ее вывод."""
        clusters = self.cluster_manager.get_cluster_list_parsed()
        cluster = select_from_list(clusters, "cluster")
        if not cluster:
            return

        cluster_uuid = cluster[0]
        sessions = self.session_manager.get_session_list_parsed(cluster_uuid)
        session = select_from_list(sessions, "session")
        if not session:
            return

        session_uuid = session[0]
        out, err = self.session_manager.get_session_info(
            cluster_uuid, session_uuid
        )
        print_output(out, err, "Информация о сеансе")

    def show_session_licenses_info(self):
        """Получает информацию о лицензиях сеанса и вызывает ее вывод."""
        clusters = self.cluster_manager.get_cluster_list_parsed()
        cluster = select_from_list(clusters, "cluster")
        if not cluster:
            return

        cluster_uuid = cluster[0]
        sessions = self.session_manager.get_session_list_parsed(cluster_uuid)
        session = select_from_list(sessions, "session")
        if not session:
            return

        session_uuid = session[0]
        out, err = self.session_manager.get_session_licenses_info(
            cluster_uuid, session_uuid
        )
        print_output(out, err, "Информация о лицензиях сеанса")

    def delete_session(self):
        """Завершает сеанс."""
        clusters = self.cluster_manager.get_cluster_list_parsed()
        cluster = select_from_list(clusters, "cluster")
        if not cluster:
            return

        cluster_uuid = cluster[0]
        sessions = self.session_manager.get_session_list_parsed(cluster_uuid)
        session = select_from_list(sessions, "session")
        if not session:
            return

        session_uuid = session[0]
        out, err = self.session_manager.delete_session(cluster_uuid, session_uuid)
        print_output(out, err, "Завершение сеанса")

    def show_session_top(self):
        """Показывает отсортированный список кластеров по количеству сессий."""
        print("\n=== Топ кластеров по количеству сессий ===\n")

        start_total = time.time()

        start_clusters = time.time()
        clusters = self.cluster_manager.get_cluster_list_parsed()
        clusters = [{"uuid": uuid, "name": name, "port": port} for uuid, name, port in clusters]

        elapsed_clusters = time.time() - start_clusters

        start_sessions = time.time()
        for cluster in clusters:
            sessions = self.session_manager.get_session_list_parsed(cluster["uuid"])
            cluster["sessions"] = len(sessions)
        elapsed_sessions = time.time() - start_sessions

        elapsed_total = time.time() - start_total

        sorted_clusters = sorted(clusters, key=lambda c: c["sessions"], reverse=True)

        for cluster in sorted_clusters:
            print(f"{cluster['name']} ({cluster['port']}): {cluster['sessions']} сессий")

        print(f"\nВремя получения кластеров: {elapsed_clusters:.2f} сек.")
        print(f"Время подсчёта сессий: {elapsed_sessions:.2f} сек.")
        print(f"Общее время: {elapsed_total:.2f} сек.")