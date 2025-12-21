import yt_dlp
import os
import sys
import subprocess

class DownloadCancelled(Exception):
    pass

class VideoDownloader:
    def __init__(self, progress_callback):
        self.progress_callback = progress_callback
        self.is_cancelled = False

    def cancel(self):
        self.is_cancelled = True

    def _progress_hook(self, d):
        if self.is_cancelled:
            raise DownloadCancelled("Загрузка отменена пользователем")
        if self.progress_callback:
            self.progress_callback(d)

    @staticmethod
    def update_ytdlp():
        """Обновляет библиотеку yt-dlp через pip"""
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "yt-dlp"])
            return True
        except Exception as e:
            print(f"Update error: {e}")
            return False

    def get_video_info(self, url, proxy=None, cookies_path=None, cookies_browser=None):
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': 'in_playlist',
        }
        if proxy: ydl_opts['proxy'] = proxy
        
        # Приоритет: Файл > Браузер
        if cookies_path and os.path.exists(cookies_path):
            ydl_opts['cookiefile'] = cookies_path
        elif cookies_browser and cookies_browser != "none":
            ydl_opts['cookiesfrombrowser'] = (cookies_browser,)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)

    def download(self, url, save_path, quality="best", audio_only=False, 
                 audio_format="mp3", audio_bitrate="192", 
                 allow_playlist=False, proxy=None, 
                 cookies_path=None, cookies_browser=None, 
                 custom_filename=None, 
                 embed_meta=True, download_subs=False,
                 use_sponsor_block=False, playlist_items=None): # [UPDATED]
        
        self.is_cancelled = False
        postprocessors = []
        ydl_format = "best"

        if audio_only:
            ydl_format = 'bestaudio/best'
            postprocessors.append({
                'key': 'FFmpegExtractAudio',
                'preferredcodec': audio_format,
                'preferredquality': audio_bitrate,
            })
        else:
            format_map = {
                "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
                "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
                "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
                "best": "best"
            }
            ydl_format = format_map.get(quality, "best")

        # --- ВСТРАИВАНИЕ МЕТАДАННЫХ ---
        if embed_meta:
            # Для видео встраиваем обложку, для аудио тоже (если формат позволяет)
            postprocessors.append({'key': 'FFmpegMetadata'})
            if not audio_only or audio_format in ['mp3', 'm4a', 'flac']:
                postprocessors.append({'key': 'EmbedThumbnail'})

        # --- SPONSORBLOCK [NEW] ---
        if use_sponsor_block:
            postprocessors.append({
                'key': 'SponsorBlock',
                'categories': ['sponsor', 'intro', 'outro', 'selfpromo', 'preview', 'interaction'],
                'when': 'after_filter'
            })

        # --- ИМЯ ФАЙЛА ---
        if custom_filename:
            if allow_playlist:
                tmpl = f"{custom_filename} - %(playlist_index)s.%(ext)s"
            else:
                tmpl = f"{custom_filename}.%(ext)s"
        else:
            tmpl = "%(title)s.%(ext)s"

        ydl_opts = {
            'format': ydl_format,
            'progress_hooks': [self._progress_hook],
            'outtmpl': os.path.join(save_path, tmpl),
            'noplaylist': not allow_playlist,
            'postprocessors': postprocessors,
            'quiet': True,
            'no_warnings': True,
            'no_color': True,
            'ignoreerrors': True if allow_playlist else False,
            'restrictfilenames': True,
            'proxy': proxy if proxy else None,
            
            # --- ОПЦИИ ---
            'writethumbnail': embed_meta,
            'writesubtitles': download_subs,
            'subtitleslangs': ['all'] if download_subs else None,
        }

        # [NEW] Выбор элементов плейлиста
        if playlist_items:
            ydl_opts['playlist_items'] = playlist_items

        # --- COOKIES ---
        if cookies_path and os.path.exists(cookies_path):
            ydl_opts['cookiefile'] = cookies_path
        elif cookies_browser and cookies_browser != "none":
            ydl_opts['cookiesfrombrowser'] = (cookies_browser,)

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
                        try: downloaded_files.append(ydl.prepare_filename(entry))
                        except: pass
            else:
                if 'requested_downloads' in info:
                    downloaded_files.append(info['requested_downloads'][0]['filepath'])
                else:
                    downloaded_files.append(ydl.prepare_filename(info))
            
            return downloaded_files