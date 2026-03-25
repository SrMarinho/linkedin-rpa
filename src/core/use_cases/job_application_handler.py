import asyncio
import time
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage
from src.config.settings import logger


class JobApplicationHandler:
    MAX_STEPS = 10

    def __init__(self, driver: WebDriver, resume: str = ""):
        self.driver = driver
        self.resume = resume

    def submit_easy_apply(self, salary_expectation: int | None = None) -> bool:
        try:
            for step in range(self.MAX_STEPS):
                time.sleep(1.5)

                self._fill_salary_fields(salary_expectation)
                self._fill_custom_fields()

                if self._has_unanswered_required_fields():
                    logger.warning("Required fields not filled — skipping")
                    self._close_modal()
                    return False

                if self._try_submit():
                    return True

                if not self._click_next():
                    logger.warning(f"No actionable button on step {step + 1} — skipping")
                    self._close_modal()
                    return False

            logger.warning("Exceeded max steps in Easy Apply flow")
            self._close_modal()
            return False

        except Exception as e:
            logger.error(f"Error during Easy Apply: {e}")
            self._close_modal()
            return False

    def _click_btn(self, btn) -> bool:
        try:
            btn.click()
            return True
        except Exception:
            try:
                self.driver.execute_script("arguments[0].click();", btn)
                return True
            except Exception:
                return False

    def _try_submit(self) -> bool:
        try:
            btn = self.driver.find_element(
                By.XPATH,
                "//button["
                "contains(@aria-label,'Submit application') or "
                "contains(@aria-label,'Enviar candidatura') or "
                ".//span[normalize-space()='Submit application'] or "
                ".//span[normalize-space()='Enviar candidatura']"
                "]",
            )
            if self._click_btn(btn):
                logger.info("Application submitted")
                time.sleep(1.5)
                self._close_modal()
                return True
        except NoSuchElementException:
            pass
        return False

    def _click_next(self) -> bool:
        try:
            btn = self.driver.find_element(
                By.XPATH,
                "//button["
                "contains(@aria-label,'Continue to next step') or "
                "contains(@aria-label,'Continuar para') or "
                "contains(@aria-label,'Avançar para') or "
                "contains(@aria-label,'Review your application') or "
                "contains(@aria-label,'Revisar') or "
                ".//span[normalize-space()='Next'] or "
                ".//span[normalize-space()='Próximo'] or "
                ".//span[normalize-space()='Avançar'] or "
                ".//span[normalize-space()='Review'] or "
                ".//span[normalize-space()='Revisar']"
                "]",
            )
            return self._click_btn(btn)
        except NoSuchElementException:
            pass
        return False

    def _fill_salary_fields(self, salary: int | None) -> None:
        if not salary:
            return
        try:
            salary_keywords = [
                "salário", "salario", "salary", "remuneração", "remuneracao",
                "pretensão", "pretensao", "compensation", "pay"
            ]
            inputs = self.driver.find_elements(By.XPATH, "//input[@type='text' or @type='number']")
            for inp in inputs:
                if not inp.is_displayed():
                    continue
                combined = self._get_field_label(inp).lower()
                if any(kw in combined for kw in salary_keywords):
                    if not inp.get_attribute("value"):
                        inp.clear()
                        inp.send_keys(str(salary))
                        logger.info(f"Filled salary field with R${salary:,}")
        except Exception as e:
            logger.debug(f"Error filling salary fields: {e}")

    def _fill_custom_fields(self) -> None:
        """Use Claude to answer custom required text/number questions."""
        if not self.resume:
            return
        try:
            inputs = self.driver.find_elements(
                By.XPATH, "//input[@required and (@type='text' or @type='number') and not(@type='hidden')]"
            )
            for inp in inputs:
                if not inp.is_displayed():
                    continue
                if inp.get_attribute("value"):
                    continue
                question = self._get_field_label(inp)
                if not question or question == "(unknown)":
                    continue
                answer = self._ask_claude(question)
                if answer:
                    inp.clear()
                    inp.send_keys(answer)
                    logger.info(f"Filled '{question}' → '{answer}'")
        except Exception as e:
            logger.debug(f"Error filling custom fields: {e}")

    def _ask_claude(self, question: str) -> str | None:
        try:
            return asyncio.run(self._ask_claude_async(question))
        except Exception:
            return None

    async def _ask_claude_async(self, question: str) -> str | None:
        prompt = f"""Based on this candidate's resume, answer the following job application form question.

RESUME:
{self.resume}

QUESTION: {question}

Reply with ONLY the answer value — a number, short word, or brief phrase suitable for a form field.
Do not include explanations. Examples:
- "Há quantos anos com Python?" → 3
- "Nível de inglês?" → Intermediário
- "Você mora em São Paulo?" → Não
- "Anos de experiência com backend?" → 3"""

        result = ""
        async for message in query(prompt=prompt, options=ClaudeAgentOptions(max_turns=1)):
            if isinstance(message, ResultMessage):
                result = message.result.strip()

        return result if result else None

    def _has_unanswered_required_fields(self) -> bool:
        try:
            inputs = self.driver.find_elements(
                By.XPATH, "//input[@required and @type!='hidden']"
            )
            for inp in inputs:
                if inp.is_displayed() and not inp.get_attribute("value"):
                    label = self._get_field_label(inp)
                    logger.warning(f"Unfilled required input: '{label}'")
                    return True

            selects = self.driver.find_elements(By.XPATH, "//select[@required]")
            for sel in selects:
                if sel.is_displayed() and not sel.get_attribute("value"):
                    label = self._get_field_label(sel)
                    logger.warning(f"Unfilled required select: '{label}'")
                    return True
        except Exception:
            pass
        return False

    def _get_field_label(self, element) -> str:
        try:
            field_id = element.get_attribute("id")
            if field_id:
                labels = self.driver.find_elements(By.XPATH, f"//label[@for='{field_id}']")
                if labels:
                    return labels[0].text.strip()
            placeholder = element.get_attribute("placeholder") or ""
            aria_label = element.get_attribute("aria-label") or ""
            return placeholder or aria_label or "(unknown)"
        except Exception:
            return "(unknown)"

    def _close_modal(self) -> None:
        try:
            btn = self.driver.find_element(
                By.XPATH,
                "//button["
                "@aria-label='Dismiss' or "
                "@aria-label='Fechar' or "
                "contains(@class,'artdeco-modal__dismiss')"
                "]",
            )
            btn.click()
            time.sleep(0.5)

            try:
                discard_btn = self.driver.find_element(
                    By.XPATH,
                    "//button["
                    ".//span[normalize-space()='Discard'] or "
                    ".//span[normalize-space()='Descartar']"
                    "]",
                )
                discard_btn.click()
            except Exception:
                pass

        except Exception:
            try:
                ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                time.sleep(0.5)
            except Exception:
                pass
