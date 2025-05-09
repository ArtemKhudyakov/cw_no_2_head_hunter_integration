import requests
import json
import pathlib as p
import os
from typing import Any
from colorama import Fore, Back, Style, init
import re

from src.temp_vacancy_storage import TempVacancyStorage
from src.viewer import Viewer

# Инициализация Colorama
init(autoreset=True)


class HeadHunterApiVacancies:
    """
    Класс для работы с API HeadHunter
    Класс Parser является родительским классом, который вам необходимо реализовать
    """

    def __init__(self, position: str, params: dict[str, Any]) -> None:
        self.__base_url = 'https://api.hh.ru'
        self.__params = params
        self.__position = position
        # params.get('text', None)
        self.headers = {'User-Agent': 'HH-User-Agent'}

        # Путь к корневой папке
        current_file_path = p.Path(__file__).resolve()
        project_root_path = current_file_path.parent.parent

        # Путь к папке data
        data_dir_path = project_root_path / 'data'

        # Создаем папку data, если ее нет
        os.makedirs(data_dir_path, exist_ok=True)

        self.__areas_file = data_dir_path / 'areas.json'
        self.__vacancies_file = data_dir_path / f'{self.__position}_{self.__params.get('area', '')}.json'

    def __repr__(self) -> str:
        return f'<HeadHunterApiVacancies position={self.__position}>'

    def __str__(self) -> str:
        return self.__repr__()

    @property
    def base_url(self) -> str:
        return self.__base_url

    @property
    def params(self) -> dict[str, Any]:
        return self.__params

    @property
    def vacancies_file(self) -> p.Path:
        return self.__vacancies_file

    def areas_data_refresh(self) -> None:
        """
        Обновляет данные о регионах с HH и сохраняет в файл.
        В случае ошибок выбрасывает исключения с описанием.
        """
        response = requests.get(f'{self.__base_url}/areas/')

        if response.status_code == 200:
            try:
                areas_data = response.json()
                with open(self.__areas_file, 'w', encoding='utf-8') as f:
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
        url = f'{self.__base_url}/vacancies'
        found = False
        if not self.__areas_file.exists():
            self.areas_data_refresh()
        if self.params['area']:
            with open(self.__areas_file, 'r', encoding='utf-8') as f:
                areas_data = json.load(f)
                for country in areas_data:
                    for region in country['areas']:
                        if str(self.__params['area']).lower() == region['name'].lower():
                            found = True
                            city_info = {'name': region['name'], 'id': region['id']}
                            break
                        for city in region['areas']:
                            if str(self.__params['area']).lower() == city['name'].lower():
                                found = True
                                city_info = {'name': city['name'], 'id': city['id']}
                                break
                            else:
                                found = False
                        if found:
                            break
                    if found:
                        break
        if found:
            print(f"город найден, id = {city_info['id']}, город {city_info['name']}")
            self.__params['area'] = city_info['id']
        else:
            print('город не найден')
            self.__params['area'] = None

        try:
            response = requests.get(
                url,
                headers=self.headers,
                params=self.__params,
                timeout=10  # Таймаут 10 секунд
            )

            # Проверка статуса ответа
            if response.status_code != 200:
                error_msg = f"Ошибка API (код {response.status_code}): {response.text[:200]}..."
                raise ConnectionError(error_msg)
            else:

                vacancies = response.json()
                if not vacancies.get('items'):
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
        loaded_vacancies = self.load_vacancies()
        with open(loaded_vacancies.file_path, 'r', encoding='utf-8') as f:
            vacancies_data = json.load(f)
        vacancies_formated_data = [
            {'id': i['id'], 'vacancy': i['name'], 'salary': i['salary'], 'published_at': i['published_at'],
             'created_at': i['created_at'], 'employer': i['employer']['name'], 'city': i['area']['name'],
             'requirements': Viewer.clean_html(
                 str(str(i.get('snippet', '').get('requirement', '')) + str(
                     i.get('snippet', '').get('responsibility', '')))),
             'experience': i['experience']['name'], 'schedule': i['schedule']['name'],
             'employment': i['employment']['name'], 'employment_form': i['employment_form']['name']} for i in
            vacancies_data['items']]
        with open(self.__vacancies_file, 'w', encoding='utf-8') as f:
            json.dump(vacancies_formated_data, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    params = {'text': 'Инженер по сварке', 'area': 'Екатеринбург', 'page': 0, 'per_page': 10}
    vacancies1 = HeadHunterApiVacancies('Инженер по сварке', params)

    vacancies1.vacancies_saver()
    with open(vacancies1.vacancies_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        print(data)
        for vacancy in data:
            Viewer.print_vacancy(vacancy)
            print("\n" + "=" * 50 + "\n")
        print(len(data))

        # for vacancy.py in data['items']:
        #     HeadHunterApiVacancies.print_colorful_vacancy(vacancy.py)
        #     print("\n" + "=" * 50 + "\n")
