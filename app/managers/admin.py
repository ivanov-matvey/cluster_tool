#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from cryptography.fernet import Fernet

from ..config import KEY_FILE, CREDENTIALS_FILE


def _load_or_generate_key():
    if os.path.exists(KEY_FILE):
        return open(KEY_FILE, "rb").read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
        return key


class AdminManager:
    def __init__(self, executor):
        self.executor = executor
        self.key = _load_or_generate_key()
        self.cipher = Fernet(self.key)
        user, pwd = self.get_admin_information()
        print(user, pwd)
        self.auth_string = f"--cluster-user={user} --cluster-pwd={pwd}"

    def update_admin_information(self, username, password):
        """Создаёт или обновляет администратора, записывая логин и зашифрованный пароль."""
        encrypted_password = self.cipher.encrypt(password.encode()).decode("utf-8")
        data = {
            "username": username,
            "password": encrypted_password
        }
        with open(CREDENTIALS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)


    def get_admin_list(self, cluster_uuid):
        """Возвращает сырой список администраторов."""
        out, err = self.executor.run_command(
            f"cluster admin list --cluster={cluster_uuid} {self.auth_string}"
        )
        return out, err


    def get_admin_information(self):
        """Читает данные из файла, расшифровывает пароль и возвращает (username, password)."""
        if not os.path.exists(CREDENTIALS_FILE):
            return None
        with open(CREDENTIALS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        username = data.get("username")
        encrypted_password = data.get("password")

        if not username or not encrypted_password:
            return None

        decrypted_password = self.cipher.decrypt(encrypted_password.encode()).decode("utf-8")

        return username, decrypted_password
