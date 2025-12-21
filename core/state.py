import os
import flet as ft
from assets.strings import STRINGS

class AppState:
    def __init__(self, page: ft.Page):
        self.page = page
        self.store = page.client_storage
        
        self.download_path = self.store.get("download_path") or os.path.join(os.path.expanduser("~"), "Downloads")
        self.history = self.store.get("history") or []
        self.theme_mode = self.store.get("theme") or "dark"
        
        # --- Settings ---
        self.monitor_clipboard = self.store.get("monitor_clipboard") or False
        self.embed_meta = self.store.get("embed_meta") or True
        self.download_subs = self.store.get("download_subs") or False
        self.sponsor_block = self.store.get("sponsor_block") or False 
        
        self.language = self.store.get("language") or "ru"
        self._observers = []

    def add_observer(self, func):
        self._observers.append(func)

    def notify_observers(self):
        for func in self._observers:
            func()

    def get_str(self, key):
        return STRINGS.get(self.language, STRINGS["ru"]).get(key, key)

    def set_language(self, lang: str):
        self.language = lang
        self.store.set("language", lang)
        self.notify_observers()

    def set_theme(self, mode: str):
        self.theme_mode = mode
        self.store.set("theme", mode)
        self.page.theme_mode = ft.ThemeMode.DARK if mode == "dark" else ft.ThemeMode.LIGHT
        self.page.bgcolor = "#0F111A" if mode == "dark" else "#F5F5F5"
        self.page.update()

    def set_download_path(self, path: str):
        self.download_path = path
        self.store.set("download_path", path)

    def set_monitor_clipboard(self, value: bool):
        self.monitor_clipboard = value
        self.store.set("monitor_clipboard", value)

    def set_embed_meta(self, value: bool):
        self.embed_meta = value
        self.store.set("embed_meta", value)

    def set_download_subs(self, value: bool):
        self.download_subs = value
        self.store.set("download_subs", value)

    def set_sponsor_block(self, value: bool):
        self.sponsor_block = value
        self.store.set("sponsor_block", value)

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