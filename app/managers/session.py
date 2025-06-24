class SessionManager:
    """Бизнес-логика для работы с сессиями."""

    def __init__(self, executor):
        self.executor = executor

    def list_sessions(self, cluster_uuid):
        """Возвращает список сессий."""
        out, _ = self.executor.run_command(f"session list --cluster={cluster_uuid}")
        return self.executor.parse_sessions(out)

    def get_session_info(self, cluster_uuid, session_uuid, licenses=False):
        """Получает информацию о сессии (и лицензиях при необходимости)."""
        extra = " --licenses" if licenses else ""
        out, err = self.executor.run_command(
            f"session info --session={session_uuid} --cluster={cluster_uuid}{extra}"
        )
        return out, err

    def terminate_session(self, cluster_uuid, session_uuid):
        """Завершает указанную сессию."""
        out, err = self.executor.run_command(
            f"session terminate --session={session_uuid} --cluster={cluster_uuid}"
        )
        return out, err
