#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
from .base import BaseExecutor
from ..config import PATH_RAC


class LocalExecutor(BaseExecutor):
    """Исполнитель для локальных команд rac."""

    def check_rac_exists(self):
        return os.path.isfile(PATH_RAC)

    def run_command(self, rac_args, ras_address=""):
        """
        Выполняет локальную команду rac и возвращает (stdout, stderr).
        Запускается без sudo — если требуется, запусти скрипт под sudo.
        """
        if not self.check_rac_exists():
            return "", f"rac не найден по пути {PATH_RAC}"

        ras_part = f"{ras_address} " if ras_address else ""
        cmd = f"{PATH_RAC} {ras_part}{rac_args}"

        result = subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return result.stdout.decode(), result.stderr.decode()
