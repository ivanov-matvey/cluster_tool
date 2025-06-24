#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from abc import ABC, abstractmethod


class BaseExecutor(ABC):
    """Базовый класс для исполнителей команд rac."""

    @abstractmethod
    def run_command(self, rac_args, ras_address=""):
        """Выполняет команду rac и возвращает (stdout, stderr)."""
        pass

    def parse_kv_blocks(self, rac_output, field_patterns, required_fields):
        """
        Универсальный парсер блоков rac-вывода по заданным regex-паттернам.
        field_patterns: список (key, regex) для парсинга строк
        required_fields: список полей, которые должны быть заполнены, чтобы сохранить блок
        """
        regex_map = {key: re.compile(pattern, re.I) for key, pattern in
                     field_patterns}
        current = {key: None for key, _ in field_patterns}
        results = []

        for raw in rac_output.splitlines():
            line = raw.strip()
            if not line:
                continue

            for key, regex in regex_map.items():
                if m := regex.match(line):
                    current[key] = m.group(1).strip()

            if all(current[k] is not None for k in required_fields):
                results.append(tuple(current[k] or "" for k in current))
                current = {key: None for key in current}

        return results

    def parse_cluster(self, rac_output):
        """Разбирает вывод "rac cluster list" и возвращает список (uuid, name)."""
        return self.parse_kv_blocks(
            rac_output,
            field_patterns=[
                ("uuid", r"^(?:cluster|uuid)\s*:\s*(\S+)"),
                ("name", r"^name\s*:\s*\"?(.*?)\"?\s*$"),
            ],
            required_fields=["uuid", "name"],
        )

    def parse_cluster_with_lifetime(self, rac_output):
        """Разбирает вывод "rac cluster list" и возвращает список (uuid, name, lifetime)."""
        return self.parse_kv_blocks(
            rac_output,
            field_patterns=[
                ("uuid", r"^(?:cluster|uuid)\s*:\s*(\S+)"),
                ("name", r"^name\s*:\s*\"?(.*?)\"?\s*$"),
                ("lifetime", r"^lifetime-limit\s*:\s*\"?(.*?)\"?\s*$"),

            ],
            required_fields=["uuid", "name", "lifetime"],
        )

    def parse_infobase(self, rac_output):
        """Разбирает вывод "rac infobase summary list" и возвращает (uuid, name)."""
        return self.parse_kv_blocks(
            rac_output,
            field_patterns=[
                ("uuid", r"^infobase\s*:\s*(\S+)"),
                ("name", r"^name\s*:\s*\"?(.*?)\"?\s*$"),
            ],
            required_fields=["uuid", "name"],
        )

    def parse_server(self, rac_output):
        """Разбирает вывод "rac server list ..." и возвращает [(uuid, name), ...]."""
        return self.parse_kv_blocks(
            rac_output,
            field_patterns=[
                ("uuid", r"^(?:server|uuid)\s*:\s*(\S+)"),
                ("name", r"^name\s*:\s*\"?(.*?)\"?\s*$"),
            ],
            required_fields=["uuid", "name"],
        )

    def parse_sessions(self, rac_output):
        """Разбирает вывод session list и возвращает [(uuid, user-name, host, app_id), ...]."""
        return self.parse_kv_blocks(
            rac_output,
            field_patterns=[
                ("uuid", r"^session\s*:\s*(\S+)"),
                ("user_name", r"^user-name\s*:\s*\"?(.*?)\"?$"),
                ("host", r"^host\s*:\s*\"?(.*?)\"?$"),
                ("app_id", r"^app-id\s*:\s*\"?(.*?)\"?$"),
            ],
            required_fields=["uuid", "user_name", "host", "app_id"],
        )
