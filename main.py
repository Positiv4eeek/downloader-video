import flet as ft
import threading
import os
import subprocess
import platform
from flet import Icons, Colors, FontWeight, ThemeMode, CrossAxisAlignment, MainAxisAlignment

# Импорт логики и кастомных компонентов
from core.logic import VideoDownloader
from ui.components import StyledTextField, PrimaryButton, StatBadge, HistoryCard

def main(page: ft.Page):
    # Конфигурация окна приложения
    page.title = "YT LOADER PRO"
    page.theme_mode = ThemeMode.DARK
    page.window_width = 500
    page.window_height = 850
    page.window_resizable = False
    page.bgcolor = "#0F111A"  # Глубокий темный фон
    page.padding = 0

    # Состояние приложения: загрузка пути и истории из хранилища
    saved_path = page.client_storage.get("download_path") or os.path.join(os.path.expanduser("~"), "Downloads")
    state = {
        "path": saved_path,
        "history": page.client_storage.get("history") or []
    }

    downloader_logic = VideoDownloader(None)

    # --- Вспомогательные функции ---
    def show_msg(text, color=Colors.BLUE_ACCENT):
        """Отображение всплывающего уведомления"""
        page.snack_bar = ft.SnackBar(
            content=ft.Text(text, weight="bold"),
            bgcolor=color,
            behavior=ft.SnackBarBehavior.FLOATING,
            margin=20
        )
        page.snack_bar.open = True
        page.update()

    def open_folder(path):
        """Открытие папки с файлом в системном проводнике"""
        try:
            folder = os.path.dirname(path) if os.path.isfile(path) else path
            if platform.system() == "Windows":
                os.startfile(folder)
            else:
                subprocess.Popen(["open" if platform.system() == "Darwin" else "xdg-open", folder])
        except Exception as e:
            show_msg(f"Ошибка открытия папки: {e}", Colors.RED_400)

    # --- UI Элементы прогресса ---
    speed_text = ft.Text("0 MB/s", size=13, weight="bold")
    eta_text = ft.Text("00:00", size=13, weight="bold")
    size_text = ft.Text("0 MB", size=13, weight="bold")
    progress_bar = ft.ProgressBar(value=0, color=Colors.BLUE_ACCENT, height=6, border_radius=10)
    status_text = ft.Text("Готов к работе", size=12, color=Colors.BLUE_GREY_400)

    # --- Обработчик прогресса загрузки ---
    def on_progress(d):
        if d['status'] == 'downloading':
            try:
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                downloaded = d.get('downloaded_bytes', 0)
                p_val = downloaded / total if total > 0 else 0
                
                progress_bar.value = p_val
                status_text.value = f"Загрузка: {p_val * 100:.1f}%"
                speed_text.value = d.get('_speed_str', '0 MB/s')
                eta_text.value = d.get('_eta_str', '00:00')
                size_text.value = d.get('_total_bytes_str') or d.get('_total_bytes_estimate_str', '---')
                page.update()
            except: 
                pass
        elif d['status'] == 'finished':
            progress_bar.value = 1.0
            status_text.value = "Завершение (склейка)..."
            page.update()

    # --- Логика скачивания ---
    def handle_download(e):
        url = url_input.value.strip()
        if not url:
            show_msg("Введите ссылку!", Colors.RED_400)
            return

        download_btn.disabled = True
        progress_container.visible = True
        status_text.value = "Инициализация..."
        page.update()

        def run():
            try:
                # Получение инфо для истории
                info = downloader_logic.get_video_info(url)
                
                # Запуск загрузки
                downloader = VideoDownloader(on_progress)
                downloader.download(
                    url, 
                    state["path"], 
                    quality=quality_dd.value, 
                    audio_only=audio_switch.value
                )
                
                # Добавление в историю
                new_entry = {
                    "title": info.get('title', 'Видео'),
                    "author": info.get('uploader', 'Автор'),
                    "thumb": info.get('thumbnail', ''),
                    "path": state["path"]
                }
                state["history"].append(new_entry)
                page.client_storage.set("history", state["history"][-20:]) # Храним последние 20 записей
                
                show_msg("✅ Загрузка завершена!", Colors.GREEN_700)
            except Exception as ex:
                show_msg(f"❌ Ошибка: {str(ex)[:50]}", Colors.RED_700)
            
            download_btn.disabled = False
            progress_container.visible = False
            page.update()

        threading.Thread(target=run, daemon=True).start()

    # --- Элементы интерфейса ---
    def load_preview(e):
        """Автоматическая загрузка превью при вставке ссылки"""
        if len(url_input.value) > 15:
            try:
                info = downloader_logic.get_video_info(url_input.value)
                video_title.value = info.get('title')
                preview_img.src = info.get('thumbnail')
                preview_card.visible = True
                page.update()
            except: 
                pass

    url_input = StyledTextField("URL Видео", "Вставьте ссылку сюда...", Icons.LINK_ROUNDED, on_change=load_preview)
    
    preview_img = ft.Image(src="", width=120, height=70, fit="cover", border_radius=10)
    video_title = ft.Text("", weight="bold", size=14, max_lines=2, overflow="ellipsis")
    preview_card = ft.Container(
        visible=False,
        padding=15,
        border_radius=20,
        bgcolor=Colors.with_opacity(0.05, Colors.WHITE),
        content=ft.Row([preview_img, ft.Column([video_title], expand=True)])
    )

    quality_dd = ft.Dropdown(
        value="best",
        options=[
            ft.dropdown.Option("best", "Максимальное"),
            ft.dropdown.Option("1080p", "1080p"),
            ft.dropdown.Option("720p", "720p"),
            ft.dropdown.Option("480p", "480p")
        ],
        border_radius=12, expand=True
    )

    audio_switch = ft.Switch(label="Только MP3", value=False, active_color=Colors.BLUE_ACCENT)
    
    path_picker = ft.FilePicker(on_result=lambda e: (
        state.update({"path": e.path}), 
        page.client_storage.set("download_path", e.path),
        show_msg(f"Папка изменена")
    ) if e.path else None)
    page.overlay.append(path_picker)

    download_btn = PrimaryButton("СКАЧАТЬ СЕЙЧАС", Icons.DOWNLOAD_FOR_OFFLINE_ROUNDED, handle_download)

    progress_container = ft.Container(
        visible=False,
        padding=20,
        border_radius=20,
        bgcolor=Colors.with_opacity(0.02, Colors.WHITE),
        content=ft.Column([
            ft.Row([
                StatBadge(Icons.SPEED_ROUNDED, "СКОРОСТЬ", speed_text),
                StatBadge(Icons.SD_STORAGE_ROUNDED, "РАЗМЕР", size_text),
            ], spacing=15),
            progress_bar,
            status_text
        ], spacing=15)
    )

    # --- Навигация ---
    def change_tab(index):
        download_view.visible = (index == 0)
        history_view.visible = (index == 1)
        nav_download.bgcolor = Colors.with_opacity(0.1, Colors.BLUE_ACCENT) if index == 0 else Colors.TRANSPARENT
        nav_history.bgcolor = Colors.with_opacity(0.1, Colors.BLUE_ACCENT) if index == 1 else Colors.TRANSPARENT
        if index == 1: 
            refresh_history()
        page.update()

    nav_download = ft.Container(
        content=ft.Text("ЗАГРУЗКА", weight="bold", size=12),
        padding=ft.padding.symmetric(12, 25),
        border_radius=10,
        bgcolor=Colors.with_opacity(0.1, Colors.BLUE_ACCENT),
        on_click=lambda _: change_tab(0)
    )
    nav_history = ft.Container(
        content=ft.Text("ИСТОРИЯ", weight="bold", size=12),
        padding=ft.padding.symmetric(12, 25),
        border_radius=10,
        on_click=lambda _: change_tab(1)
    )

    # --- Вкладки контента ---
    download_view = ft.Column([
        url_input,
        preview_card,
        ft.Row([
            quality_dd, 
            ft.IconButton(Icons.FOLDER_OPEN_ROUNDED, on_click=lambda _: path_picker.get_directory_path())
        ]),
        ft.Row([audio_switch], alignment=MainAxisAlignment.START),
        ft.Divider(height=10, color="transparent"),
        download_btn,
        progress_container
    ], spacing=15, visible=True)

    history_list = ft.ListView(expand=True, spacing=12)
    history_view = ft.Column([
        ft.Text("Недавние загрузки", size=18, weight="bold"),
        history_list
    ], visible=False, expand=True)

    def refresh_history():
        history_list.controls.clear()
        for item in reversed(state["history"]):
            history_list.controls.append(
                HistoryCard(item['title'], item['author'], item['thumb'], item['path'], open_folder)
            )
        page.update()

    # --- Главная структура страницы ---
    page.add(
        ft.Container(
            expand=True,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=["#1A1C26", "#0F111A"]
            ),
            padding=30,
            content=ft.Column([
                # Заголовок
                ft.Row([
                    ft.Icon(Icons.PLAY_CIRCLE_FILL_ROUNDED, color=Colors.BLUE_ACCENT, size=35),
                    ft.Column([
                        ft.Text("YT LOADER", size=22, weight=FontWeight.W_900),
                        ft.Text("PREMIUM EDITION", size=10, color=Colors.BLUE_ACCENT, weight="bold"),
                    ], spacing=-5)
                ], alignment=MainAxisAlignment.CENTER),
                
                ft.Divider(height=30, color=Colors.with_opacity(0.1, Colors.WHITE)),
                
                # Селектор вкладок
                ft.Row([nav_download, nav_history], alignment=MainAxisAlignment.CENTER, spacing=10),
                
                ft.Divider(height=20, color="transparent"),
                
                # Область контента
                ft.Container(content=ft.Stack([download_view, history_view]), expand=True)
            ])
        )
    )

if __name__ == "__main__":
    ft.app(target=main)