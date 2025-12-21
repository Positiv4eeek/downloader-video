import os
import flet as ft
from assets.strings import STRINGS  # Импортируем словарь

class AppState:
    def __init__(self, page: ft.Page):
        self.page = page
        self.store = page.client_storage
        
        self.download_path = self.store.get("download_path") or os.path.join(os.path.expanduser("~"), "Downloads")
        self.history = self.store.get("history") or []
        self.theme_mode = self.store.get("theme") or "dark"
        self.proxy_url = self.store.get("proxy_url") or ""
        self.cookies_path = self.store.get("cookies_path") or ""
        
        # Настройка языка (по умолчанию ru)
        self.language = self.store.get("language") or "ru"

    def get_str(self, key):
        """Возвращает строку на текущем языке"""
        return STRINGS.get(self.language, STRINGS["ru"]).get(key, key)

    def set_language(self, lang: str):
        self.language = lang
        self.store.set("language", lang)
        # Мы не вызываем page.update() здесь, так как это требует перерисовки всего UI.
        # Обычно проще перезагрузить приложение или обновить Views вручную.

    # ... (Остальные методы: set_theme, set_download_path, set_proxy, set_cookies_path, history... остаются без изменений) ...
    def set_theme(self, mode: str):
        self.theme_mode = mode
        self.store.set("theme", mode)
        self.page.theme_mode = ft.ThemeMode.DARK if mode == "dark" else ft.ThemeMode.LIGHT
        self.page.bgcolor = "#0F111A" if mode == "dark" else "#F5F5F5"
        self.page.update()

    def set_download_path(self, path: str):
        self.download_path = path
        self.store.set("download_path", path)

    def set_proxy(self, url: str):
        self.proxy_url = url
        self.store.set("proxy_url", url)

    def set_cookies_path(self, path: str):
        self.cookies_path = path
        self.store.set("cookies_path", path)

    def add_history_item(self, item: dict):
        self.history.append(item)
        if len(self.history) > 20:
            self.history.pop(0)
        self.store.set("history", self.history)

    def remove_history_item(self, item: dict):
        if item in self.history:
            self.history.remove(item)
            self.store.set("history", self.history)

    def clear_history(self):
        self.history = []
        self.store.set("history", [])