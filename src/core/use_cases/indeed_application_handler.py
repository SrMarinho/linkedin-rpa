import asyncio
import time
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import NoSuchElementException
from src.core.ai.llm_provider import get_llm_provider
from src.config.settings import logger

_REACT_SET_VALUE = """
(function(el, val) {
    var setter = Object.getOwnPropertyDescriptor(el.constructor.prototype, 'value');
    if (setter && setter.set) {
        setter.set.call(el, val);
    } else {
        el.value = val;
    }
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
})(arguments[0], arguments[1]);
"""


class IndeedApplicationHandler:
    MAX_STEPS = 10

    def __init__(self, driver: WebDriver, resume: str = ""):
        self.driver = driver
        self.resume = resume
        self._original_window = None

    def submit(self, salary_expectation: int | None = None) -> bool:
        try:
            self._original_window = self.driver.current_window_handle
            # Indeed may open application in a new tab
            WebDriverWait(self.driver, 5).until(lambda d: len(d.window_handles) > 1)
            new_window = [w for w in self.driver.window_handles if w != self._original_window][0]
            self.driver.switch_to.window(new_window)
            logger.info("Switched to Indeed application tab")
        except Exception:
            logger.info("Application opened in same tab")

        try:
            for step in range(self.MAX_STEPS):
                time.sleep(1.5)

                self._fill_all_fields(salary_expectation)

                if self._try_submit():
                    self._return_to_main()
                    return True

                if not self._click_next():
                    logger.warning(f"No actionable button on step {step + 1} — skipping")
                    self._return_to_main()
                    return False

            logger.warning("Exceeded max steps in Indeed application flow")
            self._return_to_main()
            return False

        except Exception as e:
            logger.error(f"Error during Indeed application: {e}")
            self._return_to_main()
            return False

    def _return_to_main(self):
        try:
            if self._original_window and self._original_window in self.driver.window_handles:
                self.driver.switch_to.window(self._original_window)
        except Exception:
            pass

    def _fill_all_fields(self, salary: int | None) -> None:
        try:
            inputs = self.driver.find_elements(
                By.XPATH,
                "//input[@required and @type!='hidden' and (@type='text' or @type='number' or @type='tel')]"
            )
            for inp in inputs:
                if not inp.is_displayed() or inp.get_attribute("value"):
                    continue
                question = self._get_field_label(inp)
                answer = self._decide_answer(question, salary)
                if answer:
                    self._set_input_value(inp, str(answer))
                    logger.info(f"Filled '{question}' -> '{answer}'")

            textareas = self.driver.find_elements(By.XPATH, "//textarea[@required]")
            for ta in textareas:
                if not ta.is_displayed() or ta.get_attribute("value"):
                    continue
                question = self._get_field_label(ta)
                answer = self._ask_claude(question)
                if answer:
                    ta.clear()
                    ta.send_keys(answer)
                    logger.info(f"Filled textarea '{question}'")

            selects = self.driver.find_elements(By.XPATH, "//select[@required]")
            for sel in selects:
                if not sel.is_displayed() or sel.get_attribute("value"):
                    continue
                question = self._get_field_label(sel)
                options = [o.text.strip() for o in Select(sel).options if o.get_attribute("value")]
                if not options:
                    continue
                answer = self._ask_claude_choice(question, options)
                # Re-find element to avoid stale reference after AI call
                try:
                    fresh_els = self.driver.find_elements(By.XPATH, "//select[@required]")
                    for fresh in fresh_els:
                        if fresh.is_displayed() and self._get_field_label(fresh) == question:
                            sel = fresh
                            break
                except Exception:
                    pass
                try:
                    sel_obj = Select(sel)
                    if answer:
                        matched = next((o for o in options if o.lower() == answer.lower()), None)
                        matched = matched or next((o for o in options if answer.lower() in o.lower() or o.lower() in answer.lower()), None)
                        if matched:
                            sel_obj.select_by_visible_text(matched)
                            logger.info(f"Selected '{matched}' for '{question}'")
                        else:
                            # Fallback: first non-placeholder option
                            for opt_el in sel_obj.options:
                                if opt_el.get_attribute("value"):
                                    sel_obj.select_by_value(opt_el.get_attribute("value"))
                                    logger.warning(f"No match for '{answer}' in '{question}' — selected first option: '{opt_el.text.strip()}'")
                                    break
                except Exception as e:
                    logger.warning(f"Failed to select for '{question}': {e}")

        except Exception as e:
            logger.debug(f"Error filling fields: {e}")

    def _decide_answer(self, question: str, salary: int | None) -> str | None:
        if not question or question == "(unknown)":
            return None
        salary_keywords = [
            "salário", "salario", "salary", "remuneração", "remuneracao",
            "pretensão", "pretensao", "compensation", "salarial", "expectativa",
            "remuner", "wage", "pay ", "ctc",
        ]
        if salary and any(kw in question.lower() for kw in salary_keywords):
            return str(salary)
        return self._ask_claude(question)

    def _set_input_value(self, element, value: str) -> None:
        try:
            self.driver.execute_script(_REACT_SET_VALUE, element, value)
            time.sleep(0.2)
        except Exception:
            try:
                element.clear()
                element.send_keys(value)
            except Exception:
                pass

    def _ask_claude(self, question: str) -> str | None:
        try:
            return asyncio.run(self._ask_claude_async(question))
        except Exception:
            return None

    def _ask_claude_choice(self, question: str, options: list[str]) -> str | None:
        try:
            return asyncio.run(self._ask_claude_choice_async(question, options))
        except Exception:
            return None

    async def _ask_claude_async(self, question: str) -> str | None:
        prompt = f"""Com base no currículo do candidato, responda a seguinte pergunta do formulário de candidatura.

CURRÍCULO:
{self.resume}

PERGUNTA: {question}

Responda APENAS com o valor — um número, palavra curta ou frase breve em português, adequado para um campo de formulário.
Se não souber a resposta ou ela não estiver no currículo, responda exatamente: null
Não invente. Não inclua explicações ou pontuação."""

        result = (await get_llm_provider().complete(prompt) or "").strip()
        if not result or result.lower() == "null":
            return None
        return result

    async def _ask_claude_choice_async(self, question: str, options: list[str]) -> str | None:
        options_str = "\n".join(f"- {o}" for o in options)
        prompt = f"""Com base no currículo do candidato, escolha a melhor opção para este campo do formulário de candidatura.

CURRÍCULO:
{self.resume}

PERGUNTA: {question}

OPÇÕES:
{options_str}

Responda APENAS com o texto exato da opção escolhida. Sem explicações."""

        result = await get_llm_provider().complete(prompt)

        for opt in options:
            if opt.lower() == result.lower():
                return opt
        for opt in options:
            if result.lower() in opt.lower() or opt.lower() in result.lower():
                return opt
        return None

    def _try_submit(self) -> bool:
        try:
            btn = self.driver.find_element(
                By.XPATH,
                "//button["
                "contains(@data-testid,'submit') or "
                "contains(normalize-space(),'Enviar candidatura') or "
                "contains(normalize-space(),'Submit application') or "
                "contains(normalize-space(),'Enviar') or "
                "contains(normalize-space(),'Submit')"
                "]",
            )
            if btn.is_displayed() and btn.is_enabled():
                btn.click()
                logger.info("Application submitted on Indeed")
                time.sleep(2)
                return True
        except NoSuchElementException:
            pass
        return False

    def _click_next(self) -> bool:
        try:
            btn = self.driver.find_element(
                By.XPATH,
                "//button["
                "contains(@data-testid,'next') or "
                "contains(normalize-space(),'Continuar') or "
                "contains(normalize-space(),'Continue') or "
                "contains(normalize-space(),'Próximo') or "
                "contains(normalize-space(),'Next')"
                "]",
            )
            if btn.is_displayed() and btn.is_enabled():
                btn.click()
                return True
        except NoSuchElementException:
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
