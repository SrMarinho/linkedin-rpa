import json
import re
from datetime import datetime
from pathlib import Path
from src.config.settings import logger

APPLIED_JOBS_FILE = Path("applied_jobs.json")


class AppliedJobsTracker:
    def __init__(self):
        self._data: dict = self._load()

    def _load(self) -> dict:
        if APPLIED_JOBS_FILE.exists():
            try:
                return json.loads(APPLIED_JOBS_FILE.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {}

    def _save(self):
        APPLIED_JOBS_FILE.write_text(
            json.dumps(self._data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _job_id(self, url: str) -> str:
        """Extract LinkedIn job ID from URL, fallback to sanitized URL."""
        match = re.search(r"currentJobId=(\d+)|/jobs/view/(\d+)", url)
        if match:
            return match.group(1) or match.group(2)
        return re.sub(r"[^a-z0-9]", "_", url.lower())[:80]

    def already_applied(self, job_url: str) -> bool:
        return self._job_id(job_url) in self._data

    def mark_applied(self, job_url: str, title: str, salary: int | None = None):
        job_id = self._job_id(job_url)
        self._data[job_id] = {
            "title": title,
            "url": job_url,
            "applied_at": datetime.now().isoformat(),
            "salary_offered": salary,
        }
        self._save()
        logger.info(f"Saved application: '{title}' (id={job_id})")
