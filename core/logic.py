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

    def get_video_info(self, url):
        """Получает метаданные видео"""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'best',
            # Игнорируем ошибки плейлистов при предпросмотре
            'extract_flat': 'in_playlist' 
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)

    def download(self, url, save_path, quality="best", audio_only=False, allow_playlist=False):
        """Основной метод загрузки"""
        self.is_cancelled = False
        
        # Настройка формата
        if audio_only:
            ydl_format = 'bestaudio/best'
            postprocessors = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            format_map = {
                "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
                "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
                "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
                "best": "best"
            }
            ydl_format = format_map.get(quality, "best")
            postprocessors = []

        ydl_opts = {
            'format': ydl_format,
            'progress_hooks': [self._progress_hook], # Используем наш хук с проверкой отмены
            'outtmpl': os.path.join(save_path, "%(title)s.%(ext)s"),
            'noplaylist': not allow_playlist,
            'postprocessors': postprocessors,
            'quiet': True,
            'no_warnings': True,
            'no_color': True,
            # Дополнительные настройки для стабильности
            'ignoreerrors': True if allow_playlist else False, 
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])