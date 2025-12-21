import yt_dlp
import os

class DownloadCancelled(Exception):
    pass

class VideoDownloader:
    def __init__(self, progress_callback):
        self.progress_callback = progress_callback
        self.is_cancelled = False

    def cancel(self):
        """Устанавливает флаг отмены"""
        self.is_cancelled = True

    def _progress_hook(self, d):
        """Внутренний хук для проверки флага отмены и вызова колбэка"""
        if self.is_cancelled:
            raise DownloadCancelled("Загрузка отменена пользователем")
        if self.progress_callback:
            self.progress_callback(d)

    def get_video_info(self, url, proxy=None, cookies=None):
        """Получает метаданные видео с учетом прокси и куки"""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': 'in_playlist',
        }
        if proxy: ydl_opts['proxy'] = proxy
        if cookies: ydl_opts['cookiefile'] = cookies

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)

    def download(self, url, save_path, quality="best", audio_only=False, 
                 audio_format="mp3", audio_bitrate="192", 
                 allow_playlist=False, proxy=None, cookies_path=None,
                 custom_filename=None): # <-- Новый аргумент
        """
        Основной метод загрузки. Возвращает список путей к скачанным файлам.
        """
        self.is_cancelled = False
        
        postprocessors = []
        ydl_format = "best"

        if audio_only:
            ydl_format = 'bestaudio/best'
            postprocessors = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': audio_format,
                'preferredquality': audio_bitrate,
            }]
        else:
            format_map = {
                "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
                "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
                "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
                "best": "best"
            }
            ydl_format = format_map.get(quality, "best")

        # Логика формирования имени файла
        if custom_filename:
            # Если разрешен плейлист, добавляем индекс, чтобы файлы не перезатирались
            if allow_playlist:
                tmpl = f"{custom_filename} - %(playlist_index)s.%(ext)s"
            else:
                tmpl = f"{custom_filename}.%(ext)s"
        else:
            tmpl = "%(title)s.%(ext)s"

        ydl_opts = {
            'format': ydl_format,
            'progress_hooks': [self._progress_hook],
            'outtmpl': os.path.join(save_path, tmpl), # Используем шаблон
            'noplaylist': not allow_playlist,
            'postprocessors': postprocessors,
            'quiet': True,
            'no_warnings': True,
            'no_color': True,
            'ignoreerrors': True if allow_playlist else False,
            'restrictfilenames': True,
            'proxy': proxy if proxy else None,
            'cookiefile': cookies_path if cookies_path and os.path.exists(cookies_path) else None,
        }

        downloaded_files = []

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            if 'entries' in info:
                for entry in info['entries']:
                    if not entry: continue
                    if 'requested_downloads' in entry:
                        for d in entry['requested_downloads']:
                            downloaded_files.append(d['filepath'])
                    else:
                        try:
                            downloaded_files.append(ydl.prepare_filename(entry))
                        except: pass
            else:
                if 'requested_downloads' in info:
                    downloaded_files.append(info['requested_downloads'][0]['filepath'])
                else:
                    downloaded_files.append(ydl.prepare_filename(info))
            
            return downloaded_files