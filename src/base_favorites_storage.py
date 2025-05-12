from abc import ABC, abstractmethod
from typing import Dict, List


class BaseFavoritesStorage(ABC):
    """
    Абстрактный класс для работы с хранилищем вакансий в JSON-файле
    """

    @abstractmethod
    def __init__(self, filename: str):
        """Инициализация с указанием имени файла"""
        pass

    @abstractmethod
    def load_source_vacancies(self) -> List[Dict]:
        """Загружает исходные вакансии"""
        pass

    @abstractmethod
    def load_favorites(self) -> List[Dict]:
        """Загружает избранные вакансии"""
        pass

    @abstractmethod
    def save_favorites(self, favorites_id_str: str) -> None:
        """Сохраняет избранные вакансии"""
        pass

    @abstractmethod
    def remove_from_favorites(self, vacancy_ids: str) -> None:
        """Удаляет вакансии из избранного по id"""
        pass

    @abstractmethod
    def clear_favorites(self) -> None:
        """Удаляет все избранные вакансии из указанной категории"""
        pass

    @abstractmethod
    def delete_favorites_file(self) -> None:
        """Удаляет файл категории из избранного"""
        pass
