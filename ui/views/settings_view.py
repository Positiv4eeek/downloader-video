import flet as ft
import os
import threading
from flet import Icons, Colors
from ui.components import SettingTile, StyledTextField
from core.logic import VideoDownloader

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
            options=[ft.dropdown.Option("ru", "Русский"), ft.dropdown.Option("en", "English")],
            width=120, text_size=13, border_radius=10, content_padding=10,
            on_change=self.change_language
        )
        
        # --- NEW: Выбор браузера для куки ---
        self.browser_dd = ft.Dropdown(
            value=self.app_state.cookies_browser,
            options=[
                ft.dropdown.Option("none", self.app_state.get_str("browser_none")),
                ft.dropdown.Option("chrome", "Chrome"),
                ft.dropdown.Option("firefox", "Firefox"),
                ft.dropdown.Option("opera", "Opera"),
                ft.dropdown.Option("edge", "Edge"),
            ],
            width=150, text_size=13, border_radius=10, content_padding=10,
            on_change=self.change_browser
        )

        self.monitor_clipboard_switch = ft.Switch(value=self.app_state.monitor_clipboard, on_change=self.toggle_clipboard)
        self.embed_meta_switch = ft.Switch(value=self.app_state.embed_meta, on_change=lambda e: self.app_state.set_embed_meta(e.control.value))

        self.update_btn = ft.ElevatedButton(
            self.app_state.get_str("update_ytdlp_btn"), 
            icon=Icons.UPDATE, 
            bgcolor=Colors.BLUE_GREY_800, 
            color="white",
            on_click=self.update_ytdlp
        )

        self.proxy_input = StyledTextField(self.app_state.get_str("proxy_label"), "http://user:pass@ip:port", Icons.VPN_LOCK_ROUNDED, 
                                           on_change=lambda e: self.app_state.set_proxy(e.control.value))
        self.proxy_input.value = self.app_state.proxy_url
        
        self.cookies_display = ft.Text(os.path.basename(self.app_state.cookies_path) if self.app_state.cookies_path else "Not selected", size=12, color=Colors.BLUE_GREY_400, max_lines=1, overflow="ellipsis", width=150, text_align="right")

        # --- Ссылки для обновления локализации ---
        self.title_text = ft.Text(self.app_state.get_str("settings_title"), size=20, weight="bold")
        self.lang_label = ft.Text(self.app_state.get_str("lang_label"), size=14, weight="w500")
        self.theme_label = ft.Text(self.app_state.get_str("theme_dark"), size=14, weight="w500")
        self.folder_label = ft.Text(self.app_state.get_str("folder_download"), size=14, weight="w500")
        self.cookies_label_text = ft.Text(self.app_state.get_str("cookies_label"), size=14, weight="w500")
        self.browser_cookies_label = ft.Text(self.app_state.get_str("browser_cookies_label"), size=14, weight="w500")
        self.history_btn_text = ft.Text(self.app_state.get_str("clear_history"), weight="bold", size=15)
        self.clipboard_label = ft.Text(self.app_state.get_str("monitor_clipboard"), size=14, weight="w500")
        self.meta_label = ft.Text(self.app_state.get_str("embed_meta_switch"), size=14, weight="w500")
        self.system_label = ft.Text(self.app_state.get_str("system_section"), size=16, weight="bold")

        self.controls = [
            self.title_text,
            
            self._build_tile(Icons.LANGUAGE_ROUNDED, self.lang_label, self.lang_dd),
            self._build_tile(Icons.DARK_MODE_ROUNDED, self.theme_label, self.theme_switch),
            self._build_tile(Icons.FOLDER_ROUNDED, self.folder_label, ft.Row([self.path_display, ft.IconButton(Icons.EDIT_ROUNDED, on_click=lambda _: self.path_picker.get_directory_path())])),
            
            ft.Divider(),
            ft.Text("Network & Access", size=16, weight="bold"),
            self.proxy_input,
            self._build_tile(Icons.COOKIE_ROUNDED, self.cookies_label_text, ft.Row([self.cookies_display, ft.IconButton(Icons.UPLOAD_FILE_ROUNDED, on_click=lambda _: self.cookies_picker.pick_files(allow_multiple=False))])),
            self._build_tile(Icons.WEB_ROUNDED, self.browser_cookies_label, self.browser_dd),

            ft.Divider(),
            self.system_label,
            self._build_tile(Icons.PASTE_ROUNDED, self.clipboard_label, self.monitor_clipboard_switch),
            self._build_tile(Icons.IMAGE_ROUNDED, self.meta_label, self.embed_meta_switch),
            
            ft.Container(
                content=ft.Row([
                    ft.Row([ft.Icon(Icons.SYSTEM_UPDATE_ALT_ROUNDED, color=Colors.BLUE_GREY_400), self.update_btn], spacing=15),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=15, bgcolor=Colors.with_opacity(0.03, Colors.WHITE), border_radius=12
            ),
            
            ft.Container(
                content=ft.Row([
                    ft.Row([ft.Icon(Icons.DELETE_SWEEP_ROUNDED, color=Colors.BLUE_GREY_400), ft.Text("History", size=14, weight="w500")], spacing=15),
                    ft.ElevatedButton(content=self.history_btn_text, bgcolor=Colors.RED_700, color="white", on_click=self.clear_history)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=15, bgcolor=Colors.with_opacity(0.03, Colors.WHITE), border_radius=12
            )
        ]

    def _build_tile(self, icon, label_control, content_control):
        return ft.Container(
            content=ft.Row([
                ft.Row([ft.Icon(icon, color=Colors.BLUE_GREY_400), label_control], spacing=15),
                content_control
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=15, bgcolor=Colors.with_opacity(0.03, Colors.WHITE), border_radius=12
        )

    def update_locale(self):
        self.title_text.value = self.app_state.get_str("settings_title")
        self.lang_label.value = self.app_state.get_str("lang_label")
        self.theme_label.value = self.app_state.get_str("theme_dark")
        self.folder_label.value = self.app_state.get_str("folder_download")
        self.proxy_input.label = self.app_state.get_str("proxy_label")
        self.cookies_label_text.value = self.app_state.get_str("cookies_label")
        self.browser_cookies_label.value = self.app_state.get_str("browser_cookies_label")
        self.history_btn_text.value = self.app_state.get_str("clear_history")
        self.browser_dd.options[0].text = self.app_state.get_str("browser_none")
        self.update_btn.text = self.app_state.get_str("update_ytdlp_btn")
        self.clipboard_label.value = self.app_state.get_str("monitor_clipboard")
        self.meta_label.value = self.app_state.get_str("embed_meta_switch")
        self.system_label.value = self.app_state.get_str("system_section")
        self.update()

    def change_browser(self, e):
        self.app_state.set_cookies_browser(self.browser_dd.value)

    def toggle_clipboard(self, e):
        self.app_state.set_monitor_clipboard(self.monitor_clipboard_switch.value)

    def update_ytdlp(self, e):
        self.update_btn.disabled = True
        self.update_btn.text = "Updating..."
        self.update()
        
        def run_update():
            success = VideoDownloader.update_ytdlp()
            self.update_btn.disabled = False
            self.update_btn.text = self.app_state.get_str("update_ytdlp_btn")
            msg = self.app_state.get_str("update_success") if success else self.app_state.get_str("update_error")
            color = Colors.GREEN if success else Colors.RED
            
            self.page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=color)
            self.page.snack_bar.open = True
            self.page.update()
            self.update()

        threading.Thread(target=run_update, daemon=True).start()

    # (Остальные методы без изменений: change_language, toggle_theme, change_path_result, etc.)
    def change_language(self, e):
        self.app_state.set_language(self.lang_dd.value)
    def toggle_theme(self, e):
        self.app_state.set_theme("dark" if self.theme_switch.value else "light")
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