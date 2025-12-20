import os
import platform
import subprocess

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