import os
from pathlib import Path

settings = {
   "app_name": os.getenv("APP_NAME", "APP"),
   "log_level": os.getenv("LOG_LEVEL", "INFO"),
   "log_dir": Path("logs")
}
    