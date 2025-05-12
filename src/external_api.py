import json
import os
import pathlib as p
from typing import Any, Dict, Optional, Tuple, Union

import requests

from src.base_parser import BaseParser
from src.temp_vacancy_storage import TempVacancyStorage
from src.viewer import Viewer


class HeadHunterApiVacancies(BaseParser):
    """
    Класс для работы с API HeadHunter
    """

    def __init__(self, position: str, params: Dict[str, Any]) -> None:
        self.__base_url = "https://api.hh.ru"
        self.__params = params
        self.__position = position
        self.headers = {"User-Agent": "HH-User-Agent"}

        # Путь к корневой папке
        current_file_path = p.Path(__file__).resolve()
        project_root_path = current_file_path.parent.parent

        # Путь к папке data
        data_dir_path = project_root_path / "data"

        # Путь к папке areas_data
        areas_data_dir_path = data_dir_path / "areas_data"

        # Путь к папке loaded_vacancies
        loaded_vacancies_dir_path = data_dir_path / "loaded_vacancies"

        # Создаем папку data, если ее нет
        os.makedirs(data_dir_path, exist_ok=True)
        os.makedirs(areas_data_dir_path, exist_ok=True)
        os.makedirs(loaded_vacancies_dir_path, exist_ok=True)

        self.__areas_file = areas_data_dir_path / "areas.json"
        self.__vacancies_file = (
                loaded_vacancies_dir_path / f"{self.__position.lower()}_{self.__params.get('area', '').lower()}.json"
        )

    def __repr__(self) -> str:
        """Возвращает строковое представление объекта"""
        return f"<HeadHunterApiVacancies position={self.__position}>"

    def __str__(self) -> str:
        """Возвращает строковое представление объекта"""
        return self.__repr__()

    @property
    def base_url(self) -> str:
        """Возвращает базовый URL"""
        return self.__base_url

    @property
    def params(self) -> Dict[str, Any]:
        """Возвращает введенные параметры поиска"""
        return self.__params

    @staticmethod
    def params_input() -> Dict[str, Any]:
        """Статический метод для ввода параметров поиска"""
        text = input("\nВведите название вакансии\n")
        area = input("\nВведите город для поиска\n")

        while True:
            try:
                page_input = input("\nВведите номер страницы\n")
                page = int(page_input)
                if page > 0:
                    page -= 1
                    break
                print("Ошибка ввода! Номер страницы должен быть положительным числом")
            except ValueError:
                print("Ошибка ввода! Введите целое число для номера страницы")

        while True:
            try:
                per_page_input = input("\nВведите количество вакансий для вывода на странице\n")
                per_page = int(per_page_input)
                if per_page > 0:
                    break
                print("Ошибка ввода! Количество вакансий должно быть положительным числом")
            except ValueError:
                print("Ошибка ввода! Введите целое число для количества вакансий")

        params: Dict[str, Any] = {
            "text": text,
            "area": area,
            "page": str(page),  # API ожидает строку для параметров
            "per_page": str(per_page)  # API ожидает строку для параметров
        }
        return params

    @staticmethod
    def position_input(params: Dict[str, Any]) -> str:
        """Статический метод, возвращающий должность из параметров поиска"""
        position: str = params.get("text", "")
        return position

    @property
    def vacancies_file(self) -> p.Path:
        """Возвращает путь к файлу БД для записи"""
        return self.__vacancies_file

    def areas_data_refresh(self) -> None:
        """Обновляет данные о регионах с HH и сохраняет в файл."""
        response = requests.get(f"{self.__base_url}/areas/")

        if response.status_code == 200:
            try:
                areas_data = response.json()
                with open(self.__areas_file, "w", encoding="utf-8") as f:
                    json.dump(areas_data, f, ensure_ascii=False, indent=2)
                print(f"Данные регионов обновлены {self.__areas_file}")

            except json.JSONDecodeError:
                raise ValueError("API вернуло невалидный JSON")

            except IOError as e:
                raise IOError(f"Ошибка записи в файл: {e}")

        elif response.status_code == 400:
            raise ValueError("Ошибка в параметрах запроса")

        elif response.status_code == 403:
            raise PermissionError("Доступ запрещен")

        elif response.status_code == 404:
            raise FileNotFoundError("API endpoint не найден")

        elif 500 <= response.status_code < 600:
            raise ConnectionError(f"Ошибка сервера HH (код {response.status_code})")

        else:
            raise ConnectionError(f"Неизвестная ошибка (код {response.status_code})")

    def load_vacancies(self) -> TempVacancyStorage:
        """Загружает вакансии и временно хранит их в temp-файле"""
        url = f"{self.__base_url}/vacancies"
        found = False
        city_info: Dict[str, Union[str, int]] = {"name": "", "id": 0}

        if not self.__areas_file.exists():
            self.areas_data_refresh()

        if self.params["area"]:
            with open(self.__areas_file, "r", encoding="utf-8") as f:
                areas_data = json.load(f)
                for country in areas_data:
                    for region in country["areas"]:
                        if str(self.__params["area"]).lower() == region["name"].lower():
                            found = True
                            city_info = {"name": region["name"], "id": region["id"]}
                            break
                        for city in region["areas"]:
                            if str(self.__params["area"]).lower() == city["name"].lower():
                                found = True
                                city_info = {"name": city["name"], "id": city["id"]}
                                break
                        if found:
                            break
                    if found:
                        break

        if found:
            print(f"Город найден, id = {city_info['id']}, город {city_info['name']}")
            self.__params["area"] = str(city_info["id"])  # API ожидает строку
        else:
            print("Город не найден")
            self.__params["area"] = None

        try:
            response = requests.get(url, headers=self.headers, params=self.__params, timeout=10)

            if response.status_code != 200:
                error_msg = f"Ошибка API (код {response.status_code}): {response.text[:200]}..."
                raise ConnectionError(error_msg)

            vacancies = response.json()
            if not vacancies.get("items"):
                print("Предупреждение: не найдено ни одной вакансии по заданным критериям")

        except requests.RequestException as e:
            print(f"Ошибка сетевого запроса: {e}")
            raise
        except json.JSONDecodeError as e:
            print(f"Ошибка разбора JSON ответа: {e}")
            raise

        storage = TempVacancyStorage()
        storage.save(vacancies)
        return storage

    def vacancies_saver(self) -> None:
        """Сохраняет вакансии в указанный файл. Если файл не существует, создает файл"""
        loaded_vacancies = self.load_vacancies()
        with open(loaded_vacancies.file_path, "r", encoding="utf-8") as f:
            vacancies_data = json.load(f)

        vacancies_formated_data = [
            {
                "id": i["id"],
                "vacancy": i["name"],
                "salary": i["salary"],
                "published_at": i["published_at"],
                "created_at": i["created_at"],
                "employer": i["employer"]["name"],
                "city": i["area"]["name"],
                "requirements": Viewer.clean_html(
                    str(
                        str(i.get("snippet", {}).get("requirement", ""))
                        + str(i.get("snippet", {}).get("responsibility", ""))
                    )
                ),
                "experience": i["experience"]["name"],
                "schedule": i["schedule"]["name"],
                "employment": i["employment"]["name"],
            }
            for i in vacancies_data["items"]
        ]

        with open(self.__vacancies_file, "w", encoding="utf-8") as f:
            json.dump(vacancies_formated_data, f, ensure_ascii=False, indent=2)