#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
from .base import BaseExecutor
from ..config import PATH_1C


class LocalExecutor(BaseExecutor):
    """Исполнитель для локальных команд rac."""

    def __init__(self):
        self.path_rac = self.find_rac_path()

    def find_rac_path(self):
        import os, re
        if not os.path.exists(PATH_1C):
            raise FileNotFoundError(f"Директория {PATH_1C} не найдена")
        versions = [v for v in os.listdir(PATH_1C) if
                    re.fullmatch(r"\d+\.\d+\.\d+\.\d+", v)]
        if not versions:
            raise FileNotFoundError(f"Не найдено версий 1С в директории {PATH_1C}")

        versions.sort(key=lambda v: list(map(int, v.split("."))), reverse=True)
        self.version = versions[0]
        rac_path = os.path.join(PATH_1C, self.version, "rac")

        if not os.path.exists(rac_path):
            raise FileNotFoundError(f"'rac' не найден по пути: {rac_path}")
        return rac_path

    def get_rac_version(self):
        return self.version

    def run_command(self, rac_args, ras_address=""):
        """
        Выполняет локальную команду rac и возвращает (stdout, stderr).
        Запускается без sudo — если требуется, запусти скрипт под sudo.
        """
        ras_part = f"{ras_address} " if ras_address else ""
        cmd = f"{self.path_rac} {ras_part}{rac_args}"

        result = subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return result.stdout.decode(), result.stderr.decode()
