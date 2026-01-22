import flet as ft
import threading
from flet import Icons
from ui.theme import ThemeColors, DesignSystem
from ui.components import PrimaryButton, SettingTile
from core.logic import VideoDownloader

class SettingsView(ft.Column):
    def __init__(self, page: ft.Page, app_state):
        super().__init__(
            spacing=15,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )
        self.page = page
        self.app_state = app_state
        self.visible = False

        self.path_picker = ft.FilePicker(on_result=self.change_path_result)
        self.page.overlay.extend([self.path_picker])
        
        self.path_display = ft.Text(self.app_state.download_path, size=11, color=ThemeColors.TEXT_DIM, max_lines=1, overflow="ellipsis", width=150, text_align="right")

        # Выбор языка
        self.lang_dd = ft.Dropdown(
            value=self.app_state.language,
            options=[ft.dropdown.Option("ru", "Русский"), ft.dropdown.Option("en", "English")],
            width=120, text_size=12, border_radius=12, content_padding=10,
            on_change=self.change_language,
            border_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE30)
        )
        
        self.monitor_clipboard_switch = ft.Switch(value=self.app_state.monitor_clipboard, on_change=self.toggle_clipboard, active_color=ThemeColors.PRIMARY)
        self.embed_meta_switch = ft.Switch(value=self.app_state.embed_meta, on_change=lambda e: self.app_state.set_embed_meta(e.control.value), active_color=ThemeColors.PRIMARY)

        self.update_btn = ft.ElevatedButton(
            self.app_state.get_str("update_ytdlp_btn"), 
            icon=Icons.AUTORENEW, 
            bgcolor=ft.Colors.with_opacity(0.1, ThemeColors.PRIMARY), 
            color=ft.Colors.WHITE,
            on_click=self.update_ytdlp,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12))
        )

        # --- Текстовые метки ---
        self.title_text = ft.Text(self.app_state.get_str("settings_title"), size=20, weight="bold", color=ThemeColors.TEXT_MAIN)
        self.lang_label = self.app_state.get_str("lang_label")
        self.theme_label = self.app_state.get_str("theme_dark")
        self.folder_label = self.app_state.get_str("folder_download")
        self.clipboard_label = self.app_state.get_str("monitor_clipboard")
        self.meta_label = self.app_state.get_str("embed_meta_switch")
        self.system_label = ft.Text(self.app_state.get_str("system_section"), size=15, weight="bold", color=ThemeColors.TEXT_DIM)

        self._update_controls()

    def _update_controls(self):
        self.controls = [
            ft.Container(
                padding=ft.padding.only(right=20, left=5, top=5, bottom=5),
                content=ft.Column([
                    ft.Row([
                        ft.Icon(Icons.SETTINGS_ROUNDED, color=ThemeColors.PRIMARY, size=24),
                        self.title_text,
                    ], spacing=10),
                    
                    ft.Container(height=5),
                    SettingTile(Icons.LANGUAGE_ROUNDED, self.lang_label, self.lang_dd),
                    SettingTile(Icons.FOLDER_OPEN_ROUNDED, self.folder_label, 
                        ft.Row([self.path_display, ft.IconButton(Icons.EDIT_ROUNDED, on_click=lambda _: self.path_picker.get_directory_path(), icon_color=ThemeColors.PRIMARY, icon_size=20)], spacing=0)),

                    ft.Divider(height=30, color=ft.Colors.with_opacity(0.05, ft.Colors.WHITE)),
                    self.system_label,
                    SettingTile(Icons.PASTE, self.clipboard_label, self.monitor_clipboard_switch),
                    SettingTile(Icons.AUTO_FIX_HIGH, self.meta_label, self.embed_meta_switch),
                    
                    SettingTile(Icons.SYSTEM_UPDATE_ALT, "Core Engine", self.update_btn),
                    
                    SettingTile(Icons.DELETE_SWEEP_ROUNDED, "Data", 
                        PrimaryButton(self.app_state.get_str("clear_history"), Icons.DELETE_OUTLINE_ROUNDED, self.clear_history))
                ], spacing=15)
            )
        ]

    def update_locale(self):
        self.title_text.value = self.app_state.get_str("settings_title")
        self.lang_label = self.app_state.get_str("lang_label")
        self.theme_label = self.app_state.get_str("theme_dark")
        self.folder_label = self.app_state.get_str("folder_download")
        self.clipboard_label = self.app_state.get_str("monitor_clipboard")
        self.meta_label = self.app_state.get_str("embed_meta_switch")
        self.update_btn.text = self.app_state.get_str("update_ytdlp_btn")
        self.system_label.value = self.app_state.get_str("system_section")
        self._update_controls()
        self.update()

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
            color = ft.Colors.GREEN_700 if success else ft.Colors.RED_700
            
            self.page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=color)
            self.page.snack_bar.open = True
            self.page.update()
            self.update()

        threading.Thread(target=run_update, daemon=True).start()

    def change_language(self, e):
        self.app_state.set_language(self.lang_dd.value)
    def change_path_result(self, e):
        if e.path:
            self.app_state.set_download_path(e.path)
            self.path_display.value = e.path
            self.update()
    def clear_history(self, e):
        self.app_state.clear_history()
        self.page.snack_bar = ft.SnackBar(ft.Text(self.app_state.get_str("history_cleared")), bgcolor=ThemeColors.PRIMARY)
        self.page.snack_bar.open = True
        self.page.update()

