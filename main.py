import flet as ft
import os
from flet import Icons, Colors, MainAxisAlignment

from core.state import AppState
from core.utils import check_ffmpeg, install_ffmpeg_windows, get_ffmpeg_path
from ui.views.download_view import DownloadView
from ui.views.history_view import HistoryView
from ui.views.settings_view import SettingsView
from ui.theme import ThemeColors, DesignSystem

def main(page: ft.Page):
    # 1. Инициализация состояния
    app_state = AppState(page)
    
    page.title = app_state.get_str("app_title")
    page.window_width = 500
    page.window_height = 900
    page.padding = 0
    page.bgcolor = ThemeColors.BG_DARK
    
    app_state.set_theme(app_state.theme_mode)
    
    # 2. Проверка и установка FFmpeg
    # Если путь не найден в PATH или локально, предлагаем установить
    if not get_ffmpeg_path():
        def start_install(e):
            dlg.actions[0].disabled = True
            dlg.content = ft.Column([
                ft.Text("Downloading FFmpeg... Please wait."),
                ft.ProgressBar(width=300, color=ThemeColors.PRIMARY)
            ], height=100)
            page.update()
            
            def hook(progress):
                pass
                
            success = install_ffmpeg_windows(hook)
            dlg.open = False
            
            if success:
                bin_path = os.path.join(os.getcwd(), "bin")
                os.environ["PATH"] += os.pathsep + bin_path
                page.snack_bar = ft.SnackBar(ft.Text("FFmpeg installed successfully!"), bgcolor=Colors.GREEN_700)
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Install failed. Please install manually."), bgcolor=Colors.RED_700)
            page.snack_bar.open = True
            page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("FFmpeg missing"),
            content=ft.Text("FFmpeg not found. Install automatically? (Required for MP3/1080p)"),
            actions=[
                ft.TextButton("Install", on_click=start_install),
                ft.TextButton("Cancel", on_click=lambda _: setattr(dlg, 'open', False) or page.update()),
            ],
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=DesignSystem.BORDER_RADIUS)
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
            btn.bgcolor = ft.Colors.with_opacity(0.1, ThemeColors.PRIMARY) if i == index else Colors.TRANSPARENT
            btn.content.color = ThemeColors.PRIMARY if i == index else ft.Colors.BLUE_GREY_400
        
        if index == 1: history_view.refresh()
        page.update()

    nav_home = ft.Container(content=ft.Icon(Icons.HOME_ROUNDED, color=ThemeColors.PRIMARY), padding=10, border_radius=12, on_click=lambda _: change_tab(0), bgcolor=ft.Colors.with_opacity(0.1, ThemeColors.PRIMARY))
    nav_hist = ft.Container(content=ft.Icon(Icons.HISTORY_ROUNDED, color=ft.Colors.BLUE_GREY_400), padding=10, border_radius=12, on_click=lambda _: change_tab(1))
    nav_sett = ft.Container(content=ft.Icon(Icons.SETTINGS_ROUNDED, color=ft.Colors.BLUE_GREY_400), padding=10, border_radius=12, on_click=lambda _: change_tab(2))

    # 5. Сборка Layout
    page.add(
        ft.Stack([
            # Background Gradient Overlay
            ft.Container(
                expand=True,
                gradient=ft.RadialGradient(
                    center=ft.alignment.top_right,
                    radius=1.5,
                    colors=[ft.Colors.with_opacity(0.15, ThemeColors.PRIMARY), Colors.TRANSPARENT]
                )
            ),
            ft.Container(
                expand=True,
                padding=20,
                content=ft.Column([
                    # Floating Glass Header
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=15, vertical=10),
                        border_radius=20,
                        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
                        border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
                        content=ft.Row([
                            ft.Row([
                                ft.Icon(Icons.PLAY_CIRCLE_FILL_ROUNDED, color=ThemeColors.PRIMARY, size=30),
                                ft.Text("YT LOADER", size=18, weight="bold"),
                            ], spacing=10),
                            ft.Row([nav_home, nav_hist, nav_sett], spacing=5)
                        ], alignment=MainAxisAlignment.SPACE_BETWEEN),
                    ),
                    ft.Divider(height=10, color="transparent"),
                    ft.Container(
                        content=ft.Stack([download_view, history_view, settings_view]), 
                        expand=True,
                    )
                ])
            )
        ], expand=True)
    )


if __name__ == "__main__":
    ft.app(target=main)