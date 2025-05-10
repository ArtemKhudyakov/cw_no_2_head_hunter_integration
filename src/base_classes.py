from abc import ABC, abstractmethod
from typing import Any, Dict
import pathlib


class BaseParser(ABC):
    """Абстрактный базовый класс для парсеров вакансий."""

    @abstractmethod
    def __init__(self, position: str, params: Dict[str, Any]):
        """Инициализация парсера"""
        pass

    @property
    @abstractmethod
    def base_url(self) -> str:
        """Базовый URL API"""
        pass

    @property
    @abstractmethod
    def vacancies_file(self) -> pathlib.Path:
        """Путь к файлу с вакансиями"""
        pass

    @abstractmethod
    def load_vacancies(self) -> Any:
        """Загрузка вакансий"""
        pass


    @abstractmethod
    def __repr__(self) -> str:
        """Строковое представление (должен быть реализован)"""
        pass

    @abstractmethod
    def __str__(self) -> str:
        """Строковое представление (должен быть реализован)"""
        pass