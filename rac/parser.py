import re

def _parse_kv_blocks(
    rac_output,
    field_patterns,
    required_fields,
):
    """
    Универсальный парсер блоков rac-вывода по заданным regex-паттернам.
    `field_patterns`: список (key, regex) для парсинга строк
    `required_fields`: список полей, которые должны быть заполнены, чтобы сохранить блок
    """
    regex_map = {key: re.compile(pattern, re.I) for key, pattern in field_patterns}
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


def parse_cluster(rac_output):
    """
    Разбирает вывод "rac cluster list" и возвращает список (uuid, name).
    """
    return _parse_kv_blocks(
        rac_output,
        field_patterns=[
            ("uuid", r"^(?:cluster|uuid)\s*:\s*(\S+)"),
            ("name", r"^name\s*:\s*\"?(.*?)\"?\s*$"),
        ],
        required_fields=["uuid", "name"],
    )


def parse_infobase(rac_output):
    """
    Разбирает вывод "rac infobase summary list" и возвращает (uuid, name, descr).
    """
    return _parse_kv_blocks(
        rac_output,
        field_patterns=[
            ("uuid", r"^infobase\s*:\s*(\S+)"),
            ("name", r"^name\s*:\s*\"?(.*?)\"?\s*$"),
            ("descr", r"^descr\s*:\s*\"?(.*?)\"?\s*$"),
        ],
        required_fields=["uuid", "name", "descr"],
    )


def parse_server(rac_output):
    """
    Разбирает вывод "rac server list ..." и возвращает [(uuid, name), ...].
    """
    return _parse_kv_blocks(
        rac_output,
        field_patterns=[
            ("uuid", r"^(?:server|uuid)\s*:\s*(\S+)"),
            ("name", r"^name\s*:\s*\"?(.*?)\"?\s*$"),
        ],
        required_fields=["uuid", "name"],
    )
