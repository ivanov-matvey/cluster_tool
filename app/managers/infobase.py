#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from ..config import DEFAULT_RAS_PORT


def _build_create_args(params):
    """Строит аргументы для создания инфобазы."""
    args = [
        "infobase create",
        "--create-database",
        f"--name=\"{params['name']}\"",
        f"--dbms={params['dbms']}",
        f"--db-server={params['db_server']}",
        f"--db-name={params['db_name']}",
        f"--locale={params['locale']}",
        f"--db-user={params['db_user']}",
        f"--db-pwd={params['db_pwd']}",
        f"--descr=\"{params['descr']}\""
    ]

    if params.get('date_offset'):
        args.append(f"--date-offset={params['date_offset']}")
    if params.get('sec_level'):
        args.append(f"--security-level={params['sec_level']}")
    if params.get('sched_deny') in ("on", "off"):
        args.append(f"--scheduled-jobs-deny={params['sched_deny']}")

    return " ".join(args)


class InfobaseManager:
    """Бизнес-логика для работы с инфобазами."""

    def __init__(self, executor):
        self.executor = executor

    def get_infobases(self, cluster_uuid):
        """Возвращает список инфобаз для кластера [(uuid, name, descr), ...]."""
        out, _ = self.executor.run_command(
            f"infobase summary list --cluster={cluster_uuid}")
        return self.executor.parse_infobase(out)

    def get_infobase_info_raw(self, cluster_uuid, infobase_uuid, ras_host=""):
        """Возвращает сырую информацию об инфобазе."""
        ras_address = f"{ras_host}:{DEFAULT_RAS_PORT}" if ras_host else ""
        out, err = self.executor.run_command(
            f"infobase summary info --cluster={cluster_uuid} --infobase={infobase_uuid}",
            ras_address=ras_address
        )
        return out, err

    def create_infobase(self, cluster_uuid, params):
        """Создает инфобазу с заданными параметрами."""
        args = _build_create_args(params)
        out, err = self.executor.run_command(
            f"{args} --cluster={cluster_uuid}")
        return out, err

    def drop_infobase(self, cluster_uuid, infobase_uuid, extra_flags=None):
        """Удаляет инфобазу."""
        if extra_flags is None:
            extra_flags = []

        args = [f"infobase drop --cluster={cluster_uuid} --infobase={infobase_uuid}"] + extra_flags
        out, err = self.executor.run_command(" ".join(args))
        return out, err
