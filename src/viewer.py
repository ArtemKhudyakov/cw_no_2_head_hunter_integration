from bs4 import BeautifulSoup
from colorama import Fore, Style


class Viewer:
    # def __init__(self):

    @staticmethod
    def clean_html(text: str) -> str:
        """Удаляет HTML-теги из текста (включая <highlighttext>)"""
        return BeautifulSoup(text, "html.parser").get_text()

    @staticmethod
    def format_salary(salary: dict | None) -> str:
        """Форматирует зарплату в читаемый вид"""
        if not salary:
            return "Не указана"

        parts = []
        if salary.get("from"):
            parts.append(f"от {salary['from']}")
        if salary.get("to"):
            parts.append(f"до {salary['to']}")
        if salary.get("currency"):
            parts.append(salary["currency"])

        return " ".join(parts) if parts else "Не указана"

    @staticmethod
    def print_vacancy(vacancy: dict) -> None:
        """Красиво выводит вакансию в консоль"""
        print(f"\n{vacancy['id']}")
        print(f"{Fore.YELLOW}{vacancy['vacancy']}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Компания: {vacancy.get('employer', 'Не указано')}")
        print(f"{Fore.CYAN}Зарплата: {Viewer.format_salary(vacancy.get('salary'))}")
        print(f"{Fore.MAGENTA}Город: {vacancy.get('city', 'Не указан')}")
        print(f"{Fore.MAGENTA}Опыт: {vacancy.get('experience', 'Не указан')}")
        print(f"{Fore.MAGENTA}График: {vacancy.get('schedule', 'Не указан')}")

        # Вывод требований (если есть)
        if "requirements" in vacancy:
            print(f"\n{Fore.GREEN}Требования:{Style.RESET_ALL}")
            print(vacancy["requirements"])

    @staticmethod
    def print_vacancies(vacancies: list[dict]) -> None:
        """Выводит список вакансий"""
        for vacancy in vacancies:
            Viewer.print_vacancy(vacancy)
            print("\n" + "=" * 50 + "\n")
