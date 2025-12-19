import yt_dlp
import os

class VideoDownloader:
    def __init__(self, progress_callback):
        self.progress_callback = progress_callback

    def download(self, url, save_path):
        ydl_opts = {
            'format': 'best',
            'progress_hooks': [self.progress_callback],
            'outtmpl': os.path.join(save_path, "%(title)s.%(ext)s"),
            'noplaylist': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])