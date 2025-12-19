import flet as ft
import threading
import os
import subprocess
import platform
from collections import deque
from flet import Icons, Colors, ThemeMode, MainAxisAlignment

# Импорт логики и компонентов
from core.logic import VideoDownloader, DownloadCancelled
from ui.components import StyledTextField, PrimaryButton, StatBadge, HistoryCard, SettingTile, QueueItem

def main(page: ft.Page):
    # Конфигурация окна
    page.title = "YT LOADER PRO v2.1"
    page.theme_mode = ThemeMode.DARK
    page.window_width = 500
    page.window_height = 900
    page.bgcolor = "#0F111A"
    page.padding = 0

    # --- Состояние ---
    store = page.client_storage
    state = {
        "path": store.get("download_path") or os.path.join(os.path.expanduser("~"), "Downloads"),
        "history": store.get("history") or [],
        "theme": store.get("theme") or "dark"
    }

    page.theme_mode = ThemeMode.DARK if state["theme"] == "dark" else ThemeMode.LIGHT
    page.bgcolor = "#0F111A" if page.theme_mode == ThemeMode.DARK else "#F5F5F5"
    
    download_queue = [] 
    is_processing = False
    current_downloader = None 

    # --- Вспомогательные функции (ОС) ---
    def show_msg(text, color=Colors.BLUE_ACCENT):
        page.snack_bar = ft.SnackBar(content=ft.Text(text, weight="bold"), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    def open_path(path, is_file=False):
        """Универсальная открывалка файлов и папок"""
        if not path or not os.path.exists(path):
            show_msg("Файл или папка не найдены", Colors.RED_400)
            return
        
        try:
            target = path if is_file else (os.path.dirname(path) if os.path.isfile(path) else path)
            
            if platform.system() == "Windows":
                os.startfile(target)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", target])
            else:
                subprocess.Popen(["xdg-open", target])
        except Exception as e:
            show_msg(f"Ошибка открытия: {e}", Colors.RED_400)

    def copy_to_clipboard(text):
        if text:
            page.set_clipboard(text)
            show_msg("Ссылка скопирована")

    # --- Логика очереди ---
    def process_queue():
        nonlocal is_processing, current_downloader
        if is_processing or not download_queue: return
        is_processing = True
        
        while download_queue:
            task = download_queue[0]
            update_queue_ui()
            
            cancel_btn.visible = True
            status_text.value = f"Загрузка: {task['url'][:30]}..."
            progress_bar.value = None
            page.update()

            current_downloader = VideoDownloader(on_progress)
            final_filename = None
            
            try:
                final_filename = current_downloader.download(
                    task['url'], state["path"], 
                    quality=task['quality'], audio_only=task['audio_only'], 
                    allow_playlist=task['playlist']
                )
                
                info = downloader_logic.get_video_info(task['url'])
                new_entry = {
                    "title": info.get('title', 'Видео'), 
                    "author": info.get('uploader', 'YouTube'),
                    "thumb": info.get('thumbnail', ''), 
                    "path": state["path"],            
                    "file_path": final_filename,      
                    "url": task['url']                
                }
                
                state["history"].append(new_entry)
                if len(state["history"]) > 20: state["history"].pop(0)
                store.set("history", state["history"])
                
                show_msg("✅ Загрузка завершена!", Colors.GREEN_700)
                
            except DownloadCancelled: 
                show_msg("⏹️ Отменено", Colors.ORANGE_700)
            except Exception as ex: 
                show_msg(f"❌ Ошибка: {str(ex)[:50]}", Colors.RED_700)
            finally:
                current_downloader = None
                speed_text.value = "0 MB/s"
                progress_bar.value = 0
                
                if download_queue: download_queue.pop(0)
                update_queue_ui() 
                
                if not download_queue:
                    # ИСПРАВЛЕНИЕ: Вместо window_to_front просто разворачиваем окно, если свернуто
                    page.window_minimized = False
                    page.update()

        is_processing = False
        cancel_btn.visible = False
        status_text.value = "Очередь пуста"
        page.update()

    def add_to_queue(e):
        if url_input.error_text or not url_input.value:
            validate_input(None)
            return
        
        download_queue.append({
            'url': url_input.value,
            'quality': quality_dd.value,
            'audio_only': audio_switch.value,
            'playlist': playlist_switch.value
        })
        url_input.value = ""
        update_queue_ui()
        show_msg("Добавлено в очередь")
        if not is_processing: threading.Thread(target=process_queue, daemon=True).start()

    def remove_from_queue(idx):
        if 0 <= idx < len(download_queue):
            del download_queue[idx]
            update_queue_ui()
            show_msg("Удалено из очереди")

    # --- UI Очереди (BottomSheet) ---
    queue_list_view = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
    
    # ИСПРАВЛЕНИЕ: Colors.GREY_900 (было grey_900)
    queue_bottom_sheet = ft.BottomSheet(
        ft.Container(
            ft.Column([
                ft.Text("Очередь загрузки", size=20, weight="bold"),
                ft.Divider(),
                ft.Container(queue_list_view, height=300), 
                ft.ElevatedButton("Закрыть", on_click=lambda _: page.close_bottom_sheet())
            ]),
            padding=20,
            bgcolor=Colors.GREY_900 if state["theme"] == "dark" else Colors.WHITE,
            border_radius=ft.border_radius.only(top_left=20, top_right=20)
        )
    )

    def show_queue_modal(e):
        page.bottom_sheet = queue_bottom_sheet
        queue_bottom_sheet.open = True
        page.update()

    def update_queue_ui():
        count = len(download_queue)
        queue_btn.text = f"В очереди: {count}"
        queue_btn.visible = count > 0
        
        queue_list_view.controls.clear()
        if not download_queue:
            queue_list_view.controls.append(ft.Text("Очередь пуста", color=Colors.GREY))
        else:
            for i, item in enumerate(download_queue):
                is_active = (i == 0 and is_processing)
                item_ui = QueueItem(i, item['url'], item['quality'], lambda idx: remove_from_queue(idx))
                if is_active:
                    item_ui.border = ft.border.all(1, Colors.BLUE_ACCENT)
                    item_ui.bgcolor = Colors.with_opacity(0.1, Colors.BLUE_ACCENT)
                queue_list_view.controls.append(item_ui)
        
        page.update()

    # --- Логика Истории ---
    def delete_history_item(item):
        if item in state["history"]:
            state["history"].remove(item)
            store.set("history", state["history"])
            refresh_history()
            show_msg("Запись удалена")

    # --- UI Элементы ---
    async def paste_from_clipboard(e):
        text = await page.get_clipboard_async()
        if text:
            url_input.value = text
            validate_input(None)
            url_input.update()

    def validate_input(e):
        val = url_input.value.strip()
        if not val:
            url_input.error_text = None
            download_btn.disabled = False
        elif not (val.startswith("http://") or val.startswith("https://")):
            url_input.error_text = "Некорректная ссылка"
            download_btn.disabled = True
            preview_card.visible = False
        else:
            url_input.error_text = None
            download_btn.disabled = False
            load_preview(None)
        
        download_btn.content.opacity = 0.5 if download_btn.disabled else 1
        page.update()

    paste_btn = ft.IconButton(Icons.PASTE_ROUNDED, tooltip="Вставить", icon_color=Colors.BLUE_ACCENT, on_click=paste_from_clipboard)
    url_input = StyledTextField("URL Видео", "Ссылка...", Icons.LINK_ROUNDED, on_change=validate_input, suffix=paste_btn)

    def cancel_current(e):
        if current_downloader: current_downloader.cancel()

    speed_text = ft.Text("0 MB/s", size=13, weight="bold")
    eta_text = ft.Text("00:00", size=13, weight="bold")
    size_text = ft.Text("---", size=13, weight="bold")
    progress_bar = ft.ProgressBar(value=0, color=Colors.BLUE_ACCENT, height=6, border_radius=10)
    status_text = ft.Text("Готов", size=12, color=Colors.BLUE_GREY_400)
    
    queue_btn = ft.TextButton(
        text="", 
        icon=Icons.LIST_ROUNDED, 
        icon_color=Colors.ORANGE_ACCENT,
        style=ft.ButtonStyle(color=Colors.ORANGE_ACCENT),
        visible=False,
        on_click=show_queue_modal
    )

    def on_progress(d):
        if d['status'] == 'downloading':
            try:
                p = d.get('downloaded_bytes', 0) / (d.get('total_bytes') or d.get('total_bytes_estimate', 1))
                progress_bar.value = p
                status_text.value = f"{p*100:.1f}%"
                speed_text.value = d.get('_speed_str', '--')
                eta_text.value = d.get('_eta_str', '--')
                size_text.value = d.get('_total_bytes_str', '--')
                page.update()
            except: pass
        elif d['status'] == 'finished':
            progress_bar.value = 1.0
            status_text.value = "Сборка файла..."
            page.update()

    downloader_logic = VideoDownloader(None)
    
    def load_preview(e):
        if len(url_input.value) > 15 and not url_input.error_text:
            try:
                info = downloader_logic.get_video_info(url_input.value)
                video_title.value = info.get('title', 'Video')
                preview_img.src = info.get('thumbnail', '')
                preview_card.visible = True
                page.update()
            except: pass

    preview_img = ft.Image(src="", width=120, height=70, fit="cover", border_radius=10)
    video_title = ft.Text("", weight="bold", size=14, max_lines=2, overflow="ellipsis")
    preview_card = ft.Container(visible=False, padding=15, border_radius=20, bgcolor=Colors.with_opacity(0.05, Colors.WHITE),
                                content=ft.Row([preview_img, ft.Column([video_title], expand=True)]))

    quality_dd = ft.Dropdown(value="best", options=[ft.dropdown.Option(k,v) for k,v in {"best":"Макс.","1080p":"1080p","720p":"720p"}.items()], border_radius=12, expand=True)
    audio_switch = ft.Switch(label="MP3", value=False)
    playlist_switch = ft.Switch(label="Плейлист", value=False)
    
    download_btn = PrimaryButton("ДОБАВИТЬ", Icons.ADD_TO_PHOTOS_ROUNDED, add_to_queue)
    cancel_btn = ft.ElevatedButton("СТОП", icon=Icons.CANCEL, bgcolor=Colors.RED_700, color="white", visible=False, on_click=cancel_current)
    
    progress_container = ft.Container(visible=True, padding=20, border_radius=20, bgcolor=Colors.with_opacity(0.02, Colors.WHITE),
                                      content=ft.Column([
                                          ft.Row([queue_btn], alignment=MainAxisAlignment.END), 
                                          ft.Row([StatBadge(Icons.SPEED_ROUNDED, "СКОРОСТЬ", speed_text), StatBadge(Icons.SD_STORAGE_ROUNDED, "РАЗМЕР", size_text)], spacing=15),
                                          progress_bar,
                                          ft.Row([status_text, cancel_btn], alignment=MainAxisAlignment.SPACE_BETWEEN)
                                      ]))

    download_view = ft.Column([
        url_input, preview_card,
        ft.Row([quality_dd]),
        ft.Row([audio_switch, playlist_switch], alignment=MainAxisAlignment.SPACE_BETWEEN),
        download_btn, progress_container
    ], spacing=15, visible=True)

    # --- Настройки ---
    def toggle_theme(e):
        state["theme"] = "light" if state["theme"] == "dark" else "dark"
        store.set("theme", state["theme"])
        page.theme_mode = ThemeMode.LIGHT if state["theme"] == "light" else ThemeMode.DARK
        page.bgcolor = "#F5F5F5" if state["theme"] == "light" else "#0F111A"
        
        # ИСПРАВЛЕНИЕ: Colors.GREY_900 (было grey_900)
        queue_bottom_sheet.content.bgcolor = Colors.GREY_900 if state["theme"] == "dark" else Colors.WHITE
        page.update()

    def change_path_result(e):
        if e.path:
            state["path"] = e.path
            store.set("download_path", e.path)
            path_display.value = e.path
            page.update()

    path_picker = ft.FilePicker(on_result=change_path_result)
    page.overlay.append(path_picker)
    path_display = ft.Text(state["path"], size=12, color=Colors.BLUE_GREY_400, max_lines=1, overflow="ellipsis", width=200, text_align="right")

    def clear_history(e):
        state["history"] = []
        store.set("history", [])
        refresh_history()
        show_msg("История очищена")

    settings_view = ft.Column([
        ft.Text("Настройки", size=20, weight="bold"),
        SettingTile(Icons.DARK_MODE_ROUNDED, "Темная тема", ft.Switch(value=(state["theme"]=="dark"), on_change=toggle_theme)),
        SettingTile(Icons.FOLDER_ROUNDED, "Папка загрузок", ft.Row([path_display, ft.IconButton(Icons.EDIT_ROUNDED, on_click=lambda _: path_picker.get_directory_path())])),
        ft.Divider(),
        SettingTile(Icons.DELETE_SWEEP_ROUNDED, "История", ft.ElevatedButton("Очистить", bgcolor=Colors.RED_700, color="white", on_click=clear_history)),
    ], spacing=10, visible=False)

    # --- История (Обновленная) ---
    history_list = ft.ListView(expand=True, spacing=12)
    def refresh_history():
        history_list.controls.clear()
        if not state["history"]:
            history_list.controls.append(ft.Text("История пуста", text_align="center", color=Colors.GREY))
        for item in reversed(state["history"]):
            history_list.controls.append(HistoryCard(
                item,
                on_open_folder=lambda p: open_path(p, is_file=False),
                on_open_file=lambda p: open_path(p, is_file=True),
                on_copy_link=copy_to_clipboard,
                on_delete=delete_history_item
            ))
        page.update()

    history_view = ft.Column([ft.Text("Недавние", size=18, weight="bold"), history_list], visible=False, expand=True)

    # --- Навигация ---
    def change_tab(index):
        download_view.visible = (index == 0)
        history_view.visible = (index == 1)
        settings_view.visible = (index == 2)
        
        for i, btn in enumerate([nav_home, nav_hist, nav_sett]):
            btn.bgcolor = Colors.with_opacity(0.1, Colors.BLUE_ACCENT) if i == index else Colors.TRANSPARENT
        
        if index == 1: refresh_history()
        page.update()

    nav_home = ft.Container(content=ft.Icon(Icons.HOME_ROUNDED), padding=10, border_radius=10, on_click=lambda _: change_tab(0))
    nav_hist = ft.Container(content=ft.Icon(Icons.HISTORY_ROUNDED), padding=10, border_radius=10, on_click=lambda _: change_tab(1))
    nav_sett = ft.Container(content=ft.Icon(Icons.SETTINGS_ROUNDED), padding=10, border_radius=10, on_click=lambda _: change_tab(2))

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