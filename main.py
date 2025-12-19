import flet as ft
import yt_dlp
import threading
import os

# Импортируем все необходимые константы с большой буквы
from flet import (
    Icons, 
    Colors, 
    FontWeight, 
    MainAxisAlignment, 
    CrossAxisAlignment, 
    ThemeMode
)

def main(page: ft.Page):
    # Настройки страницы
    page.title = "Modern YouTube Downloader"
    page.theme_mode = ThemeMode.DARK
    page.window_width = 500
    page.window_height = 650
    page.window_resizable = False
    page.padding = 40
    page.vertical_alignment = MainAxisAlignment.START
    page.horizontal_alignment = CrossAxisAlignment.CENTER

    # --- ЛОГИКА ЗАГРУЗКИ ---
    
    def progress_hook(d):
        if d['status'] == 'downloading':
            p = d.get('_percent_str', '0%').replace('%', '').strip()
            try:
                clean_percent = float(p) / 100
                progress_bar.value = clean_percent
                status_text.value = f"Загрузка: {d.get('_percent_str')}"
                page.update()
            except ValueError:
                pass
        elif d['status'] == 'finished':
            progress_bar.value = 1.0
            status_text.value = "Сборка файла завершена!"
            page.update()

    def start_download(e):
        url = url_input.value.strip()
        
        if not url:
            url_input.error_text = "Пожалуйста, вставьте ссылку"
            page.update()
            return
        
        url_input.error_text = None
        download_btn.disabled = True
        progress_container.visible = True
        status_text.value = "Анализ видео..."
        status_text.color = Colors.BLUE_GREY_200
        progress_bar.value = 0
        page.update()

        ydl_opts = {
            'format': 'best',
            'progress_hooks': [progress_hook],
            'outtmpl': os.path.join(os.path.expanduser("~"), "Downloads", "%(title)s.%(ext)s"),
            'noplaylist': True,
        }

        def run_proc():
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                status_text.value = "✅ Видео успешно скачано в 'Загрузки'"
                status_text.color = Colors.GREEN_400
            except Exception as ex:
                status_text.value = f"❌ Ошибка: {str(ex)[:50]}..."
                status_text.color = Colors.RED_400
            
            download_btn.disabled = False
            page.update()

        threading.Thread(target=run_proc, daemon=True).start()

    # --- ДИЗАЙН ИНТЕРФЕЙСА (UI) ---

    header = ft.Column(
        controls=[
            ft.Icon(Icons.PLAY_CIRCLE_FILL_ROUNDED, size=50, color=Colors.RED_ACCENT),
            ft.Text("YT Video Loader", size=28, weight=FontWeight.BOLD),
            ft.Text("Вставьте ссылку ниже", color=Colors.GREY_400),
        ],
        horizontal_alignment=CrossAxisAlignment.CENTER
    )

    url_input = ft.TextField(
        label="URL видео",
        hint_text="https://www.youtube.com/watch?v=...", # ИСПРАВЛЕНО: placeholder -> hint_text
        border_radius=15,
        border_color=Colors.BLUE_GREY_700,
        focused_border_color=Colors.BLUE_ACCENT,
        prefix_icon=Icons.LINK_ROUNDED,
        text_size=14,
    )

    download_btn = ft.ElevatedButton(
        content=ft.Row(
            [ft.Icon(Icons.DOWNLOAD_ROUNDED), ft.Text("СКАЧАТЬ", weight="bold")],
            alignment=MainAxisAlignment.CENTER,
            spacing=10
        ),
        style=ft.ButtonStyle(
            color=Colors.WHITE,
            bgcolor=Colors.BLUE_700,
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
        height=50,
        width=float("inf"),
        on_click=start_download
    )

    status_text = ft.Text("", size=12, color=Colors.BLUE_GREY_200)
    progress_bar = ft.ProgressBar(
        value=0, 
        width=400, 
        color=Colors.BLUE_ACCENT, 
        bgcolor=Colors.BLUE_GREY_900
    )
    
    progress_container = ft.Column(
        visible=False,
        controls=[
            status_text,
            progress_bar,
        ],
        horizontal_alignment=CrossAxisAlignment.CENTER
    )

    page.add(
        header,
        ft.Divider(height=40, color="transparent"),
        url_input,
        ft.Divider(height=10, color="transparent"),
        download_btn,
        ft.Divider(height=30, color="transparent"),
        progress_container
    )

if __name__ == "__main__":
    ft.app(target=main)