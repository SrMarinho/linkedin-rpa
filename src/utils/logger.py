import logging
import os
from datetime import datetime
import logging
from datetime import datetime
from pathlib import Path


# -------------------------------------------------------------
# Formatter opcional — elimina quebras de linha nos logs
# -------------------------------------------------------------
class SingleLineFormatter(logging.Formatter):
    def format(self, record):
        msg = super().format(record)
        return msg.replace("\n", " ")


# -------------------------------------------------------------
# Wrapper / fábrica de logger
# -------------------------------------------------------------
class CustomLogger:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.logger = self._configure()

    # público ────────────────────────────────────────────────
    def get_logger(self) -> logging.Logger:
        """Retorna o logger pronto para usar."""
        return self.logger

    # privado ────────────────────────────────────────────────
    def _configure(self) -> logging.Logger:
        logger = logging.getLogger(self.cfg["app_name"])

        # Se já tem handlers, alguém já configurou — só devolve
        if logger.handlers:
            return logger

        # Nível global do logger
        logger.setLevel(getattr(logging, self.cfg["log_level"].upper(), logging.INFO))

        # Handler de console
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        console.setFormatter(SingleLineFormatter("%(message)s"))
        logger.addHandler(console)

        # Handler de arquivo (um log por dia)
        file_path = self._build_log_path(self.cfg["log_dir"])
        file_handler = logging.FileHandler(file_path, mode="a", encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        logger.addHandler(file_handler)

        return logger

    @staticmethod
    def _build_log_path(base_dir: Path) -> Path:
        """Garante a pasta …/<ano>/<mês>/ e devolve o caminho do log YYYYMMDD.log."""
        today = datetime.now()
        folder = base_dir / f"{today:%Y}" / f"{today:%m}"
        folder.mkdir(parents=True, exist_ok=True)
        return folder / f"{today:%Y%m%d}.log"
