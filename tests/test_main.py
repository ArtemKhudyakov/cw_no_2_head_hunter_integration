from unittest.mock import Mock, patch
import pytest


from main import main
from src.external_api import HeadHunterApiVacancies


def test_main_exit_immediately(mock_input: Mock, mock_print: Mock) -> None:
    """Тест немедленного выхода из программы."""
    mock_input.side_effect = ["нет"]
    with pytest.raises(SystemExit):
        main()
    mock_print.assert_any_call("Начать поиск вакансий? Да/Нет")


def test_main_search_flow(
    mock_input: Mock, mock_api_vacancies: Mock, mock_print: Mock, mock_viewer_print_vacancies: Mock
) -> None:
    """Тест основного потока поиска вакансий."""
    mock_input.side_effect = [
        "да",  # Начать поиск
        "Python",
        "Москва",
        "1",
        "10",  # Параметры поиска (имитация ввода)
        "нет",  # Повторить поиск
        "8",  # Выйти
    ]

    with patch.object(
        HeadHunterApiVacancies,
        "params_input",
        return_value={"text": "Python", "area": "Москва", "page": "0", "per_page": "10"},
    ):
        with patch.object(HeadHunterApiVacancies, "position_input", return_value="Python Developer"):
            with pytest.raises(SystemExit):
                main()

    mock_viewer_print_vacancies.assert_called_once()


def test_main_top_vacancies(mock_input: Mock, mock_api_vacancies: Mock, mock_print: Mock) -> None:
    """Тест вывода топ-N вакансий по зарплате."""
    mock_input.side_effect = [
        "да",  # Начать поиск
        "Python",
        "Москва",
        "1",
        "10",  # Параметры поиска
        "нет",  # Повторить поиск
        "1",  # Вывести топ N
        "3",  # N = 3
        "8",  # Выйти
    ]

    with pytest.raises(SystemExit):
        main()

    assert mock_print.call_count > 0


def test_main_save_favorites(mock_input: Mock, mock_api_vacancies: Mock, mock_json_favorites_storage: Mock) -> None:
    """Тест сохранения вакансий в избранное."""
    mock_input.side_effect = [
        "да",  # Начать поиск
        "Python",
        "Москва",
        "1",
        "10",  # Параметры поиска
        "нет",  # Повторить поиск
        "2",  # Сохранить в избранное
        "1",  # ID вакансии
        "python_jobs",  # Категория
        "8",  # Выйти
    ]

    with pytest.raises(SystemExit):
        main()

    mock_json_favorites_storage.return_value.save_favorites.assert_called_once()


def test_main_view_favorites(mock_input: Mock, mock_api_vacancies: Mock, mock_json_favorites_storage: Mock) -> None:
    """Тест просмотра избранных вакансий."""
    mock_input.side_effect = [
        "да",  # Начать поиск
        "Python",
        "Москва",
        "1",
        "10",  # Параметры поиска
        "нет",  # Повторить поиск
        "3",  # Посмотреть избранное
        "python_jobs",  # Категория
        "8",  # Выйти
    ]

    with pytest.raises(SystemExit):
        main()

    mock_json_favorites_storage.return_value.get_favorites.assert_called_once()


def test_main_clear_favorites(mock_input: Mock, mock_api_vacancies: Mock, mock_json_favorites_storage: Mock) -> None:
    """Тест очистки избранных вакансий."""
    mock_input.side_effect = [
        "да",  # Начать поиск
        "Python",
        "Москва",
        "1",
        "10",  # Параметры поиска
        "нет",  # Повторить поиск
        "4",  # Очистить избранное
        "да",  # Подтверждение
        "python_jobs",  # Категория
        "8",  # Выйти
    ]

    with pytest.raises(SystemExit):
        main()

    mock_json_favorites_storage.return_value.clear_favorites.assert_called_once()


def test_main_remove_from_favorites(
    mock_input: Mock, mock_api_vacancies: Mock, mock_json_favorites_storage: Mock
) -> None:
    """Тест удаления конкретных вакансий из избранного."""
    mock_input.side_effect = [
        "да",  # Начать поиск
        "Python",
        "Москва",
        "1",
        "10",  # Параметры поиска
        "нет",  # Повортиь поиск
        "5",  # Удалить из избранного
        "python_jobs",  # Категория
        "1,2",  # ID вакансий
        "8",  # Выйти
    ]

    with pytest.raises(SystemExit):
        main()

    mock_json_favorites_storage.return_value.remove_from_favorites.assert_called_once_with("1,2")


def test_main_delete_favorites_file(
    mock_input: Mock, mock_api_vacancies: Mock, mock_json_favorites_storage: Mock
) -> None:
    """Тест удаления файла с избранными вакансиями."""
    mock_input.side_effect = [
        "да",  # Начать поиск
        "Python",
        "Москва",
        "1",
        "10",  # Параметры поиска
        "нет",  # Повторить поиск
        "7",  # Удалить файл категории
        "python_jobs",  # Категория
        "8",  # Выйти
    ]

    with pytest.raises(SystemExit):
        main()

    mock_json_favorites_storage.return_value.delete_favorites_file.assert_called_once()
