from typing import Any, Dict, List, Optional
import pytest
from bs4 import BeautifulSoup
from colorama import Fore, Style
from src.viewer import Viewer  # Замените на реальный импорт

@pytest.mark.parametrize(
    "html_input, expected",
    [
        ("<p>Simple text</p>", "Simple text"),
        ("<div><h1>Title</h1><p>Content</p></div>", "Title Content"),  # Добавлен пробел
        ("Text with <highlighttext>tags</highlighttext>", "Text with tags"),
        ("", ""),
        ("No tags here", "No tags here"),
        ("<script>alert()</script>", "alert()"),
        ("<style>body {color: red;}</style>", "body {color: red;}"),
    ],
)
def test_clean_html(html_input: str, expected: str) -> None:
    """Тестирует очистку HTML-тегов."""
    assert Viewer.clean_html(html_input) == expected


@pytest.mark.parametrize(
    "salary, expected",
    [
        (None, "Не указана"),
        ({"from": 100000}, "от 100000"),
        ({"to": 200000}, "до 200000"),
        ({"from": 100000, "to": 200000}, "от 100000 до 200000"),
        ({"from": 100000, "to": 200000, "currency": "RUB"}, "от 100000 до 200000 RUB"),
        ({"currency": "USD"}, "USD"),
        ({}, "Не указана"),
    ],
)
def test_format_salary(salary: Optional[Dict[str, Any]], expected: str) -> None:
    """Тестирует форматирование зарплаты."""
    assert Viewer.format_salary(salary) == expected


def test_print_vacancy_full(
    capsys: pytest.CaptureFixture[str], sample_vacancy: Dict[str, Any]
) -> None:
    """Тестирует вывод полной вакансии."""
    Viewer.print_vacancy(sample_vacancy)
    captured = capsys.readouterr()
    output = captured.out

    assert sample_vacancy["id"] in output
    assert sample_vacancy["vacancy"] in output
    assert Fore.YELLOW in output
    assert Style.RESET_ALL in output
    assert "от 100000 до 150000 RUB" in output
    assert sample_vacancy["city"] in output
    assert sample_vacancy["experience"] in output
    assert sample_vacancy["schedule"] in output
    assert sample_vacancy["requirements"] in output


def test_print_vacancy_minimal(capsys: pytest.CaptureFixture[str]) -> None:
    """Тестирует вывод вакансии с минимальными данными."""
    minimal_vacancy: Dict[str, Any] = {"id": "456", "vacancy": "Backend Developer"}
    Viewer.print_vacancy(minimal_vacancy)
    captured = capsys.readouterr()
    output = captured.out

    assert minimal_vacancy["id"] in output
    assert minimal_vacancy["vacancy"] in output
    assert "Не указано" in output
    assert "Не указана" in output


def test_print_vacancies(
    capsys: pytest.CaptureFixture[str], sample_vacancies: List[Dict[str, Any]]
) -> None:
    """Тестирует вывод списка вакансий."""
    Viewer.print_vacancies(sample_vacancies)
    captured = capsys.readouterr()
    output = captured.out

    for vacancy in sample_vacancies:
        assert vacancy["vacancy"] in output
        assert vacancy["id"] in output

    assert "=======" in output
    assert output.count("=======") >= len(sample_vacancies)