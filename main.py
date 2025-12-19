import flet as ft
import threading
import os
from flet import Icons, Colors, FontWeight, ThemeMode, MainAxisAlignment, CrossAxisAlignment

# Импортируем наши новые модули
from core.logic import VideoDownloader
from ui.components import StyledTextField, PrimaryButton

def main(page: ft.Page):
    page.title = "Modern YT Loader v2.0"
    page.theme_mode = ThemeMode.DARK
    page.window_width = 450
    page.window_height = 600
    page.padding = 30

    def on_progress(d):
        if d['status'] == 'downloading':
            p = d.get('_percent_str', '0%').replace('%', '').strip()
            try:
                progress_bar.value = float(p) / 100
                status_text.value = f"Загрузка: {d.get('_percent_str')}"
                page.update()
            except: pass

    def handle_download(e):
        url = url_input.value.strip()
        if not url:
            url_input.error_text = "Введите ссылку!"
            page.update()
            return

        download_btn.disabled = True
        progress_bar.visible = True
        status_text.value = "Начинаем..."
        page.update()

        downloader = VideoDownloader(on_progress)
        save_path = os.path.join(os.path.expanduser("~"), "Downloads")
        
        def run():
            try:
                downloader.download(url, save_path)
                status_text.value = "✅ Готово! Проверьте папку Загрузки"
                status_text.color = Colors.GREEN_400
            except Exception as ex:
                status_text.value = f"❌ Ошибка: {str(ex)[:30]}..."
                status_text.color = Colors.RED_400
            download_btn.disabled = False
            page.update()

        threading.Thread(target=run, daemon=True).start()

    # Сборка интерфейса из компонентов
    url_input = StyledTextField("URL видео", "https://...", Icons.LINK_ROUNDED)
    download_btn = PrimaryButton("СКАЧАТЬ", Icons.DOWNLOAD_ROUNDED, handle_download)
    progress_bar = ft.ProgressBar(value=0, visible=False, color=Colors.BLUE_ACCENT)
    status_text = ft.Text("", size=12)

    page.add(
        ft.Column([
            ft.Icon(Icons.SLOW_MOTION_VIDEO_ROUNDED, size=50, color=Colors.RED_ACCENT),
            ft.Text("YT Downloader", size=24, weight=FontWeight.BOLD),
            ft.Divider(height=20, color="transparent"),
            url_input,
            download_btn,
            ft.Divider(height=10, color="transparent"),
            status_text,
            progress_bar
        ], horizontal_alignment=CrossAxisAlignment.CENTER)
    )

if __name__ == "__main__":
    ft.app(target=main)