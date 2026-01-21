from pathlib import Path
from src.utils.logger import CustomLogger
import src.config.logging as logging

logger = CustomLogger(logging.settings).get_logger()

base_dir = Path("").resolve().resolve()
logger.info(base_dir)

screenshots_path = base_dir/Path("screenshots")

Path.mkdir(screenshots_path, exist_ok=True)
