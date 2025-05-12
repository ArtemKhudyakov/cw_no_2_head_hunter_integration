import json
from pathlib import Path
from typing import Any, Dict

import pytest

from src.temp_vacancy_storage import TempVacancyStorage


def test_file_creation(storage: TempVacancyStorage) -> None:
    """Проверяем создание временного файла."""
    assert Path(storage.file_path).exists()
    assert storage.file_path.endswith('_vacancies.json')


def test_save_and_load(storage: TempVacancyStorage) -> None:
    """Тестируем сохранение и загрузку данных."""
    test_data: Dict[str, Any] = {"test": "data", "nums": [1, 2, 3]}

    storage.save(test_data)
    loaded_data = storage.load()

    assert loaded_data == test_data
    with open(storage.file_path, 'r', encoding='utf-8') as f:
        assert json.load(f) == test_data


def test_context_manager() -> None:
    """Тестируем работу контекстного менеджера."""
    test_data: Dict[str, str] = {"key": "value"}

    with TempVacancyStorage() as storage:
        storage.save(test_data)
        assert Path(storage.file_path).exists()
        assert storage.load() == test_data

    assert not Path(storage.file_path).exists()


def test_file_deletion(storage: TempVacancyStorage) -> None:
    """Проверяем удаление файла при закрытии."""
    file_path = storage.file_path
    storage.close()
    assert not Path(file_path).exists()


def test_save_to_closed_file(storage: TempVacancyStorage) -> None:
    """Проверяем обработку ошибки записи в закрытый файл."""
    storage.close()
    with pytest.raises(ValueError):
        storage.save({"test": "data"})


def test_load_invalid_json(storage: TempVacancyStorage) -> None:
    """Проверяем обработку некорректного JSON."""
    with open(storage.file_path, 'w', encoding='utf-8') as f:
        f.write('invalid json')

    with pytest.raises(json.JSONDecodeError):
        storage.load()