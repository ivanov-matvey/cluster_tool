#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class ProcessManager:
    """Реализация работы с процессами."""

    def __init__(self, executor):
        self.executor = executor

    def get_process_list_parsed(self, cluster_uuid):
        """Возвращает обработанный список процессов."""
        out, _ = self.executor.run_command(
            f"process list --cluster={cluster_uuid}")
        return self.executor.parse_process(out)

    def get_process_list(self, cluster_uuid):
        """Возвращает сырой список процессов."""
        out, err = self.executor.run_command(
            f"process list --cluster={cluster_uuid}")
        return out, err
