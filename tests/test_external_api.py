import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from src.external_api import HeadHunterApiVacancies


def test_init(api_instance):
    """Тест инициализации класса."""
    assert api_instance.base_url == "https://api.hh.ru"
    assert api_instance.params["text"] == "Python"
    assert str(api_instance) == "<HeadHunterApiVacancies position=Python Developer>"


@patch("requests.get")
def test_areas_data_refresh_success(mock_get, api_instance, temp_files):
    """Тест успешного обновления данных о регионах."""
    temp_areas_file, _ = temp_files

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"id": 1, "name": "Москва"}]
    mock_get.return_value = mock_response

    api_instance.areas_data_refresh()

    assert temp_areas_file.exists()
    with open(temp_areas_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data == [{"id": 1, "name": "Москва"}]


@patch("requests.get")
def test_load_vacancies_success(mock_get, api_instance, temp_files):
    """Тест успешной загрузки вакансий."""
    temp_areas_file, _ = temp_files

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "items": [
            {
                "id": "1",
                "name": "Python Developer",
                "salary": {"from": 100000, "to": 150000},
                "published_at": "2023-01-01",
                "created_at": "2023-01-01",
                "employer": {"name": "Google"},
                "area": {"name": "Москва"},
                "snippet": {"requirement": "Python", "responsibility": "Разработка"},
                "experience": {"name": "1-3 года"},
                "schedule": {"name": "Полный день"},
                "employment": {"name": "Полная занятость"},
            }
        ]
    }
    mock_get.return_value = mock_response

    # Мок данных о регионах
    with open(temp_areas_file, "w", encoding="utf-8") as f:
        json.dump([{"id": 1, "name": "Москва", "areas": []}], f)

    storage = api_instance.load_vacancies()
    assert Path(storage.file_path).exists()