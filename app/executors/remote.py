#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from .base import BaseExecutor
from ..config import PATH_1C


class RemoteExecutor(BaseExecutor):
    """Исполнитель для удалённых команд rac через SSH."""

    def __init__(self, ssh_client, sudo_pwd):
        self.ssh_client = ssh_client
        self.sudo_pwd = sudo_pwd
        self._rac_path = None

    def _get_latest_1c_version(self):
        """Получает последнюю версию 1С из удалённой директории."""
        try:
            # Выполняет команду для получения списка директорий в PATH_1C
            cmd = f"sudo -S -p '' ls -1 {PATH_1C}"
            stdin, stdout, stderr = self.ssh_client.exec_command(cmd,
                                                                 get_pty=True)
            stdin.write(self.sudo_pwd + "\n")
            stdin.flush()

            output = stdout.read().decode().replace(self.sudo_pwd, "").strip()
            error = stderr.read().decode().strip()

            if error:
                raise Exception(f"Ошибка при получении списка версий: {error}")

            # Фильтрует только директории с версиями (формат: x.x.xx.xxxx)
            version_pattern = r'^\d+\.\d+\.\d+\.\d+$'
            versions = []

            for line in output.split('\n'):
                line = line.strip()
                if re.match(version_pattern, line):
                    versions.append(line)

            if not versions:
                raise Exception(f"Не найдено версий 1С в директории {PATH_1C}")

            # Сортирует версии и берет последнюю
            versions.sort(key=lambda v: [int(x) for x in v.split('.')],
                          reverse=True)
            latest_version = versions[0]

            return latest_version

        except Exception as e:
            raise Exception(f"Не удалось определить последнюю версию 1С: {e}")

    def _get_rac_path(self):
        """Получает путь к rac с учетом последней версии 1С."""
        if self._rac_path is None:
            latest_version = self._get_latest_1c_version()
            self._rac_path = f"{PATH_1C}/{latest_version}/rac"
        return self._rac_path

    def run_command(self, rac_args, ras_address=""):
        """Выполняет удалённую команду rac через SSH и возвращает (stdout, stderr)."""
        rac_path = self._get_rac_path()
        ras_part = f"{ras_address} " if ras_address else ""
        cmd = f"sudo -S -p '' {rac_path} {ras_part}{rac_args}"

        stdin, stdout, stderr = self.ssh_client.exec_command(cmd, get_pty=True)
        stdin.write(self.sudo_pwd + "\n")
        stdin.flush()

        out = stdout.read().decode().replace(self.sudo_pwd, "")
        err = stderr.read().decode()
        return out, err
