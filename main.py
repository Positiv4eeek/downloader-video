import flet as ft
import os
from flet import Icons, Colors, MainAxisAlignment

from core.state import AppState
from core.utils import check_ffmpeg, install_ffmpeg_windows, get_ffmpeg_path
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
    
    # 2. Проверка и установка FFmpeg
    # Если путь не найден в PATH или локально, предлагаем установить
    if not get_ffmpeg_path():
        def start_install(e):
            dlg.actions[0].disabled = True
            dlg.content = ft.Column([
                ft.Text("Downloading FFmpeg... Please wait."),
                ft.ProgressBar(width=300)
            ], height=100)
            page.update()
            
            def hook(progress):
                # В реальном приложении тут можно обновлять progress bar, но в flet с потоками
                # нужно аккуратно. Пока оставим так.
                pass
                
            success = install_ffmpeg_windows(hook)
            dlg.open = False
            
            if success:
                # Добавляем bin в PATH текущего процесса
                bin_path = os.path.join(os.getcwd(), "bin")
                os.environ["PATH"] += os.pathsep + bin_path
                page.snack_bar = ft.SnackBar(ft.Text("FFmpeg installed successfully!"), bgcolor=Colors.GREEN)
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Install failed. Please install manually."), bgcolor=Colors.RED)
            page.snack_bar.open = True
            page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("FFmpeg missing"),
            content=ft.Text("FFmpeg not found. Install automatically? (Required for MP3/1080p)"),
            actions=[
                ft.TextButton("Install", on_click=start_install),
                ft.TextButton("Cancel", on_click=lambda _: setattr(dlg, 'open', False) or page.update()),
            ],
            modal=True
        )
        page.dialog = dlg
        dlg.open = True

    # 3. Создание Views
    download_view = DownloadView(page, app_state)
    history_view = HistoryView(page, app_state)
    settings_view = SettingsView(page, app_state)

    # --- Подписка на изменение языка ---
    def on_language_changed():
        download_view.update_locale()
        settings_view.update_locale()
        page.title = app_state.get_str("app_title")
        page.update()

    app_state.add_observer(on_language_changed)

    # 4. Навигация
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

    # 5. Сборка Layout
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