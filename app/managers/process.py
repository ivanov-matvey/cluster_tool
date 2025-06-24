#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class ProcessManager:
    """Бизнес-логика для работы с процессами."""

    def __init__(self, executor):
        self.executor = executor

    def get_processes_raw(self, cluster_uuid):
        """Возвращает сырой вывод процессов для кластера."""
        out, err = self.executor.run_command(
            f"process list --cluster={cluster_uuid}")
        return out, err
