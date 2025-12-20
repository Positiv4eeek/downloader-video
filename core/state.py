import os
import flet as ft

class AppState:
    def __init__(self, page: ft.Page):
        self.page = page
        self.store = page.client_storage
        
        # Загрузка или значения по умолчанию
        self.download_path = self.store.get("download_path") or os.path.join(os.path.expanduser("~"), "Downloads")
        self.history = self.store.get("history") or []
        self.theme_mode = self.store.get("theme") or "dark"

    def set_theme(self, mode: str):
        self.theme_mode = mode
        self.store.set("theme", mode)
        self.page.theme_mode = ft.ThemeMode.DARK if mode == "dark" else ft.ThemeMode.LIGHT
        self.page.bgcolor = "#0F111A" if mode == "dark" else "#F5F5F5"
        self.page.update()

    def set_download_path(self, path: str):
        self.download_path = path
        self.store.set("download_path", path)

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