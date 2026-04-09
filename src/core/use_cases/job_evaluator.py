import re
import unicodedata
import asyncio
from pathlib import Path
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage
from src.config.settings import logger

MAX_DESCRIPTION_CHARS = 3000
HAIKU_MODEL = "claude-haiku-4-5-20251001"

# Keywords in job titles that indicate each seniority level
_LEVEL_KEYWORDS: dict[str, list[str]] = {
    "senior":    ["senior", "sênior", "sr.", "sr ", "specialist", "especialista",
                  "lead", "principal", "staff", "head", "arquiteto", "architect"],
    "pleno":     ["pleno", "pl.", "mid", "mid-level", "intermediario", "intermediário"],
    "junior":    ["junior", "júnior", "jr.", "jr ", "trainee", "estagiario",
                  "estagiário", "estágio", "estagio", "intern"],
}

def _normalize(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()


class JobEvaluator:
    def __init__(self, resume_path: str, preferences: str = "", level: str | list[str] = ""):
        path = Path(resume_path)
        if path.suffix.lower() == ".pdf":
            from pypdf import PdfReader
            reader = PdfReader(resume_path)
            self.resume = "\n".join(page.extract_text() or "" for page in reader.pages)
        else:
            with open(resume_path, "r", encoding="utf-8") as f:
                self.resume = f.read()
        self.preferences = preferences
        if isinstance(level, str):
            self.levels = [level] if level else []
        else:
            self.levels = [l for l in level if l]

    def quick_reject(self, title: str) -> bool:
        """Returns True if the title can be rejected without an AI call.

        Checks seniority level keywords against the accepted levels.
        If no levels are configured, never quick-rejects.
        """
        if not self.levels:
            return False

        title_n = _normalize(title)
        accepted = {_normalize(l) for l in self.levels}

        # Detect which level the title is advertising
        detected = None
        for level, keywords in _LEVEL_KEYWORDS.items():
            if any(kw in title_n for kw in keywords):
                detected = level
                break

        if detected is None:
            return False  # can't tell from title alone — let AI decide

        if detected not in accepted:
            logger.info(f"Quick reject (title seniority '{detected}' not in {list(accepted)}): '{title}'")
            return True

        return False

    def evaluate(self, title: str, description: str) -> tuple[bool, int | None]:
        """Returns (is_match, salary_estimate). Single AI call using Haiku."""
        return asyncio.run(self._evaluate_async(title, description))

    async def _evaluate_async(self, title: str, description: str) -> tuple[bool, int | None]:
        description = description[:MAX_DESCRIPTION_CHARS]

        preferences_section = (
            f"\nCANDIDATE PREFERENCES (prioritize these):\n{self.preferences}\n"
            if self.preferences else ""
        )

        if self.levels:
            accepted = " or ".join(f"'{l}'" for l in self.levels)
            level_rule = (
                f"2. Seniority: only accept jobs targeting {accepted} level(s). "
                f"If the job is clearly for a different level, answer NO.\n"
            )
        else:
            level_rule = "2. Seniority: accept any level.\n"

        prompt = f"""You are a career advisor. Evaluate if this job matches the candidate and, if yes, estimate the salary expectation.

CANDIDATE RESUME:
{self.resume}
{preferences_section}
JOB TITLE: {title}

JOB DESCRIPTION:
{description}

Rules:
1. Job description must be in Portuguese (pt-BR). If in English/Spanish/other, answer NO.
{level_rule}3. Check required technologies, remote vs on-site, contract type, and candidate preferences.

Market reference (monthly gross, BRL):
- Junior Dev: CLT R$3.000–6.000 | PJ R$4.000–8.000
- Pleno Dev: CLT R$6.000–10.000 | PJ R$8.000–14.000
- Sênior Dev: CLT R$10.000–18.000 | PJ R$14.000–25.000

IMPORTANT: Reply with ONLY one line in this exact format, no markdown, no extra text:
YES|<salary_integer>|<reason>
or
NO|<reason>

Examples:
YES|5000|Candidate has Python/FastAPI experience and role is remote
NO|Job description is in English"""

        result = ""
        async for message in query(
            prompt=prompt,
            options=ClaudeAgentOptions(max_turns=1, model=HAIKU_MODEL),
        ):
            if isinstance(message, ResultMessage):
                result = message.result.strip()

        # Robust parsing: find the first line that starts with YES or NO
        is_match = False
        salary = None
        reason = result

        for line in result.splitlines():
            line = line.strip()
            upper = line.upper()
            if upper.startswith("YES") or upper.startswith("NO"):
                parts = line.split("|")
                is_match = parts[0].strip().upper() == "YES"
                if is_match and len(parts) >= 2:
                    try:
                        salary = int(re.sub(r"\D", "", parts[1]))
                    except Exception:
                        salary = None
                reason = parts[-1].strip() if len(parts) >= 2 else line
                break

        logger.info(f"Evaluation: {'YES' if is_match else 'NO'} | salary={salary} | {reason}")
        return is_match, salary
