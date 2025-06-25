class SessionManager:
    """Бизнес-логика для работы с сессиями."""

    def __init__(self, executor):
        self.executor = executor

    def get_session_list_parsed(self, cluster_uuid):
        """Возвращает обработанный список сессий."""
        out, _ = self.executor.run_command(f"session list --cluster={cluster_uuid}")
        return self.executor.parse_session(out)

    def get_session_list(self, cluster_uuid):
        """Возвращает сырой список сессий."""
        out, err = self.executor.run_command(f"session list --cluster={cluster_uuid}")
        return out, err

    def get_session_info(self, cluster_uuid, session_uuid):
        """Возвращает сырую информацию о сессии."""
        out, err = self.executor.run_command(
            f"session info --session={session_uuid} --cluster={cluster_uuid}"
        )
        return out, err

    def get_session_licenses_info(self, cluster_uuid, session_uuid):
        """Возвращает сырую информацию о лицензиях сессии."""
        out, err = self.executor.run_command(
            f"session info --session={session_uuid} --cluster={cluster_uuid} --licenses"
        )
        return out, err

    def delete_session(self, cluster_uuid, session_uuid):
        """Удаляет сессию."""
        out, err = self.executor.run_command(
            f"session terminate --session={session_uuid} --cluster={cluster_uuid}"
        )
        return out, err
