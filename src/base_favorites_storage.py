from abc import ABC, abstractmethod
import json
from typing import List, Dict, Any
import pathlib


class BaseFavoritesStorage(ABC):
    """
    Абстрактный класс для работы с хранилищем вакансий в JSON-файле
    """

    @abstractmethod
    def __init__(self, filename: str):
        """Инициализация с указанием имени файла"""
        pass

    @abstractmethod
    def add_vacancy(self, vacancy: Dict[str, Any]) -> None:
        """Добавление вакансии в файл"""
        pass

    @abstractmethod
    def get_vacancies(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Получение вакансий по критериям"""
        pass

    @abstractmethod
    def delete_vacancy(self, vacancy_id: str) -> None:
        """Удаление вакансии по ID"""
        pass

    @abstractmethod
    def clear_all(self) -> None:
        """Полная очистка файла с вакансиями"""
        pass