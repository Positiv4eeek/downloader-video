import flet as ft
import threading
import os
from flet import Icons, Colors, FontWeight, ThemeMode, CrossAxisAlignment, MainAxisAlignment

# Импортируем нашу логику и компоненты
from core.logic import VideoDownloader
from ui.components import StyledTextField, PrimaryButton, StatBadge

def main(page: ft.Page):
    # Настройки окна
    page.title = "Modern YT Loader Pro v2.5"
    page.theme_mode = ThemeMode.DARK
    page.window_width = 500
    page.window_height = 800
    page.padding = 25
    page.window_resizable = False

    # Состояние приложения
    selected_path = os.path.join(os.path.expanduser("~"), "Downloads")
    downloader_logic = VideoDownloader(None)

    # UI элементы, которые будут обновляться динамически
    speed_text = ft.Text("0 MB/s", size=12, weight="bold")
    eta_text = ft.Text("00:00", size=12, weight="bold")
    size_text = ft.Text("0 MB", size=12, weight="bold")
    
    video_title = ft.Text("Ожидание ссылки...", weight="bold", max_lines=2, overflow="ellipsis")
    video_author = ft.Text("", size=12, color=Colors.BLUE_GREY_400)
    preview_img = ft.Image(src="", width=140, height=80, fit="cover", border_radius=8, visible=False)
    
    # 1. Логика выбора папки
    def on_directory_result(e: ft.FilePickerResultEvent):
        nonlocal selected_path
        if e.path:
            selected_path = e.path
            path_text.value = f"Путь: ...{selected_path[-25:]}"
            page.update()

    directory_picker = ft.FilePicker(on_result=on_directory_result)
    page.overlay.append(directory_picker)

    # 2. Исправленный обработчик прогресса (решает проблему пустого экрана при HLS)
    def on_progress(d):
        if d['status'] == 'downloading':
            try:
                # Получаем процент загрузки
                p_str = d.get('_percent_str')
                if p_str:
                    p_val = float(p_str.replace('%', '').strip()) / 100
                else:
                    # Расчет вручную, если yt-dlp не отдал готовую строку процента
                    downloaded = d.get('downloaded_bytes', 0)
                    total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                    p_val = downloaded / total if total > 0 else 0
                    p_str = f"{p_val*100:.1f}%"

                # Обновляем прогресс-бар и текстовый статус
                progress_bar.value = p_val
                status_text.value = f"Загрузка: {p_str}"
                
                # Обновляем детальную статистику
                speed_text.value = d.get('_speed_str', '---')
                eta_text.value = d.get('_eta_str', '---')
                
                # Размер может быть точным или оценочным (для HLS)
                total_size = d.get('_total_bytes_str') or d.get('_total_bytes_estimate_str', '---')
                size_text.value = total_size
                
                page.update()
            except Exception as ex:
                print(f"Ошибка в on_progress: {ex}")

    # 3. Загрузка информации о видео (Preview)
    def load_preview(e):
        url = url_input.value.strip()
        if len(url) > 15:
            try:
                info = downloader_logic.get_video_info(url)
                video_title.value = info.get('title')
                video_author.value = info.get('uploader')
                preview_img.src = info.get('thumbnail')
                preview_img.visible = True
                preview_card.visible = True
                page.update()
            except:
                preview_card.visible = False
                page.update()

    # 4. Запуск процесса скачивания
    def handle_download(e):
        url = url_input.value.strip()
        if not url:
            url_input.error_text = "Введите ссылку!"
            page.update()
            return

        # Блокируем кнопку и показываем блок прогресса
        download_btn.disabled = True
        progress_container.visible = True
        status_text.value = "Инициализация..."
        status_text.color = Colors.BLUE_ACCENT
        page.update()

        downloader = VideoDownloader(on_progress)
        
        def run():
            try:
                downloader.download(
                    url, 
                    selected_path, 
                    quality=quality_dd.value,
                    audio_only=audio_switch.value,
                    allow_playlist=playlist_switch.value
                )
                status_text.value = "✅ Готово! Файл сохранен"
                status_text.color = Colors.GREEN_400
            except Exception as ex:
                status_text.value = f"❌ Ошибка: {str(ex)[:40]}..."
                status_text.color = Colors.RED_400
            
            download_btn.disabled = False
            page.update()

        threading.Thread(target=run, daemon=True).start()

    # Сборка интерфейса
    url_input = StyledTextField("Ссылка на YouTube", "https://...", Icons.LINK_ROUNDED)
    url_input.on_change = load_preview

    preview_card = ft.Card(
        visible=False,
        variant=ft.CardVariant.OUTLINED,
        content=ft.Container(
            padding=15,
            content=ft.Row([
                preview_img,
                ft.Column([video_title, video_author], expand=True, tight=True)
            ], vertical_alignment=CrossAxisAlignment.CENTER)
        )
    )

    quality_dd = ft.Dropdown(
        label="Качество видео",
        value="best",
        options=[
            ft.dropdown.Option("best", "Максимальное"),
            ft.dropdown.Option("1080p", "1080p Full HD"),
            ft.dropdown.Option("720p", "720p HD"),
            ft.dropdown.Option("480p", "480p SD"),
        ],
        border_radius=12, expand=True
    )

    audio_switch = ft.Switch(label="Только MP3", value=False)
    playlist_switch = ft.Switch(label="Плейлист", value=False)
    
    path_text = ft.Text(f"Путь: Загрузки", size=11, color=Colors.BLUE_GREY_400)
    path_btn = ft.TextButton("Изменить папку", icon=Icons.FOLDER_OPEN, on_click=lambda _: directory_picker.get_directory_path())

    download_btn = PrimaryButton("СКАЧАТЬ ВИДЕО", Icons.DOWNLOAD_FOR_OFFLINE_ROUNDED, handle_download)
    progress_bar = ft.ProgressBar(value=0, color=Colors.BLUE_ACCENT, height=8, border_radius=5)
    status_text = ft.Text("", size=12)

    # Блок со статистикой и прогресс-баром
    progress_container = ft.Column([
        ft.Row([
            StatBadge(Icons.SPEED_ROUNDED, "СКОРОСТЬ", speed_text),
            StatBadge(Icons.TIMER_ROUNDED, "ОСТАЛОСЬ", eta_text),
            StatBadge(Icons.SD_STORAGE_ROUNDED, "РАЗМЕР", size_text),
        ], spacing=10),
        ft.Divider(height=10, color="transparent"),
        progress_bar,
        status_text
    ], visible=False)

    # Добавление всех элементов на страницу
    page.add(
        ft.Column([
            ft.Row([
                ft.Icon(Icons.SLOW_MOTION_VIDEO_ROUNDED, size=40, color=Colors.RED_ACCENT),
                ft.Text("YT Downloader Pro", size=26, weight=FontWeight.BOLD)
            ], alignment=MainAxisAlignment.CENTER),
            ft.Divider(height=20, color=Colors.BLUE_GREY_900),
            url_input,
            preview_card,
            ft.Row([quality_dd], alignment=MainAxisAlignment.START),
            ft.Row([audio_switch, playlist_switch], alignment=MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([path_text, path_btn], alignment=MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(height=10, color="transparent"),
            download_btn,
            ft.Container(padding=5),
            progress_container
        ], horizontal_alignment=CrossAxisAlignment.CENTER)
    )

if __name__ == "__main__":
    ft.app(target=main)