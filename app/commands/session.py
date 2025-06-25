from ..managers.cluster import ClusterManager
from ..managers.session import SessionManager
from ..ui.common import select_from_list, print_output


class SessionCommands:
    """Команды для работы с сессиями."""

    def __init__(self, executor):
        self.session_manager = SessionManager(executor)

    def show_session_list(self):
        """Показывает список сессий."""
        cluster_manager = ClusterManager(self.session_manager.executor)
        clusters = cluster_manager.get_clusters()
        cluster = select_from_list(clusters, "кластер")
        if not cluster:
            return

        cluster_uuid = cluster[0]
        sessions = self.session_manager.list_sessions(cluster_uuid)

        if not sessions:
            print("\nНет активных сессий.")
            return

        print("\n===== Сессии =====\n")
        for i, (uuid, user, host, app_id) in enumerate(sessions, 1):
            print(f"{i}) {user} — {uuid}")
            print(f"    Хост: {host or 'n/a'}  Приложение: {app_id or 'n/a'}")

    def show_session_info(self, with_licenses=False):
        """Показывает подробную информацию о сессии."""
        cluster_manager = ClusterManager(self.session_manager.executor)
        clusters = cluster_manager.get_clusters()
        cluster = select_from_list(clusters, "кластер")
        if not cluster:
            return

        cluster_uuid = cluster[0]
        sessions = self.session_manager.list_sessions(cluster_uuid)
        session = select_from_list(sessions, "сессию")
        if not session:
            return

        session_uuid = session[0]
        out, err = self.session_manager.get_session_info(
            cluster_uuid, session_uuid, licenses=with_licenses
        )
        if out.strip() == "":
            out = "Нет лицензий.\n"
        print_output(out, err, "Информация о сессии")

    def delete_session(self):
        """Завершает выбранную сессию."""
        cluster_manager = ClusterManager(self.session_manager.executor)
        clusters = cluster_manager.get_clusters()
        cluster = select_from_list(clusters, "кластер")
        if not cluster:
            return

        cluster_uuid = cluster[0]
        sessions = self.session_manager.list_sessions(cluster_uuid)
        session = select_from_list(sessions, "сессию")
        if not session:
            return

        session_uuid = session[0]
        out, err = self.session_manager.terminate_session(cluster_uuid, session_uuid)
        print_output(out, err, "Завершение сессии")
