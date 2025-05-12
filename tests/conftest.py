import tempfile
from pathlib import Path

import pytest
from pytest import FixtureRequest
from src.external_api import HeadHunterApiVacancies
from src.temp_vacancy_storage import TempVacancyStorage
from typing import Any, Dict, List, Optional

@pytest.fixture
def api_instance():
    """Фикстура для создания экземпляра API."""
    position = "Python Developer"
    params = {
        "text": "Python",
        "area": "Москва",
        "page": "0",
        "per_page": "10"
    }
    return HeadHunterApiVacancies(position, params)


@pytest.fixture
def temp_files(api_instance):
    """Фикстура для временных файлов."""
    temp_dir = tempfile.TemporaryDirectory()
    temp_areas_file = Path(temp_dir.name) / "areas.json"
    temp_vacancies_file = Path(temp_dir.name) / "vacancies.json"

    # Подмена путей
    api_instance._HeadHunterApiVacancies__areas_file = temp_areas_file
    api_instance._HeadHunterApiVacancies__vacancies_file = temp_vacancies_file

    yield temp_areas_file, temp_vacancies_file
    temp_dir.cleanup()


@pytest.fixture
def storage(request: FixtureRequest) -> TempVacancyStorage:
    """Фикстура создает и автоматически очищает хранилище."""
    storage = TempVacancyStorage()

    def cleanup() -> None:
        storage.close()

    request.addfinalizer(cleanup)
    return storage

@pytest.fixture
def sample_vacancy() -> Dict[str, Any]:
    """Фикстура с примером вакансии."""
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
    """Фикстура с примером списка вакансий."""
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