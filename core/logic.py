import yt_dlp
import os

class VideoDownloader:
    def __init__(self, progress_callback):
        self.progress_callback = progress_callback

    def get_video_info(self, url):
        """Получает метаданные видео для предварительного просмотра в интерфейсе"""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'best'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)

    def download(self, url, save_path, quality="best", audio_only=False, allow_playlist=False):
        """Основной метод загрузки с поддержкой пост-процессинга и выбора качества"""
        
        # Настройка формата и конвертации
        if audio_only:
            ydl_format = 'bestaudio/best'
            # Параметры для извлечения аудио в формате mp3
            postprocessors = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            # Маппинг качества видео
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
            'progress_hooks': [self.progress_callback],
            'outtmpl': os.path.join(save_path, "%(title)s.%(ext)s"),
            'noplaylist': not allow_playlist,
            'postprocessors': postprocessors,
            'quiet': True,
            'no_warnings': True,
            'no_color': True,  # Добавьте эту строку, чтобы убрать спецсимволы цветов
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])