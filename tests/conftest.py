import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Generator, Tuple
from unittest.mock import MagicMock, mock_open, patch

import pytest
from pytest import FixtureRequest

from src.external_api import HeadHunterApiVacancies
from src.favorites_storage import JSONFavoritesStorage
from src.temp_vacancy_storage import TempVacancyStorage


@pytest.fixture
def api_instance() -> HeadHunterApiVacancies:
    """Фикстура для создания экземпляра API HeadHunter.

    Returns:
        HeadHunterApiVacancies: Экземпляр класса HeadHunterApiVacancies с тестовыми параметрами
    """
    position = "Python Developer"
    params = {"text": "Python", "area": "Москва", "page": "0", "per_page": "10"}
    return HeadHunterApiVacancies(position, params)


@pytest.fixture
def temp_files(api_instance: HeadHunterApiVacancies) -> Generator[Tuple[Path, Path], None, None]:
    """Фикстура создает временные файлы для тестирования и подменяет пути в API инстансе.

    Args:
        api_instance: Фикстура с экземпляром API HeadHunter

    Yields:
        Tuple[Path, Path]: Кортеж с путями к временным файлам (areas.json, vacancies.json)
    """
    temp_dir = tempfile.TemporaryDirectory()
    temp_areas_file = Path(temp_dir.name) / "areas.json"
    temp_vacancies_file = Path(temp_dir.name) / "vacancies.json"

    # Подмена путей в инстансе API
    # api_instance._HeadHunterApiVacancies__areas_file = temp_areas_file
    # api_instance._HeadHunterApiVacancies__vacancies_file = temp_vacancies_file
    api_instance.areas_file = temp_areas_file
    api_instance.vacancies_file = temp_vacancies_file
    yield temp_areas_file, temp_vacancies_file
    temp_dir.cleanup()


@pytest.fixture
def storage(request: FixtureRequest) -> TempVacancyStorage:
    """Фикстура создает временное хранилище вакансий с автоматической очисткой после тестов.

    Args:
        request: Специальный объект pytest для регистрации финализаторов

    Returns:
        TempVacancyStorage: Экземпляр временного хранилища вакансий
    """
    storage = TempVacancyStorage()

    def cleanup() -> None:
        storage.close()

    request.addfinalizer(cleanup)
    return storage


@pytest.fixture
def sample_vacancy() -> Dict[str, Any]:
    """Фикстура возвращает тестовую вакансию в виде словаря.

    Returns:
        Dict[str, Any]: Словарь с данными вакансии, включая:
            - id: Идентификатор вакансии
            - vacancy: Название вакансии
            - employer: Работодатель
            - salary: Зарплата (от, до, валюта)
            - city: Город
            - experience: Требуемый опыт
            - schedule: График работы
            - requirements: Требования
    """
    return {
        "id": "123",
        "vacancy": "Python Developer",
        "employer": "Tech Corp",
        "salary": {"from": 100000, "to": 150000, "currency": "RUB"},
        "city": "Москва",
        "experience": "1-3 года",
        "schedule": "Полный день",
        "requirements": "Опыт работы с Python",
    }


@pytest.fixture
def sample_vacancies() -> List[Dict[str, Any]]:
    """Фикстура возвращает список тестовых вакансий.

    Returns:
        List[Dict[str, Any]]: Список словарей с данными вакансий, включая:
            - id: Идентификатор вакансии
            - vacancy: Название вакансии
            - employer: Работодатель
            - salary: Зарплата (может быть None)
            - city: Город
    """
    return [
        {
            "id": "1",
            "vacancy": "Frontend Developer",
            "employer": "Web Inc",
            "salary": {"from": 80000},
            "city": "Санкт-Петербург",
        },
        {
            "id": "2",
            "vacancy": "Data Scientist",
            "employer": "Data Corp",
            "salary": None,
            "city": "Новосибирск",
        },
    ]


@pytest.fixture
def mock_input() -> Generator[MagicMock, None, None]:
    """Фикстура для мокирования ввода input().

    Yields:
        MagicMock: Мок-объект для замены builtins.input
    """
    with patch("builtins.input") as mock:
        yield mock


@pytest.fixture
def mock_print() -> Generator[MagicMock, None, None]:
    """Фикстура для мокирования вывода print().

    Yields:
        MagicMock: Мок-объект для замены builtins.print
    """
    with patch("builtins.print") as mock:
        yield mock


