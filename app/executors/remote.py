#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .base import BaseExecutor
from ..config import PATH_RAC


class RemoteExecutor(BaseExecutor):
    """Исполнитель для удалённых команд rac через SSH."""

    def __init__(self, ssh_client, sudo_pwd):
        self.ssh_client = ssh_client
        self.sudo_pwd = sudo_pwd

    def run_command(self, rac_args, ras_address=""):
        """Выполняет удалённую команду rac через SSH и возвращает (stdout, stderr)."""
        ras_part = f"{ras_address} " if ras_address else ""
        cmd = f"sudo -S -p '' {PATH_RAC} {ras_part}{rac_args}"

        stdin, stdout, stderr = self.ssh_client.exec_command(cmd, get_pty=True)
        stdin.write(self.sudo_pwd + "\n")
        stdin.flush()

        out = stdout.read().decode().replace(self.sudo_pwd, "")
        err = stderr.read().decode()
        return out, err
