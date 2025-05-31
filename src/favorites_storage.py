import json
import os
import pathlib as p
from typing import Any, Dict, List

from src.base_favorites_storage import BaseFavoritesStorage
from src.vacancy import Vacancy


class JSONFavoritesStorage(BaseFavoritesStorage):
    """
    Реализация хранилища избранных вакансий в JSON-файле
    """

    def __init__(self, source_file: p.Path, favorites_file: str = "favorites") -> None:
        # Путь к корневой папке
        current_file_path = p.Path(__file__).resolve()
        project_root_path = current_file_path.parent.parent

        # Путь к папке data
        data_dir_path = project_root_path / "data"

        # Путь к папке favorites
        self.__favorites_dir_path = data_dir_path / "favorite"

        # Создаем папку data, если ее нет
        os.makedirs(data_dir_path, exist_ok=True)
        os.makedirs(self.__favorites_dir_path, exist_ok=True)

        self.__source_file = source_file
        self.__favorites_file = (
            self.__favorites_dir_path / f"{favorites_file}.json"
            if favorites_file != ""
            else self.__favorites_dir_path / "favorites.json"
        )

    def source_file(self) -> p.Path:
        return self.__source_file

    def favorites_file(self) -> p.Path:
        return self.__favorites_file

    def load_source_vacancies(self) -> List[Dict[str, Any]]:
        """Загружает исходные вакансии"""
        with open(self.__source_file, "r", encoding="utf-8") as f:
            data: List[Dict[str, Any]] = json.load(f)
            return data

    def load_favorites(self) -> List[Dict[str, Any]]:
        """Загружает избранные вакансии"""
        if not self.__favorites_file.exists():
            return []
        with open(self.__favorites_file, "r", encoding="utf-8") as f:
            data: List[Dict[str, Any]] = json.load(f)
            return data

    def save_favorites(self, favorites_id_str: str) -> None:
        """Сохраняет избранные вакансии"""
        favorites_list: List[Dict[str, Any]] = []
        if self.__favorites_file.exists():
            favorites_list = self.load_favorites()

        start_numb = len(favorites_list)
        favorites_id_list = favorites_id_str.split(",")
        data = self.load_source_vacancies()
        vacancies = [Vacancy.from_saved_dict(item) for item in data]

        if favorites_id_list:
            for id_ in favorites_id_list:
                for vacancy in vacancies:
                    if str(id_).strip() == str(vacancy.id):
                        favorites_list.append(vacancy.to_dict())

        with open(self.__favorites_file, "w", encoding="utf-8") as f:
            json.dump(favorites_list, f, ensure_ascii=False, indent=2)
        print(f"Сохранено {len(favorites_list) - start_numb} вакансий")

    def get_favorites(self) -> List[Dict[str, Any]]:
        """Получает список вакансий из загруженных избранных вакансий"""
        return self.load_favorites()

    def remove_from_favorites(self, vacancy_ids: str) -> None:
        """Удаляет вакансии из избранного по id"""
        if not self.__favorites_file.exists():
            print("Категории не существует!")
            return

        favorites: List[Dict[str, Any]] = self.load_favorites()
        vacancy_ids_list = [id_.strip() for id_ in vacancy_ids.split(",")]
        new_favorites = [v for v in favorites if v["id"] not in vacancy_ids_list]

        if len(new_favorites) == len(favorites):
            print("Не найдено вакансий для удаления")
        else:
            with open(self.__favorites_file, "w", encoding="utf-8") as f:
                json.dump(new_favorites, f, ensure_ascii=False, indent=2)
            print(f"Удалено {len(favorites) - len(new_favorites)} вакансий")

    def clear_favorites(self) -> None:
        """Удаляет все избранные вакансии из указанной категории"""
        if not self.__favorites_file.exists():
            print("Категории не существует, нечего очищать!")
            return

        favorites: List[Dict[str, Any]] = []
        with open(self.__favorites_file, "w", encoding="utf-8") as f:
            json.dump(favorites, f, ensure_ascii=False, indent=2)
        print(f"Все вакансии удалены из избранного категории {self.__favorites_file}")

    def delete_favorites_file(self) -> None:
        """Удаляет файл категории из избранного"""
        if not self.__favorites_file.exists():
            print("Категории не существует, нечего удалять!")
            return

        try:
            self.__favorites_file.unlink()  # Удаляем файл с диска
            print(f"Файл {self.__favorites_file} успешно удален")
        except Exception as e:
            print(f"Ошибка при удалении файла: {e}")
