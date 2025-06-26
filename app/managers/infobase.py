#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def _build_create_args(params):
    """Строит аргументы для создания информационной базы."""
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
    """Реализация работы с информационными базами."""

    def __init__(self, executor):
        self.executor = executor

    def get_infobase_list_parsed(self, cluster_uuid):
        """Возвращает обработанный список информационных баз."""
        out, _ = self.executor.run_command(
            f"infobase summary list --cluster={cluster_uuid}"
        )
        return self.executor.parse_infobase(out)

    def get_infobase_list(self, cluster_uuid):
        """Возвращает сырой список информационных баз."""
        out, err = self.executor.run_command(
            f"infobase summary list --cluster={cluster_uuid}"
        )
        return out, err

    def get_infobase_info(self, cluster_uuid, infobase_uuid):
        """Возвращает сырую информацию об информационной базе."""
        out, err = self.executor.run_command(
            f"infobase info --cluster={cluster_uuid} --infobase={infobase_uuid}"
        )
        return out, err

    def create_infobase(self, cluster_uuid, params):
        """Создает информационную базу с заданными параметрами."""
        if params is None:
            print("Создание информационной базы отменено.")
            return None, None  # или выбросить исключение, если нужно

        args = _build_create_args(params)
        out, err = self.executor.run_command(
            f"{args} --cluster={cluster_uuid}"
        )
        return out, err

    def drop_infobase(self, cluster_uuid, infobase_uuid, extra_flags=None):
        """Удаляет информационную базу."""
        if extra_flags is None:
            extra_flags = []

        args = [f"infobase drop --cluster={cluster_uuid} --infobase={infobase_uuid}"] + extra_flags
        out, err = self.executor.run_command(" ".join(args))
        return out, err
