#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .cluster import ClusterCommands
from .infobase import InfobaseCommands
from .process import ProcessCommands
from .server import ServerCommands
from .session import SessionCommands


class MainCommands:
    """Главный класс, объединяющий все команды."""

    def __init__(self, executor):
        self.cluster_commands = ClusterCommands(executor)
        self.infobase_commands = InfobaseCommands(executor)
        self.process_commands = ProcessCommands(executor)
        self.server_commands = ServerCommands(executor)
        self.session_commands = SessionCommands(executor)

    # Команды для кластеров
    def show_cluster_list(self):
        """Показывает полный вывод rac cluster list."""
        return self.cluster_commands.show_cluster_list()

    def update_session_lifetime(self):
        self.cluster_commands.update_session_lifetime()

    # Команды для инфобаз
    def show_infobases(self):
        """Показывает информационные базы для выбранного кластера."""
        return self.infobase_commands.show_infobases()

    def show_infobase_info(self, ras_host=""):
        """Показывает информацию об инфобазе."""
        return self.infobase_commands.show_infobase_info(ras_host)

    def create_infobase(self):
        """Создает информационную базу."""
        return self.infobase_commands.create_infobase()

    def drop_infobase(self):
        """Удаляет информационную базу."""
        return self.infobase_commands.drop_infobase()

    # Команды для процессов
    def show_processes(self):
        """Показывает процессы для выбранного кластера."""
        return self.process_commands.show_processes()

    # Команды для серверов
    def show_server_info(self):
        """Показывает информацию о рабочем сервере."""
        return self.server_commands.show_server_info()

    # Команды для сеансов
    def show_sessions(self):
        self.session_commands.show_sessions()

    def show_session_info(self, with_licenses=False):
        self.session_commands.show_session_info(with_licenses)

    def terminate_session(self):
        self.session_commands.terminate_session()
