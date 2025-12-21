import flet as ft
from flet import Icons, Colors, MainAxisAlignment

from core.state import AppState
from core.utils import check_ffmpeg
from ui.views.download_view import DownloadView
from ui.views.history_view import HistoryView
from ui.views.settings_view import SettingsView

def main(page: ft.Page):
    # 1. Инициализация состояния
    app_state = AppState(page)
    
    page.title = app_state.get_str("app_title")
    page.window_width = 500
    page.window_height = 900
    page.padding = 0
    
    app_state.set_theme(app_state.theme_mode)
    
    # Проверка FFmpeg
    if not check_ffmpeg():
        page.snack_bar = ft.SnackBar(
            content=ft.Text("⚠️ FFmpeg not found! MP3 and some video formats might fail.", color=Colors.WHITE),
            bgcolor=Colors.RED_700,
            duration=5000,
            action="OK"
        )
        page.snack_bar.open = True

    # 2. Создание Views
    download_view = DownloadView(page, app_state)
    history_view = HistoryView(page, app_state)
    settings_view = SettingsView(page, app_state)

    # 3. Навигация
    def change_tab(index):
        download_view.visible = (index == 0)
        history_view.visible = (index == 1)
        settings_view.visible = (index == 2)
        
        for i, btn in enumerate([nav_home, nav_hist, nav_sett]):
            btn.bgcolor = Colors.with_opacity(0.1, Colors.BLUE_ACCENT) if i == index else Colors.TRANSPARENT
        
        if index == 1: history_view.refresh()
        page.update()

    nav_home = ft.Container(content=ft.Icon(Icons.HOME_ROUNDED), padding=10, border_radius=10, on_click=lambda _: change_tab(0), bgcolor=Colors.with_opacity(0.1, Colors.BLUE_ACCENT))
    nav_hist = ft.Container(content=ft.Icon(Icons.HISTORY_ROUNDED), padding=10, border_radius=10, on_click=lambda _: change_tab(1))
    nav_sett = ft.Container(content=ft.Icon(Icons.SETTINGS_ROUNDED), padding=10, border_radius=10, on_click=lambda _: change_tab(2))

    # 4. Сборка Layout
    page.add(
        ft.Container(
            expand=True,
            content=ft.Column([
                ft.Row([
                    ft.Icon(Icons.PLAY_CIRCLE_FILL_ROUNDED, color=Colors.BLUE_ACCENT, size=30),
                    ft.Text("YT LOADER", size=20, weight="bold"),
                    ft.Row([nav_home, nav_hist, nav_sett], spacing=5)
                ], alignment=MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=20, color="transparent"),
                ft.Container(content=ft.Stack([download_view, history_view, settings_view]), expand=True)
            ]),
            padding=25
        )
    )

if __name__ == "__main__":
    ft.app(target=main)