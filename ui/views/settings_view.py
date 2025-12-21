import flet as ft
import os
from flet import Icons, Colors
from ui.components import SettingTile, StyledTextField

class SettingsView(ft.Column):
    def __init__(self, page: ft.Page, app_state):
        super().__init__()
        self.page = page
        self.app_state = app_state
        self.visible = False
        self.spacing = 10

        self.path_picker = ft.FilePicker(on_result=self.change_path_result)
        self.cookies_picker = ft.FilePicker(on_result=self.change_cookies_result)
        self.page.overlay.extend([self.path_picker, self.cookies_picker])
        
        self.path_display = ft.Text(self.app_state.download_path, size=12, color=Colors.BLUE_GREY_400, max_lines=1, overflow="ellipsis", width=200, text_align="right")
        self.theme_switch = ft.Switch(value=(self.app_state.theme_mode=="dark"), on_change=self.toggle_theme)

        # Выбор языка
        self.lang_dd = ft.Dropdown(
            value=self.app_state.language,
            options=[
                ft.dropdown.Option("ru", "Русский"),
                ft.dropdown.Option("en", "English"),
            ],
            width=120,
            text_size=13,
            border_radius=10,
            content_padding=10,
            on_change=self.change_language
        )

        self.proxy_input = StyledTextField(self.app_state.get_str("proxy_label"), "http://user:pass@ip:port", Icons.VPN_LOCK_ROUNDED, 
                                           on_change=lambda e: self.app_state.set_proxy(e.control.value))
        self.proxy_input.value = self.app_state.proxy_url
        
        self.cookies_display = ft.Text(os.path.basename(self.app_state.cookies_path) if self.app_state.cookies_path else "Not selected", size=12, color=Colors.BLUE_GREY_400, max_lines=1, overflow="ellipsis", width=150, text_align="right")

        self.controls = [
            ft.Text(self.app_state.get_str("settings_title"), size=20, weight="bold"),
            
            SettingTile(Icons.LANGUAGE_ROUNDED, self.app_state.get_str("lang_label"), self.lang_dd),
            SettingTile(Icons.DARK_MODE_ROUNDED, self.app_state.get_str("theme_dark"), self.theme_switch),
            SettingTile(Icons.FOLDER_ROUNDED, self.app_state.get_str("folder_download"), ft.Row([self.path_display, ft.IconButton(Icons.EDIT_ROUNDED, on_click=lambda _: self.path_picker.get_directory_path())])),
            
            ft.Divider(),
            ft.Text("Network & Access", size=16, weight="bold"),
            self.proxy_input,
            SettingTile(Icons.COOKIE_ROUNDED, self.app_state.get_str("cookies_label"), ft.Row([self.cookies_display, ft.IconButton(Icons.UPLOAD_FILE_ROUNDED, on_click=lambda _: self.cookies_picker.pick_files(allow_multiple=False))])),
            
            ft.Divider(),
            SettingTile(Icons.DELETE_SWEEP_ROUNDED, "History", ft.ElevatedButton(self.app_state.get_str("clear_history"), bgcolor=Colors.RED_700, color="white", on_click=self.clear_history)),
        ]

    def change_language(self, e):
        self.app_state.set_language(self.lang_dd.value)
        # Показываем уведомление о необходимости перезагрузки (или перезагружаем сами)
        self.page.snack_bar = ft.SnackBar(ft.Text("Language changed. Please restart app to apply all changes completely."), bgcolor=Colors.ORANGE_700)
        self.page.snack_bar.open = True
        self.page.update()

    def toggle_theme(self, e):
        new_mode = "dark" if self.theme_switch.value else "light"
        self.app_state.set_theme(new_mode)

    def change_path_result(self, e):
        if e.path:
            self.app_state.set_download_path(e.path)
            self.path_display.value = e.path
            self.update()
            
    def change_cookies_result(self, e):
        if e.files:
            path = e.files[0].path
            self.app_state.set_cookies_path(path)
            self.cookies_display.value = os.path.basename(path)
            self.cookies_display.tooltip = path
            self.update()

    def clear_history(self, e):
        self.app_state.clear_history()
        self.page.snack_bar = ft.SnackBar(ft.Text(self.app_state.get_str("history_cleared")))
        self.page.snack_bar.open = True
        self.page.update()