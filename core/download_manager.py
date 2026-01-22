import threading
import time
import os
from dataclasses import dataclass, field
from typing import List, Optional, Callable, Dict, Any
from core.logic import VideoDownloader, DownloadCancelled

@dataclass
class DownloadTask:
    url: str
    save_path: str
    options: Dict[str, Any] = field(default_factory=dict)
    status: str = "waiting" # waiting, downloading, finished, error, cancelled
    progress: float = 0.0
    speed: str = ""
    eta: str = ""
    error_msg: str = ""
    title: str = "" # For display in queue
    thumb: str = ""

class DownloadManager:
    def __init__(self, app_state):
        self.app_state = app_state
        self.queue: List[DownloadTask] = []
        self.is_processing = False
        self.is_paused = False
        self.current_downloader: Optional[VideoDownloader] = None
        self._logic = VideoDownloader(None) # For fetching info
        
        # Callbacks
        self.on_queue_update: Optional[Callable] = None
        self.on_progress: Optional[Callable[[DownloadTask], None]] = None
        self.on_status_change: Optional[Callable[[str, str], None]] = None # msg, color
        self.on_clipboard_found: Optional[Callable[[str], None]] = None
        
        # Clipboard thread
        self._clip_thread_running = True
        
    def set_callbacks(self, on_queue_update=None, on_progress=None, on_status_change=None, on_clipboard_found=None):
        self.on_queue_update = on_queue_update
        self.on_progress = on_progress
        self.on_status_change = on_status_change
        self.on_clipboard_found = on_clipboard_found

    def add_task(self, url: str, options: dict, title: str = "", thumb: str = ""):
        task = DownloadTask(
            url=url, 
            save_path=self.app_state.download_path,
            options=options,
            title=title,
            thumb=thumb
        )
        self.queue.append(task)
        if self.on_queue_update:
            self.on_queue_update()
            
        if not self.is_processing and not self.is_paused:
            threading.Thread(target=self._process_queue, daemon=True).start()

    def remove_task(self, index: int):
        if 0 <= index < len(self.queue):
            del self.queue[index]
            if self.on_queue_update:
                self.on_queue_update()

    def move_task(self, from_idx: int, to_idx: int):
        if 0 <= from_idx < len(self.queue) and 0 <= to_idx < len(self.queue):
            self.queue[from_idx], self.queue[to_idx] = self.queue[to_idx], self.queue[from_idx]
            if self.on_queue_update:
                self.on_queue_update()

    def clear_queue(self):
        if self.is_processing and self.queue:
            # Keep currently running task
            self.queue = [self.queue[0]]
        else:
            self.queue = []
        if self.on_queue_update:
            self.on_queue_update()

    def toggle_pause(self, paused: bool):
        self.is_paused = paused
        if not self.is_paused and not self.is_processing and self.queue:
            threading.Thread(target=self._process_queue, daemon=True).start()

    def cancel_current(self):
        if self.current_downloader:
            self.current_downloader.cancel()

    def get_video_info(self, url):
        """Bloacking call to get info, likely run in a thread by UI"""
        return self._logic.get_video_info(url)

    def start_clipboard_monitor(self, page_clipboard_getter: Callable):
        threading.Thread(target=self._monitor_loop, args=(page_clipboard_getter,), daemon=True).start()

    def _process_queue(self):
        self.is_processing = True
        
        while self.queue:
            if self.is_paused:
                break
                
            task = self.queue[0]
            task.status = "downloading"
            if self.on_queue_update: self.on_queue_update()
            
            if self.on_status_change:
                self.on_status_change(self.app_state.get_str("status_downloading"), "blue")

            # Create downloader instance
            def progress_hook(d):
                self._update_task_progress(task, d)
                
            self.current_downloader = VideoDownloader(progress_hook)
            
            try:
                # Prepare args from options
                opts = task.options
                downloaded_files = self.current_downloader.download(
                    task.url, task.save_path,
                    quality=opts.get('quality', 'best'),
                    audio_only=opts.get('audio_only', False),
                    audio_format=opts.get('audio_format', 'mp3'),
                    audio_bitrate=opts.get('audio_bitrate', '192'),
                    allow_playlist=opts.get('playlist', False),
                    custom_filename=opts.get('filename'),
                    embed_meta=self.app_state.embed_meta,
                    download_subs=opts.get('subs', False),
                    use_sponsor_block=opts.get('sponsor_block', False),
                    playlist_items=opts.get('playlist_items')
                )
                
                # Success
                task.status = "finished"
                task.progress = 1.0
                
                # Add to history
                for file_path in downloaded_files:
                    title = os.path.basename(file_path)
                    self.app_state.add_history_item({
                        "title": title,
                        "author": "YouTube", 
                        "thumb": task.thumb,
                        "path": task.save_path,            
                        "file_path": file_path,      
                        "url": task.url                
                    })
                
                if self.on_status_change:
                    self.on_status_change(self.app_state.get_str("status_finished"), "green")
                    
            except DownloadCancelled:
                task.status = "cancelled"
                if self.on_status_change:
                    self.on_status_change("Cancelled", "orange")
            except Exception as e:
                task.status = "error"
                task.error_msg = str(e)
                if self.on_status_change:
                    self.on_status_change(f"Error: {str(e)[:50]}", "red")
            finally:
                self.current_downloader = None
                # Remove finished task
                if self.queue and self.queue[0] == task:
                     self.queue.pop(0)
                
                if self.on_queue_update: self.on_queue_update()
        
        self.is_processing = False
        if self.on_status_change:
            self.on_status_change(self.app_state.get_str("status_ready"), None)

    def _update_task_progress(self, task, d):
        if d['status'] == 'downloading':
            try:
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 1)
                downloaded = d.get('downloaded_bytes', 0)
                task.progress = downloaded / total
                task.speed = d.get('_speed_str', '--')
                task.eta = d.get('_eta_str', '--:--')
                
                if self.on_progress:
                    self.on_progress(task)
            except: pass
        elif d['status'] == 'finished':
            task.progress = 1.0
            if self.on_progress:
                self.on_progress(task)

    def _monitor_loop(self, get_clipboard_func):
        last_val = ""
        while self._clip_thread_running:
            try:
                if self.app_state.monitor_clipboard:
                    val = get_clipboard_func() # This needs to be thread-safe or handled correctly by Flet
                    if val and isinstance(val, str):
                        val = val.strip()
                        if val != last_val:
                            last_val = val
                            if "youtube.com" in val or "youtu.be" in val:
                                if self.on_clipboard_found:
                                    self.on_clipboard_found(val)
            except:
                pass
            time.sleep(2)
