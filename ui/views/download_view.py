import flet as ft
import threading
import time
from flet import Icons, Colors, MainAxisAlignment
from core.logic import VideoDownloader, DownloadCancelled
from core.utils import open_path
from ui.components import StyledTextField, PrimaryButton, StatBadge, QueueItem

class DownloadView(ft.Column):
    def __init__(self, page: ft.Page, app_state):
        super().__init__()
        self.page = page
        self.app_state = app_state
        self.download_queue = []
        self.is_processing = False
        self.current_downloader = None
        self.downloader_logic = VideoDownloader(None)
        
        self.spacing = 15
        self.visible = True
        self.expand = True

        self._setup_ui()

    def _setup_ui(self):
        self.paste_btn = ft.IconButton(Icons.PASTE_ROUNDED, tooltip="Вставить", icon_color=Colors.BLUE_ACCENT, on_click=self.paste_from_clipboard)
        self.url_input = StyledTextField("URL Видео", "Ссылка...", Icons.LINK_ROUNDED, on_change=self.validate_input, suffix=self.paste_btn)
        
        # --- Скелетон и Превью ---
        self.preview_img = ft.Image(src="", width=120, height=70, fit="cover", border_radius=10, visible=False)
        self.skeleton = ft.Container(width=120, height=70, bgcolor=Colors.with_opacity(0.1, Colors.WHITE), border_radius=10, visible=False, animate_opacity=500)
        self.video_title = ft.Text("", weight="bold", size=14, max_lines=2, overflow="ellipsis")
        
        self.preview_card = ft.Container(
            visible=False, 
            padding=15, 
            border_radius=20, 
            bgcolor=Colors.with_opacity(0.05, Colors.WHITE),
            content=ft.Row([
                ft.Stack([self.skeleton, self.preview_img]), 
                ft.Column([self.video_title], expand=True)
            ])
        )

        self.quality_dd = ft.Dropdown(value="best", options=[ft.dropdown.Option(k,v) for k,v in {"best":"Макс.","1080p":"1080p","720p":"720p"}.items()], border_radius=12, expand=True)
        self.audio_switch = ft.Switch(label="MP3", value=False)
        self.playlist_switch = ft.Switch(label="Плейлист", value=False)
        self.open_folder_switch = ft.Checkbox(label="Открыть папку после завершения", value=False, label_style=ft.TextStyle(size=12, color=Colors.BLUE_GREY_200))

        self.download_btn = PrimaryButton("ДОБАВИТЬ", Icons.ADD_TO_PHOTOS_ROUNDED, self.add_to_queue)
        
        # Прогресс
        self.speed_text = ft.Text("0 MB/s", size=13, weight="bold")
        self.size_text = ft.Text("---", size=13, weight="bold")
        self.progress_bar = ft.ProgressBar(value=0, color=Colors.BLUE_ACCENT, height=6, border_radius=10)
        self.status_text = ft.Text("Готов", size=12, color=Colors.BLUE_GREY_400)
        self.cancel_btn = ft.ElevatedButton("СТОП", icon=Icons.CANCEL, bgcolor=Colors.RED_700, color="white", visible=False, on_click=self.cancel_current)
        
        self.queue_btn = ft.TextButton(text="", icon=Icons.LIST_ROUNDED, icon_color=Colors.ORANGE_ACCENT, visible=False, on_click=self.show_queue_modal)

        self.progress_container = ft.Container(visible=True, padding=20, border_radius=20, bgcolor=Colors.with_opacity(0.02, Colors.WHITE),
                                          content=ft.Column([
                                              ft.Row([self.queue_btn], alignment=MainAxisAlignment.END), 
                                              ft.Row([StatBadge(Icons.SPEED_ROUNDED, "СКОРОСТЬ", self.speed_text), StatBadge(Icons.SD_STORAGE_ROUNDED, "РАЗМЕР", self.size_text)], spacing=15),
                                              self.progress_bar,
                                              ft.Row([self.status_text, self.cancel_btn], alignment=MainAxisAlignment.SPACE_BETWEEN)
                                          ]))

        self.controls = [
            self.url_input, self.preview_card,
            ft.Row([self.quality_dd]),
            ft.Row([self.audio_switch, self.playlist_switch], alignment=MainAxisAlignment.SPACE_BETWEEN),
            self.open_folder_switch, # Добавили чекбокс
            self.download_btn, self.progress_container
        ]

        self.queue_list_view = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
        self.queue_bottom_sheet = ft.BottomSheet(
            ft.Container(
                ft.Column([
                    ft.Text("Очередь загрузки", size=20, weight="bold"),
                    ft.Divider(),
                    ft.Container(self.queue_list_view, height=300), 
                    ft.ElevatedButton("Закрыть", on_click=lambda _: self.page.close_bottom_sheet())
                ]),
                padding=20,
                bgcolor=Colors.GREY_900, 
                border_radius=ft.border_radius.only(top_left=20, top_right=20)
            )
        )

    # --- Логика ---
    async def paste_from_clipboard(self, e):
        text = await self.page.get_clipboard_async()
        if text:
            self.url_input.value = text
            self.validate_input(None)
            self.url_input.update()

    def validate_input(self, e):
        val = self.url_input.value.strip()
        if not val:
            self.url_input.error_text = None
            self.download_btn.disabled = False
            self.preview_card.visible = False
        elif not (val.startswith("http://") or val.startswith("https://")):
            self.url_input.error_text = "Некорректная ссылка"
            self.download_btn.disabled = True
            self.preview_card.visible = False
        else:
            self.url_input.error_text = None
            self.download_btn.disabled = False
            # Запускаем загрузку превью в отдельном потоке
            self.start_preview_loading(val)
        self.update()

    def start_preview_loading(self, url):
        # Показываем Скелетон
        self.preview_card.visible = True
        self.skeleton.visible = True
        self.preview_img.visible = False
        self.video_title.value = "Загрузка информации..."
        self.update()

        def load_task():
            try:
                info = self.downloader_logic.get_video_info(url)
                # Возвращаемся в UI поток для обновления
                self.video_title.value = info.get('title', 'Video')
                self.preview_img.src = info.get('thumbnail', '')
                self.skeleton.visible = False
                self.preview_img.visible = True
                self.update()
            except Exception as e:
                self.video_title.value = "Ошибка получения данных"
                self.skeleton.visible = True
                self.update()

        threading.Thread(target=load_task, daemon=True).start()

    def add_to_queue(self, e):
        if self.url_input.error_text or not self.url_input.value: return
        self.download_queue.append({
            'url': self.url_input.value,
            'quality': self.quality_dd.value,
            'audio_only': self.audio_switch.value,
            'playlist': self.playlist_switch.value
        })
        self.url_input.value = ""
        self.preview_card.visible = False # Скрываем превью после добавления
        self.update_queue_ui()
        self.show_msg("Добавлено в очередь")
        if not self.is_processing: threading.Thread(target=self.process_queue, daemon=True).start()

    def update_queue_ui(self):
        count = len(self.download_queue)
        self.queue_btn.text = f"В очереди: {count}"
        self.queue_btn.visible = count > 0
        
        self.queue_list_view.controls.clear()
        if not self.download_queue:
            self.queue_list_view.controls.append(ft.Text("Очередь пуста", color=Colors.GREY))
        else:
            for i, item in enumerate(self.download_queue):
                # Определяем статус для карточки
                status = "waiting"
                if i == 0 and self.is_processing:
                    status = "downloading"
                
                self.queue_list_view.controls.append(
                    QueueItem(i, item['url'], item['quality'], status, self.remove_from_queue)
                )
        self.page.update()

    def remove_from_queue(self, idx):
        if 0 <= idx < len(self.download_queue):
            del self.download_queue[idx]
            self.update_queue_ui()

    def show_queue_modal(self, e):
        is_dark = self.app_state.theme_mode == "dark"
        self.queue_bottom_sheet.content.bgcolor = Colors.GREY_900 if is_dark else Colors.WHITE
        self.page.bottom_sheet = self.queue_bottom_sheet
        self.queue_bottom_sheet.open = True
        self.page.update()

    def cancel_current(self, e):
        if self.current_downloader: self.current_downloader.cancel()

    def process_queue(self):
        self.is_processing = True
        while self.download_queue:
            task = self.download_queue[0]
            self.update_queue_ui()
            
            self.cancel_btn.visible = True
            self.status_text.value = f"Загрузка..."
            self.progress_bar.value = None
            self.page.update()

            self.current_downloader = VideoDownloader(self.on_progress)
            
            try:
                final_filename = self.current_downloader.download(
                    task['url'], self.app_state.download_path, 
                    quality=task['quality'], audio_only=task['audio_only'], allow_playlist=task['playlist']
                )
                
                # Добавляем в историю
                info = self.downloader_logic.get_video_info(task['url'])
                self.app_state.add_history_item({
                    "title": info.get('title', 'Видео'), 
                    "author": info.get('uploader', 'YouTube'),
                    "thumb": info.get('thumbnail', ''), 
                    "path": self.app_state.download_path,            
                    "file_path": final_filename,      
                    "url": task['url']                
                })
                self.show_msg("✅ Готово!", Colors.GREEN_700)
                
                # ОТКРЫТИЕ ПАПКИ ЕСЛИ НУЖНО
                if self.open_folder_switch.value:
                    open_path(self.app_state.download_path)
                
            except DownloadCancelled: self.show_msg("⏹️ Отменено", Colors.ORANGE_700)
            except Exception as ex: self.show_msg(f"❌ Ошибка: {str(ex)[:50]}", Colors.RED_700)
            finally:
                self.current_downloader = None
                self.speed_text.value = "0 MB/s"
                self.progress_bar.value = 0
                if self.download_queue: self.download_queue.pop(0)
                self.update_queue_ui()
        
        self.is_processing = False
        self.cancel_btn.visible = False
        self.status_text.value = "Очередь пуста"
        self.page.update()

    def on_progress(self, d):
        if d['status'] == 'downloading':
            try:
                p = d.get('downloaded_bytes', 0) / (d.get('total_bytes') or d.get('total_bytes_estimate', 1))
                self.progress_bar.value = p
                self.status_text.value = f"{p*100:.1f}%"
                self.speed_text.value = d.get('_speed_str', '--')
                self.size_text.value = d.get('_total_bytes_str', '--')
                self.page.update()
            except: pass
        elif d['status'] == 'finished':
            self.progress_bar.value = 1.0
            self.status_text.value = "Сборка..."
            self.page.update()

    def show_msg(self, text, color=Colors.BLUE_ACCENT):
        self.page.snack_bar = ft.SnackBar(content=ft.Text(text), bgcolor=color)
        self.page.snack_bar.open = True
        self.page.update()