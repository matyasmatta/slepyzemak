import os
import json
import datetime

def get_config(path="D:\Dokumenty\Klíče\config.json"):
    try:
        with open(path) as f: 
            config = json.load(f)
        return config
    except:
        raise ImportError("Invalid config.json file")
    
class Logger:
    def __init__(self, filename="main.log", max_file_size_bytes=10 * 1024 * 1024):
        self.filename = filename[:-4]+".log"
        self.max_file_size_bytes = max_file_size_bytes
        self.check_and_create_log_file()

    def check_and_create_log_file(self):
        if not os.path.isfile(self.filename):
            with open(self.filename, "w") as file:
                file.write("")  # Create an empty log file if it doesn't exist

    def get_log_file_size(self):
        return os.path.getsize(self.filename) if os.path.exists(self.filename) else 0

    def write(self, log_type="error", data="", timestamp=None):
        if timestamp is None:
            timestamp = datetime.datetime.now()

        file_size = self.get_log_file_size()
        if file_size >= self.max_file_size_bytes:
            raise ValueError(f"Log file size exceeds {self.max_file_size_bytes} bytes")

        with open(self.filename, "a") as file:
            log_entry = f"{timestamp} [{log_type.upper()}]: {data}\n"
            file.write(log_entry)
