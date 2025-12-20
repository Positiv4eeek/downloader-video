import flet as ft
from flet import Icons, Colors, MainAxisAlignment, ThemeMode

from core.state import AppState
from ui.views.download_view import DownloadView
from ui.views.history_view import HistoryView
from ui.views.settings_view import SettingsView

def main(page: ft.Page):
    page.title = "YT LOADER PRO v2.2"
    page.window_width = 500
    page.window_height = 900
    page.padding = 0
    
    # 1. Инициализация состояния
    app_state = AppState(page)
    # Применяем тему при старте
    app_state.set_theme(app_state.theme_mode)

    # 2. Создание Views
    download_view = DownloadView(page, app_state)
    history_view = HistoryView(page, app_state)
    settings_view = SettingsView(page, app_state)

    # 3. Навигация
    def change_tab(index):
        download_view.visible = (index == 0)
        history_view.visible = (index == 1)
        settings_view.visible = (index == 2)
        
        # Обновляем стиль кнопок
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