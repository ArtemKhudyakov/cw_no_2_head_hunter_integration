import json
from typing import List, Dict
import pathlib as p

from src.base_favorites_storage import BaseFavoritesStorage
import os

from src.vacancy import Vacancy


class JSONFavoritesStorage:
    """
    Реализация хранилища избранных вакансий в JSON-файле
    """

    def __init__(self, source_file: p.Path, favorites_file: str = "favorites"):

        # Путь к корневой папке
        current_file_path = p.Path(__file__).resolve()
        project_root_path = current_file_path.parent.parent

        # Путь к папке data
        data_dir_path = project_root_path / 'data'

        # Путь к папке favorites
        self.__favorites_dir_path = data_dir_path / 'favorite'


        # Создаем папку data, если ее нет
        os.makedirs(data_dir_path, exist_ok=True)
        os.makedirs(self.__favorites_dir_path, exist_ok=True)

        self.__source_file = source_file
        self.__favorites_file = (self.__favorites_dir_path/f'{favorites_file}.json'
                                 if favorites_file != '' else self.__favorites_dir_path/'favorites.json')


    def load_source_vacancies(self) -> List[Dict]:
        """Загружает исходные вакансии"""
        with open(self.__source_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_favorites(self) -> List[Dict]:
        """Загружает избранные вакансии"""
        if not self.__favorites_file.exists():
            return []
        with open(self.__favorites_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_favorites(self,vacancies:list[Vacancy], favorites_id_str: str) -> None:
        """Сохраняет избранные вакансии"""
        favorites_list = []
        favorites_id_list = favorites_id_str.split(',')
        if favorites_id_list:
            for id in favorites_id_list:
                for vacancy in vacancies:
                    if str(id).strip() == str(vacancy.id):
                        favorites_list.append(vacancy.__repr__())
        with open(self.__favorites_file, 'w', encoding='utf-8') as f:
            json.dump(favorites_list, f, ensure_ascii=False, indent=2)
        print(f'Сохранено {len(favorites_list)} вакансий')

    def add_to_favorites(self, vacancies: List[Vacancy], favorites_id_str: str, favorites_file_name) -> None:
        if favorites_file_name:
            favorites_file = self.__favorites_dir_path / f'{favorites_file_name}.json'
        else:
            favorites_file = self.__favorites_file
        favorites = self.load_favorites()

        existing_ids = {v['id'] for v in favorites}
        added_count = 0

        for vacancy in vacancies:
            if vacancy.id in favorites_id_str and vacancy.id not in existing_ids:
                favorites.append(vacancy.__repr__())
                added_count += 1
        with open(favorites_file, 'w', encoding='utf-8') as f:
            json.dump(favorites, f, ensure_ascii=False, indent=2)

        print(f"Добавлено {added_count} вакансий в избранное")


    def get_favorites(self) -> List[Dict]:
        return self.load_favorites()

    def remove_from_favorites(self, vacancy_ids: List[str]) -> None:
        favorites = self.load_favorites()
        new_favorites = [v for v in favorites if v['id'] not in vacancy_ids]

        if len(new_favorites) == len(favorites):
            print("Не найдено вакансий для удаления")
        else:
            with open(self.__favorites_file, 'w', encoding='utf-8') as f:
                json.dump(favorites, f, ensure_ascii=False, indent=2)
            print(f"Удалено {len(favorites) - len(new_favorites)} вакансий")

    def clear_favorites(self) -> None:
        favorites = []
        with open(self.__favorites_file, 'w', encoding='utf-8') as f:
            json.dump(favorites, f, ensure_ascii=False, indent=2)
        print(f"Все вакансии удалены из избранного категории {self.__favorites_file}")


    def delete_favorites_file(self) -> None:
        del self.__favorites_file