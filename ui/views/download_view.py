import flet as ft
import threading
import os
import re
import time
from flet import Icons, Colors, MainAxisAlignment
from core.logic import VideoDownloader, DownloadCancelled
from core.utils import open_path
from ui.theme import ThemeColors, DesignSystem
from ui.components import StyledTextField, PrimaryButton, StatBadge, QueueItem

class DownloadView(ft.Column):
    def __init__(self, page: ft.Page, app_state):
        super().__init__(
            spacing=15,
            expand=True,
            scroll=ft.ScrollMode.AUTO
        )
        self.page = page
        self.app_state = app_state
        self.download_queue = []
        self.is_processing = False
        self.queue_paused = False
        self.current_downloader = None
        self.downloader_logic = VideoDownloader(None)
        
        self.playlist_entries = []
        self.selected_indices = []

        self._setup_ui()

    def _setup_ui(self):
        self.paste_btn = ft.IconButton(Icons.PASTE_ROUNDED, tooltip="Paste", icon_color=ThemeColors.PRIMARY, on_click=self.paste_from_clipboard)
        self.url_input = StyledTextField(
            self.app_state.get_str("url_label"), 
            self.app_state.get_str("url_hint"), 
            Icons.LINK_ROUNDED, 
            on_change=self.validate_input, 
            suffix=self.paste_btn
        )
        
        self.filename_input = StyledTextField(
            "Имя файла (опционально)", 
            "MyVideo", 
            Icons.DRIVE_FILE_RENAME_OUTLINE_ROUNDED, 
            visible=False
        )

        self.preview_img = ft.Image(src="", width=120, height=70, fit="cover", border_radius=12, visible=False)
        self.skeleton = ft.Container(
            width=120, height=70, 
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE), 
            border_radius=12, 
            visible=False, 
            animate_opacity=500,
            alignment=ft.alignment.center,
            content=ft.Icon(Icons.IMAGE_NOT_SUPPORTED_ROUNDED, color=ft.Colors.with_opacity(0.2, ft.Colors.WHITE))
        )
        self.video_title = ft.Text("", weight="bold", size=14, max_lines=2, overflow="ellipsis", color=ThemeColors.TEXT_MAIN)
        
        self.preview_card = ft.Container(
            visible=False, 
            padding=15, 
            border_radius=20, 
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
            content=ft.Row([
                ft.Stack([self.skeleton, self.preview_img]), 
                ft.Column([self.video_title], expand=True)
            ])
        )

        self.select_videos_btn = ft.ElevatedButton(
            "Выбрать видео", 
            icon=Icons.LIST_ALT_ROUNDED, 
            visible=False,
            on_click=self.open_playlist_dialog,
            style=ft.ButtonStyle(bgcolor=ft.Colors.with_opacity(0.1, ThemeColors.PRIMARY), color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=12))
        )

        self.quality_dd = ft.Dropdown(value="best", options=[ft.dropdown.Option("best", self.app_state.get_str("quality_best"))], border_radius=15, expand=True, text_size=13, border_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE30))
        self.audio_format_dd = ft.Dropdown(value="mp3", options=[ft.dropdown.Option(k) for k in ["mp3", "m4a", "wav"]], width=80, text_size=12, content_padding=5, visible=False, border_radius=10)
        self.audio_bitrate_dd = ft.Dropdown(value="192", options=[ft.dropdown.Option(k, f"{k}k") for k in ["128", "192", "320"]], width=80, text_size=12, content_padding=5, visible=False, border_radius=10)
        
        self.audio_switch = ft.Switch(label=self.app_state.get_str("audio_only_switch"), value=False, on_change=self.toggle_audio_options, active_color=ThemeColors.PRIMARY)
        self.audio_options_row = ft.Row([self.audio_format_dd, self.audio_bitrate_dd], visible=False, spacing=5)

        self.subs_switch = ft.Switch(label=self.app_state.get_str("subs_switch"), value=self.app_state.download_subs, active_color=ThemeColors.PRIMARY)
        self.playlist_switch = ft.Switch(label=self.app_state.get_str("playlist_switch"), value=False, active_color=ThemeColors.PRIMARY)
        self.open_folder_switch = ft.Checkbox(label=self.app_state.get_str("open_folder_check"), value=False, label_style=ft.TextStyle(size=12, color=ThemeColors.TEXT_DIM), fill_color=ThemeColors.PRIMARY)

        self.download_btn = PrimaryButton(self.app_state.get_str("add_btn"), Icons.ADD_TO_PHOTOS_ROUNDED, self.add_to_queue)
        
        self.speed_text = ft.Text("0 MB/s", size=13, weight="bold", color=ThemeColors.TEXT_MAIN)
        self.eta_text = ft.Text("--:--", size=13, weight="bold", color=ThemeColors.TEXT_MAIN)
        self.progress_bar = ft.ProgressBar(value=0, color=ThemeColors.PRIMARY, height=8, border_radius=10)
        self.status_text = ft.Text(self.app_state.get_str("status_ready"), size=12, color=ThemeColors.TEXT_DIM)
        self.cancel_btn = ft.Container(
            content=ft.IconButton(Icons.STOP, icon_color=ft.Colors.RED_400, on_click=self.cancel_current, tooltip="Stop Download"),
            visible=False
        )
        
        self.queue_btn = ft.TextButton(text="", icon=Icons.LIST_ROUNDED, icon_color=ThemeColors.PRIMARY_LIGHT, visible=False, on_click=self.show_queue_modal)

        self.progress_container = ft.Container(
            visible=True, padding=20, border_radius=25, 
            bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.WHITE),
            border=ft.border.all(1, ft.Colors.with_opacity(0.05, ft.Colors.WHITE)),
            content=ft.Column([
                ft.Row([
                    ft.Text("PROGRESS", size=10, weight="bold", color=ThemeColors.TEXT_DIM),
                    self.queue_btn
                ], alignment=MainAxisAlignment.SPACE_BETWEEN), 
                ft.Row([
                    StatBadge(Icons.SPEED_ROUNDED, "SPEED", self.speed_text), 
                    StatBadge(Icons.TIMER_ROUNDED, self.app_state.get_str("eta"), self.eta_text)
                ], spacing=15),
                ft.Container(self.progress_bar, padding=ft.padding.symmetric(vertical=5), shadow=DesignSystem.SHADOW_GLOW),
                ft.Row([self.status_text, self.cancel_btn], alignment=MainAxisAlignment.SPACE_BETWEEN)
            ])
        )

        self.controls = [
            ft.Container(
                padding=ft.padding.only(right=20, left=5, top=5, bottom=5),
                content=ft.Column([
                    self.url_input, 
                    self.filename_input,
                    self.preview_card,
                    self.select_videos_btn,
                    ft.Row([self.quality_dd]),
                    ft.Row([self.audio_switch, self.audio_options_row], alignment=MainAxisAlignment.SPACE_BETWEEN),
                    ft.Row([self.playlist_switch, self.subs_switch], alignment=MainAxisAlignment.SPACE_BETWEEN),
                    self.open_folder_switch,
                    self.download_btn, self.progress_container
                ], spacing=15)
            )
        ]

        self.queue_list_view = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
        self.pause_queue_switch = ft.Switch(label="Pause Queue", value=False, on_change=self.toggle_queue_pause, active_color=ThemeColors.PRIMARY)
        
        self.queue_bottom_sheet = ft.BottomSheet(
            ft.Container(
                ft.Column([
                    ft.Row([
                        ft.Text(self.app_state.get_str("queue_title"), size=20, weight="bold"),
                        ft.Row([
                             self.pause_queue_switch,
                             ft.IconButton(Icons.DELETE_SWEEP_ROUNDED, tooltip=self.app_state.get_str("clear_queue"), on_click=self.clear_queue_all, icon_color=ft.Colors.RED_400)
                        ])
                    ], alignment=MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
                    ft.Container(self.queue_list_view, height=300), 
                    PrimaryButton("Close", Icons.CLOSE_ROUNDED, lambda _: self.page.close_bottom_sheet())
                ]),
                padding=25,
                bgcolor=ThemeColors.BG_CARD,
                border_radius=ft.border_radius.only(top_left=30, top_right=30),
                border=ft.border.only(top=ft.border.BorderSide(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)))
            )
        )

        
        self.playlist_dialog = ft.AlertDialog(
            title=ft.Text("Выберите видео"),
            content=ft.Container(width=400, height=300),
            actions=[
                ft.TextButton("Отмена", on_click=lambda e: self.close_dialog(False)),
                ft.TextButton("Выбрать", on_click=lambda e: self.close_dialog(True)),
            ],
            modal=True
        )

        # Запуск мониторинга буфера
        threading.Thread(target=self._monitor_loop, daemon=True).start()

    def update_locale(self):
        self.url_input.label = self.app_state.get_str("url_label")
        self.url_input.hint_text = self.app_state.get_str("url_hint")
        self.quality_dd.options[0].text = self.app_state.get_str("quality_best")
        self.audio_switch.label = self.app_state.get_str("audio_only_switch")
        self.playlist_switch.label = self.app_state.get_str("playlist_switch")
        self.subs_switch.label = self.app_state.get_str("subs_switch")
        self.open_folder_switch.label = self.app_state.get_str("open_folder_check")
        
        self.download_btn.content.content.controls[1].value = self.app_state.get_str("add_btn")
        self.status_text.value = self.app_state.get_str("status_ready")
        self.queue_bottom_sheet.content.content.controls[0].controls[0].value = self.app_state.get_str("queue_title")
        self.update()

    def toggle_queue_pause(self, e):
        self.queue_paused = self.pause_queue_switch.value
        if not self.queue_paused and not self.is_processing and self.download_queue:
            threading.Thread(target=self.process_queue, daemon=True).start()

    def move_item_up(self, index):
        if index > 0 and index < len(self.download_queue):
            if self.is_processing and index == 1: return 
            self.download_queue[index], self.download_queue[index-1] = self.download_queue[index-1], self.download_queue[index]
            self.update_queue_ui()

    def move_item_down(self, index):
        if index < len(self.download_queue) - 1:
            if self.is_processing and index == 0: return
            self.download_queue[index], self.download_queue[index+1] = self.download_queue[index+1], self.download_queue[index]
            self.update_queue_ui()

    def update_queue_ui(self):
        count = len(self.download_queue)
        self.queue_btn.text = f"{count}"
        self.queue_btn.visible = count > 0
        
        self.queue_list_view.controls.clear()
        if not self.download_queue:
            self.queue_list_view.controls.append(ft.Text(self.app_state.get_str("queue_empty"), color=Colors.GREY))
        else:
            for i, item in enumerate(self.download_queue):
                status = "waiting"
                if i == 0 and self.is_processing: status = "downloading"
                self.queue_list_view.controls.append(
                    QueueItem(i, item, status, self.remove_from_queue, self.move_item_up, self.move_item_down, count)
                )
        self.page.update()

    def toggle_audio_options(self, e):
        visible = self.audio_switch.value
        self.audio_options_row.visible = visible
        self.audio_format_dd.visible = visible
        self.audio_bitrate_dd.visible = visible
        self.quality_dd.disabled = visible
        self.update()

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
            self.filename_input.visible = False
            self.select_videos_btn.visible = False
        elif not (val.startswith("http://") or val.startswith("https://")):
            self.url_input.error_text = self.app_state.get_str("error_url")
            self.download_btn.disabled = True
            self.preview_card.visible = False
            self.filename_input.visible = False
            self.select_videos_btn.visible = False
        else:
            self.url_input.error_text = None
            self.download_btn.disabled = False
            self.start_preview_loading(val)
        self.update()

    def start_preview_loading(self, url):
        self.preview_card.visible = True
        self.skeleton.visible = True
        self.preview_img.visible = False
        self.filename_input.visible = False
        self.select_videos_btn.visible = False
        self.video_title.value = self.app_state.get_str("quality_loading")
        self.quality_dd.options = [ft.dropdown.Option("best", self.app_state.get_str("quality_best"))]
        self.quality_dd.value = "best"
        self.update()

        def load_task():
            try:
                # ВЫЗОВ БЕЗ ПРОКСИ/КУКИ
                info = self.downloader_logic.get_video_info(url)
                
                self.video_title.value = info.get('title', 'Video')
                
                thumb_url = info.get('thumbnail')
                if thumb_url:
                    self.preview_img.src = thumb_url
                    self.preview_img.visible = True
                    self.skeleton.visible = False
                else:
                    self.preview_img.visible = False
                    self.skeleton.visible = True 

                if 'entries' in info:
                    self.playlist_entries = list(info['entries'])
                    self.select_videos_btn.text = f"Выбрано: {len(self.playlist_entries)} / {len(self.playlist_entries)}"
                    self.select_videos_btn.visible = True
                    self.playlist_switch.value = True
                    self.selected_indices = []
                else:
                    self.select_videos_btn.visible = False
                    self.playlist_entries = []

                safe_title = re.sub(r'[<>:"/\\|?*]', '', info.get('title', ''))
                self.filename_input.value = safe_title
                self.filename_input.visible = True

                formats = info.get('formats', [])
                resolutions = set()
                for f in formats:
                    if f.get('vcodec') != 'none' and f.get('height'):
                        resolutions.add(f.get('height'))
                
                sorted_res = sorted(list(resolutions), reverse=True)
                if sorted_res:
                    new_options = [ft.dropdown.Option("best", self.app_state.get_str("quality_best"))]
                    for res in sorted_res:
                        new_options.append(ft.dropdown.Option(f"{res}p", f"{res}p"))
                    self.quality_dd.options = new_options

                self.update()
            except Exception as e:
                self.video_title.value = self.app_state.get_str("error_generic") + f": {str(e)[:20]}"
                self.skeleton.visible = True
                self.preview_img.visible = False
                self.update()

        threading.Thread(target=load_task, daemon=True).start()

    def open_playlist_dialog(self, e):
        if not self.playlist_entries: return
        
        checkboxes = []
        for i, entry in enumerate(self.playlist_entries):
            idx = i + 1
            if not entry: continue
            title = entry.get('title', f'Video {idx}')
            is_checked = (not self.selected_indices) or (str(idx) in self.selected_indices)
            checkboxes.append(
                ft.Checkbox(label=f"{idx}. {title}", value=is_checked, data=str(idx))
            )
            
        list_view = ft.ListView(controls=checkboxes, expand=True)
        self.playlist_dialog.content = list_view
        self.page.dialog = self.playlist_dialog
        self.playlist_dialog.open = True
        self.page.update()

    def close_dialog(self, save):
        if save:
            lv = self.playlist_dialog.content
            selected = []
            for cb in lv.controls:
                if cb.value:
                    selected.append(cb.data)
            
            if len(selected) == len(self.playlist_entries) or len(selected) == 0:
                self.selected_indices = []
                self.select_videos_btn.text = f"Все ({len(self.playlist_entries)})"
            else:
                self.selected_indices = selected
                self.select_videos_btn.text = f"Выбрано: {len(selected)}"
        
        self.playlist_dialog.open = False
        self.page.update()

    def add_to_queue(self, e):
        if self.url_input.error_text or not self.url_input.value: return
        
        playlist_str = ",".join(self.selected_indices) if self.selected_indices else None

        self.download_queue.append({
            'url': self.url_input.value,
            'quality': self.quality_dd.value,
            'audio_only': self.audio_switch.value,
            'audio_format': self.audio_format_dd.value,
            'audio_bitrate': self.audio_bitrate_dd.value,
            'playlist': self.playlist_switch.value,
            'filename': self.filename_input.value.strip(),
            'subs': self.subs_switch.value,
            'playlist_items': playlist_str, 
            'sponsor_block': self.app_state.sponsor_block,
            'thumb': self.preview_img.src if self.preview_img.visible else ""
        })
        self.url_input.value = ""
        self.filename_input.value = ""
        self.filename_input.visible = False
        self.preview_card.visible = False
        self.select_videos_btn.visible = False
        self.selected_indices = []
        self.update_queue_ui()
        self.show_msg("Added to queue")
        
        if not self.is_processing and not self.queue_paused: 
            threading.Thread(target=self.process_queue, daemon=True).start()

    def process_queue(self):
        self.is_processing = True
        while self.download_queue:
            if self.queue_paused: break

            task = self.download_queue[0]
            self.update_queue_ui()
            
            self.cancel_btn.visible = True
            self.status_text.value = self.app_state.get_str("status_downloading")
            self.page.update()

            self.current_downloader = VideoDownloader(self.on_progress)
            
            try:
                # ВЫЗОВ БЕЗ ПРОКСИ/КУКИ
                downloaded_files = self.current_downloader.download(
                    task['url'], self.app_state.download_path, 
                    quality=task['quality'], 
                    audio_only=task['audio_only'],
                    audio_format=task.get('audio_format', 'mp3'),
                    audio_bitrate=task.get('audio_bitrate', '192'),
                    allow_playlist=task['playlist'],
                    custom_filename=task.get('filename'),
                    embed_meta=self.app_state.embed_meta,
                    download_subs=task.get('subs', False),
                    use_sponsor_block=task.get('sponsor_block', False),
                    playlist_items=task.get('playlist_items')
                )
                
                for file_path in downloaded_files:
                    title = os.path.basename(file_path)
                    self.app_state.add_history_item({
                        "title": title,
                        "author": "YouTube", 
                        "thumb": task.get('thumb', ""),
                        "path": self.app_state.download_path,            
                        "file_path": file_path,      
                        "url": task['url']                
                    })
                
                self.show_msg(self.app_state.get_str("status_finished"), Colors.GREEN_700)
                
                if self.open_folder_switch.value:
                    open_path(self.app_state.download_path)
                
            except DownloadCancelled: self.show_msg("Cancelled", Colors.ORANGE_700)
            except Exception as ex: self.show_msg(f"Error: {str(ex)[:50]}", Colors.RED_700)
            finally:
                self.current_downloader = None
                self.speed_text.value = "0 MB/s"
                self.eta_text.value = "--:--"
                self.progress_bar.value = 0
                if self.download_queue: self.download_queue.pop(0)
                self.update_queue_ui()
        
        self.is_processing = False
        self.cancel_btn.visible = False
        self.status_text.value = self.app_state.get_str("status_ready")
        self.page.update()

    def on_progress(self, d):
        if d['status'] == 'downloading':
            try:
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 1)
                downloaded = d.get('downloaded_bytes', 0)
                p = downloaded / total
                
                self.progress_bar.value = p
                self.status_text.value = f"{p*100:.1f}%"
                self.speed_text.value = d.get('_speed_str', '--')
                self.eta_text.value = d.get('_eta_str', '--:--')
                self.page.update()
            except: pass
        elif d['status'] == 'finished':
            self.progress_bar.value = 1.0
            self.status_text.value = self.app_state.get_str("status_processing")
            self.page.update()

    def show_msg(self, text, color=Colors.BLUE_ACCENT):
        self.page.snack_bar = ft.SnackBar(content=ft.Text(text), bgcolor=color)
        self.page.snack_bar.open = True
        self.page.update()

    def remove_from_queue(self, idx):
        if 0 <= idx < len(self.download_queue):
            del self.download_queue[idx]
            self.update_queue_ui()

    def clear_queue_all(self, e):
        if self.is_processing and self.download_queue:
            self.download_queue = [self.download_queue[0]]
        else:
            self.download_queue = []
        self.update_queue_ui()

    def show_queue_modal(self, e):
        is_dark = self.app_state.theme_mode == "dark"
        self.queue_bottom_sheet.content.bgcolor = Colors.GREY_900 if is_dark else Colors.WHITE
        self.page.bottom_sheet = self.queue_bottom_sheet
        self.queue_bottom_sheet.open = True
        self.page.update()

    def cancel_current(self, e):
        if self.current_downloader: self.current_downloader.cancel()

    def _monitor_loop(self):
        last_val = ""
        while True:
            try:
                if self.app_state.monitor_clipboard:
                    # Пытаемся получить текст из буфера (синхронно)
                    # Note: get_clipboard returns None or string
                    val = self.page.get_clipboard() 
                    if val and isinstance(val, str):
                        val = val.strip()
                        if val != last_val:
                            last_val = val
                            # Проверяем, что это не то, что уже в поле, и похоже на ссылку youtube
                            if val != self.url_input.value and ("youtube.com" in val or "youtu.be" in val):
                                self.url_input.value = val
                                self.validate_input(None)
                                self.update()
                                self.show_msg(self.app_state.get_str("status_ready") + " (Clipboard detected)", Colors.GREEN)
            except Exception as e:
                # Игнорируем ошибки (например, если страница закрылась или таймаут)
                # print(f"Clip error: {e}") 
                pass
            
            time.sleep(2)