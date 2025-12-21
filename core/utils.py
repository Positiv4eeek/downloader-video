import os
import platform
import subprocess
import shutil
import zipfile
import urllib.request

def open_path(path, is_file=False):
    """Универсальная открывалка файлов и папок"""
    if not path or not os.path.exists(path):
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
        print(f"Error opening path: {e}")

def get_ffmpeg_path():
    """Возвращает путь к ffmpeg или None"""
    # 1. Проверяем локальную папку bin
    local_bin = os.path.join(os.getcwd(), "bin")
    if platform.system() == "Windows":
        local_exe = os.path.join(local_bin, "ffmpeg.exe")
    else:
        local_exe = os.path.join(local_bin, "ffmpeg")
        
    if os.path.exists(local_exe):
        return local_exe
        
    # 2. Проверяем системный PATH
    return shutil.which("ffmpeg")

def check_ffmpeg():
    """Проверяет наличие FFmpeg в системе (совместимость со старым кодом)"""
    return get_ffmpeg_path() is not None

def install_ffmpeg_windows(progress_hook=None):
    """Скачивает и распаковывает FFmpeg (только Windows)"""
    url = "https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    temp_zip = "ffmpeg.zip"
    bin_dir = os.path.join(os.getcwd(), "bin")
    
    if not os.path.exists(bin_dir):
        os.makedirs(bin_dir)

    try:
        # Скачивание
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            total_size = int(response.info().get('Content-Length', 0))
            downloaded = 0
            chunk_size = 8192
            
            with open(temp_zip, 'wb') as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk: break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_hook and total_size > 0:
                        progress_hook(downloaded / total_size)
        
        # Распаковка
        with zipfile.ZipFile(temp_zip, 'r') as zf:
            for file in zf.namelist():
                if file.endswith("ffmpeg.exe"):
                    with open(os.path.join(bin_dir, "ffmpeg.exe"), 'wb') as f_out:
                        f_out.write(zf.read(file))
                    break
                    
        os.remove(temp_zip)
        return True
    except Exception as e:
        print(f"FFmpeg install error: {e}")
        if os.path.exists(temp_zip): os.remove(temp_zip)
        return False