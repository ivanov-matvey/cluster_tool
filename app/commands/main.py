#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .cluster import ClusterCommands
from .infobase import InfobaseCommands
from .process import ProcessCommands
from .server import ServerCommands
from .session import SessionCommands
from .admin import AdminCommands
from ..ui.common import menu_with_arrows_multiple


class MainCommands:
    """Главный класс. Объединяет все команды."""

    def __init__(self, executor):
        self.cluster_commands = ClusterCommands(executor)
        self.infobase_commands = InfobaseCommands(executor)
        self.process_commands = ProcessCommands(executor)
        self.server_commands = ServerCommands(executor)
        self.session_commands = SessionCommands(executor)
        self.admin_commands = AdminCommands()

    # Команды для кластеров
    def show_cluster_list(self):
        """Выводит список кластеров."""
        return self.cluster_commands.show_cluster_list()

    def update_session_lifetime(self):
        """Обновляет период перезапуска рабочих сеансов."""
        self.cluster_commands.update_session_lifetime()


    # Команды для инфобаз
    def show_infobase_list(self):
        """Выводит список информационных баз для выбранного кластера."""
        return self.infobase_commands.show_infobase_list()

    def show_infobase_info(self, ras_host=""):
        """Выводит полную информацию об информационной базе."""
        return self.infobase_commands.show_infobase_info(ras_host)

    def create_infobase(self):
        """Создает информационную базу."""
        return self.infobase_commands.create_infobase()

    def delete_infobase(self):
        """Удаляет информационную базу."""
        return self.infobase_commands.delete_infobase()


    # Команды для процессов
    def show_process_list(self):
        """Выводит полную информацию о процессах для выбранного кластера."""
        return self.process_commands.show_process_list()


    # Команды для серверов
    def show_server_list(self):
        """Выводит полную информацию о серверах."""
        return self.server_commands.show_server_list()

    def show_server_info(self):
        """Выводит полную информацию о рабочем сервере."""
        return self.server_commands.show_server_info()


    # Команды для сеансов
    def show_session_list(self):
        """Выводит список сеансов для выбранного кластера."""
        self.session_commands.show_session_list()

    def show_session_info(self):
        """Выводит полную информацию о сеансе."""
        self.session_commands.show_session_info()

    def show_session_licenses_info(self):
        """Выводит полную информацию о лицензиях сеанса."""
        self.session_commands.show_session_licenses_info()

    def delete_session(self):
        """Удаляет сеанс."""
        self.session_commands.delete_session()


    # Команды для администратора серверов
    def show_admin_information(self):
        """Выводит информацию об администраторе кластеров."""
        self.admin_commands.show_admin_information()

    def update_admin_information(self):
        """Обновляет информацию об администраторе кластеров."""
        self.admin_commands.update_admin_information()


    # Тестовое меню с множественным выбором
    def test_menu(self):
        options = [
            ("1", "Пункт первый"),
            ("2", "Пункт второй"),
            ("3", "Пункт третий"),
            ("4", "Пункт четвертый"),
            ("5", "Пункт пятый"),
        ]
        menu_with_arrows_multiple("Выберите пункт", options)