@pytest.fixture
def mock_api_vacancies() -> Generator[MagicMock, None, None]:
    """Фикстура для мокирования HeadHunterApiVacancies с тестовыми данными.

    Yields:
        MagicMock: Мок-объект класса HeadHunterApiVacancies с:
            - Замоканными статическими методами
            - Тестовыми данными вакансий
            - Замоканным методом vacancies_saver
    """
    with patch("main.HeadHunterApiVacancies") as mock:
        instance = mock.return_value
        # Мокаем статические методы
        instance.params_input.return_value = {"text": "Python", "area": "Москва", "page": "0", "per_page": "10"}
        instance.position_input.return_value = "Python Developer"
        instance.vacancies_file = "test_vacancies.json"

        # Мокаем метод vacancies_saver
        instance.vacancies_saver = MagicMock()

        # Мокаем файловые операции
        mock_vacancies_data = [
            {
                "id": "1",
                "vacancy": "Python Developer",
                "salary": {"from": 100000, "to": 150000, "currency": "RUB"},
                "employer": "Tech Corp",
                "city": "Москва",
                "requirements": "Опыт работы",
                "experience": "1-3 года",
                "schedule": "Полный день",
            }
        ]

        # Мокаем открытие файла
        with patch("builtins.open", mock_open(read_data=json.dumps(mock_vacancies_data))):
            yield mock


@pytest.fixture
def mock_json_favorites_storage() -> Generator[MagicMock, None, None]:
    """Фикстура для мокирования JSONFavoritesStorage с тестовыми данными.

    Yields:
        MagicMock: Мок-объект класса JSONFavoritesStorage с:
            - Замоканным методом load_favorites (возвращает пустой список)
            - Замоканным методом get_favorites (возвращает тестовые данные)
    """
    with patch("main.JSONFavoritesStorage") as mock:
        instance = mock.return_value
        instance.load_favorites.return_value = []
        instance.get_favorites.return_value = [
            {
                "id": "1",
                "vacancy": "Python Developer",
                "salary": {"from": 100000, "to": 150000, "currency": "RUB"},
                "employer": "Tech Corp",
                "city": "Москва",
                "requirements": "Опыт работы",
                "experience": "1-3 года",
                "schedule": "Полный день",
            }
        ]
        yield mock


@pytest.fixture
def mock_viewer_print_vacancies() -> Generator[MagicMock, None, None]:
    """Фикстура для мокирования метода print_vacancies класса Viewer.

    Yields:
        MagicMock: Мок-объект для метода Viewer.print_vacancies
    """
    with patch("src.viewer.Viewer.print_vacancies") as mock:
        yield mock


@pytest.fixture
def mock_file_structure(tmp_path: Path) -> Path:
    """Фикстура создает временную структуру папок для тестирования.

    Args:
        tmp_path: Временный путь предоставляемый pytest

    Returns:
        Path: Путь к корневой директории созданной структуры:
            - data/
              - favorite/
    """
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    favorites_dir = data_dir / "favorite"
    favorites_dir.mkdir()
    return tmp_path


@pytest.fixture
def sample_vacancy2() -> Dict[str, Any]:
    """Альтернативная фикстура с тестовой вакансией.

    Returns:
        Dict[str, Any]: Словарь с данными вакансии (аналогично sample_vacancy, но с другим id)
    """
    return {
        "id": "1",
        "vacancy": "Python Developer",
        "salary": {"from": 100000, "to": 150000, "currency": "RUB"},
        "employer": "Tech Corp",
        "city": "Москва",
        "requirements": "Опыт работы",
        "experience": "1-3 года",
        "schedule": "Полный день",
    }


@pytest.fixture
def storage2(tmp_path: Path, sample_vacancy2: Dict[str, Any]) -> JSONFavoritesStorage:
    """Фикстура создает тестовое хранилище избранного с одной вакансией.

    Args:
        tmp_path: Временный путь предоставляемый pytest
        sample_vacancy2: Фикстура с тестовой вакансией

    Returns:
        JSONFavoritesStorage: Экземпляр хранилища с тестовыми данными:
            - Создает временную структуру папок
            - Сохраняет тестовую вакансию в файл
            - Инициализирует хранилище с категорией 'test_category'
    """
    # Создаем временную структуру папок
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    favorites_dir = data_dir / "favorite"
    favorites_dir.mkdir()

    # Создаем тестовый файл с вакансиями
    source_file = tmp_path / "source_vacancies.json"
    with open(source_file, "w", encoding="utf-8") as f:
        json.dump([sample_vacancy2], f)

    return JSONFavoritesStorage(source_file, "test_category")