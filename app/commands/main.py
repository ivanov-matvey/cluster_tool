#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .cluster import ClusterCommands
from .infobase import InfobaseCommands
from .process import ProcessCommands
from .server import ServerCommands
from .session import SessionCommands


class MainCommands:
    """Главный класс. Объединяет все команды."""

    def __init__(self, executor):
        self.cluster_commands = ClusterCommands(executor)
        self.infobase_commands = InfobaseCommands(executor)
        self.process_commands = ProcessCommands(executor)
        self.server_commands = ServerCommands(executor)
        self.session_commands = SessionCommands(executor)

    # Команды для кластеров
    def show_cluster_list(self):
        """Показывает список кластеров."""
        return self.cluster_commands.show_cluster_list()

    def update_session_lifetime(self):
        """Обновляет период перезапуска рабочих сеансов."""
        self.cluster_commands.update_session_lifetime()


    # Команды для инфобаз
    def show_infobase_list(self):
        """Показывает список информационных баз для выбранного кластера."""
        return self.infobase_commands.show_infobase_list()

    def show_infobase_info(self, ras_host=""):
        """Показывает полную информацию об информационной базе."""
        return self.infobase_commands.show_infobase_info(ras_host)

    def create_infobase(self):
        """Создает информационную базу."""
        return self.infobase_commands.create_infobase()

    def delete_infobase(self):
        """Удаляет информационную базу."""
        return self.infobase_commands.delete_infobase()


    # Команды для процессов
    def show_process_list(self):
        """Показывает полную информацию о процессах для выбранного кластера."""
        return self.process_commands.show_process_list()

    def show_process_info(self):
        """Показывает полную информацию о процессе."""
        # TODO: Реализовать функцию
        pass


    # Команды для серверов
    def show_server_list(self):
        """Показывает список серверов для выбранного кластера"""
        # TODO: Реализовать функцию
        pass

    def show_server_info(self):
        """Показывает полную информацию о рабочем сервере."""
        return self.server_commands.show_server_info()


    # Команды для сеансов
    def show_session_list(self):
        """Показывает список сеансов для выбранного кластера."""
        self.session_commands.show_session_list()

    def show_session_info(self, with_licenses=False):
        """Показывает полную информацию о сеансе."""
        self.session_commands.show_session_info(with_licenses)

    def delete_session(self):
        """Удаляет сеанс."""
        self.session_commands.delete_session()
