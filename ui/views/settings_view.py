import flet as ft
from flet import Icons, Colors
from ui.components import SettingTile

class SettingsView(ft.Column):
    def __init__(self, page: ft.Page, app_state):
        super().__init__()
        self.page = page
        self.app_state = app_state
        self.visible = False
        self.spacing = 10

        self.path_picker = ft.FilePicker(on_result=self.change_path_result)
        self.page.overlay.append(self.path_picker)
        
        self.path_display = ft.Text(self.app_state.download_path, size=12, color=Colors.BLUE_GREY_400, max_lines=1, overflow="ellipsis", width=200, text_align="right")
        self.theme_switch = ft.Switch(value=(self.app_state.theme_mode=="dark"), on_change=self.toggle_theme)

        self.controls = [
            ft.Text("Настройки", size=20, weight="bold"),
            SettingTile(Icons.DARK_MODE_ROUNDED, "Темная тема", self.theme_switch),
            SettingTile(Icons.FOLDER_ROUNDED, "Папка загрузок", ft.Row([self.path_display, ft.IconButton(Icons.EDIT_ROUNDED, on_click=lambda _: self.path_picker.get_directory_path())])),
            ft.Divider(),
            SettingTile(Icons.DELETE_SWEEP_ROUNDED, "История", ft.ElevatedButton("Очистить", bgcolor=Colors.RED_700, color="white", on_click=self.clear_history)),
        ]

    def toggle_theme(self, e):
        new_mode = "dark" if self.theme_switch.value else "light"
        self.app_state.set_theme(new_mode)

    def change_path_result(self, e):
        if e.path:
            self.app_state.set_download_path(e.path)
            self.path_display.value = e.path
            self.update()

    def clear_history(self, e):
        self.app_state.clear_history()
        self.page.snack_bar = ft.SnackBar(ft.Text("История очищена"))
        self.page.snack_bar.open = True
        self.page.update()