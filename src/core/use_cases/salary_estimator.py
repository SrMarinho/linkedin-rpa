import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage
from src.config.settings import logger


class SalaryEstimator:
    """Estimates an appropriate salary expectation for a job application."""

    def estimate(self, title: str, description: str) -> int | None:
        return asyncio.run(self._estimate_async(title, description))

    async def _estimate_async(self, title: str, description: str) -> int | None:
        prompt = f"""You are a Brazilian tech salary expert. Analyze this job posting and suggest an appropriate salary expectation for the candidate to put on their application.

JOB TITLE: {title}

JOB DESCRIPTION:
{description}

Instructions:
1. Check if the job description mentions a salary range or value — if yes, use it as reference.
2. Identify the seniority level (Junior, Pleno, Sênior) from the title and description.
3. Identify the contract type (CLT or PJ) if mentioned.
4. Based on current Brazilian tech market rates (2024-2025), suggest a fair salary expectation.

Market reference (monthly gross, BRL):
- Junior Dev: CLT R$3.000–6.000 | PJ R$4.000–8.000
- Pleno Dev: CLT R$6.000–10.000 | PJ R$8.000–14.000
- Sênior Dev: CLT R$10.000–18.000 | PJ R$14.000–25.000

Reply with ONLY a single integer representing the suggested monthly salary in BRL (no currency symbol, no dots, no text).
Example: 8000"""

        result = ""
        async for message in query(
            prompt=prompt,
            options=ClaudeAgentOptions(max_turns=1),
        ):
            if isinstance(message, ResultMessage):
                result = message.result.strip()

        try:
            # Extract first number found in the response
            import re
            match = re.search(r"\d[\d.]*", result.replace(",", ""))
            if match:
                value = int(match.group().replace(".", ""))
                logger.info(f"Salary estimate: R${value:,}")
                return value
        except Exception:
            pass

        logger.warning(f"Could not parse salary estimate from: '{result}'")
        return None
