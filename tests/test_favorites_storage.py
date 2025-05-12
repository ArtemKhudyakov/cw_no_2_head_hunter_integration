import json
from typing import Any, Dict, List

import pytest

from src.favorites_storage import JSONFavoritesStorage


def test_load_source_vacancies(storage2: JSONFavoritesStorage, sample_vacancy2: Dict[str, Any]) -> None:
    vacancies: List[Dict[str, Any]] = storage2.load_source_vacancies()
    assert len(vacancies) == 1


def test_load_favorites_existing(storage2: JSONFavoritesStorage, sample_vacancy2: Dict[str, Any]) -> None:
    # Создаем файл с избранными вакансиями
    with open(storage2.favorites_file(), "w", encoding="utf-8") as f:
        json.dump([sample_vacancy2], f)

    favorites: List[Dict[str, Any]] = storage2.load_favorites()
    assert len(favorites) == 1
    assert favorites[0]["id"] == sample_vacancy2["id"]


def test_save_favorites_invalid_id(storage2: JSONFavoritesStorage) -> None:
    initial_count: int = len(storage2.load_favorites())
    storage2.save_favorites("999")  # Несуществующий ID
    favorites: List[Dict[str, Any]] = storage2.load_favorites()
    assert len(favorites) == initial_count  # Количество не изменилось


def test_get_favorites(storage2: JSONFavoritesStorage, sample_vacancy2: Dict[str, Any]) -> None:
    # Предварительно сохраняем вакансию
    with open(storage2.favorites_file(), "w", encoding="utf-8") as f:
        json.dump([sample_vacancy2], f)

    favorites: List[Dict[str, Any]] = storage2.get_favorites()
    assert len(favorites) == 1
    assert favorites[0]["id"] == "1"


def test_remove_from_favorites(storage2: JSONFavoritesStorage, sample_vacancy2: Dict[str, Any]) -> None:
    # Добавляем две вакансии
    with open(storage2.favorites_file(), "w", encoding="utf-8") as f:
        json.dump([sample_vacancy2, {**sample_vacancy2, "id": "2"}], f)

    storage2.remove_from_favorites("1,2")
    favorites: List[Dict[str, Any]] = storage2.load_favorites()
    assert len(favorites) == 0


def test_remove_nonexistent_vacancies(storage2: JSONFavoritesStorage, sample_vacancy2: Dict[str, Any]) -> None:
    # Добавляем одну вакансию
    with open(storage2.favorites_file(), "w", encoding="utf-8") as f:
        json.dump([sample_vacancy2], f)

    storage2.remove_from_favorites("999")  # Несуществующий ID
    favorites: List[Dict[str, Any]] = storage2.load_favorites()
    assert len(favorites) == 1  # Вакансия осталась


def test_clear_favorites(storage2: JSONFavoritesStorage, sample_vacancy2: Dict[str, Any]) -> None:
    # Добавляем вакансии
    with open(storage2.favorites_file(), "w", encoding="utf-8") as f:
        json.dump([sample_vacancy2], f)

    storage2.clear_favorites()
    favorites: List[Dict[str, Any]] = storage2.load_favorites()
    assert len(favorites) == 0


def test_delete_favorites_file(storage2: JSONFavoritesStorage, sample_vacancy2: Dict[str, Any]) -> None:
    # Создаем файл
    with open(storage2.favorites_file(), "w", encoding="utf-8") as f:
        json.dump([sample_vacancy2], f)

    storage2.delete_favorites_file()
    assert not storage2.favorites_file().exists()


def test_delete_nonexistent_file(storage2: JSONFavoritesStorage) -> None:
    # Файл не существует
    storage2.delete_favorites_file()  # Не должно вызывать ошибок
    assert not storage2.favorites_file().exists()


def test_error_handling_load_source(storage2: JSONFavoritesStorage) -> None:
    # Повреждаем исходный файл
    with open(storage2.source_file(), "w", encoding="utf-8") as f:
        f.write("invalid json")

    with pytest.raises(json.JSONDecodeError):
        storage2.load_source_vacancies()


def test_error_handling_load_favorites(storage2: JSONFavoritesStorage) -> None:
    # Повреждаем файл избранного
    with open(storage2.favorites_file(), "w", encoding="utf-8") as f:
        f.write("invalid json")

    with pytest.raises(json.JSONDecodeError):
        storage2.load_favorites()
