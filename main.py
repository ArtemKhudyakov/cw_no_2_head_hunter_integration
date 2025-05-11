import json
from src.vacancy import Vacancy
from src.viewer import Viewer
from src.external_api import HeadHunterApiVacancies
from src.favorites_storage import JSONFavoritesStorage

if __name__ == '__main__':
    # params = HeadHunterApiVacancies.params_input()
    # position = HeadHunterApiVacancies.position_input(params)
    # vacancies1 = HeadHunterApiVacancies(position, params)

    params = {'text': 'инженер по сварке',
                  'area': 'Челябинск',
                  'page': 0,
                  'per_page': 5}
    position = HeadHunterApiVacancies.position_input(params)
    vacancies1 = HeadHunterApiVacancies(position, params)
    vacancies1.vacancies_saver()
    with open(vacancies1.vacancies_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for vacancy in data:
            Viewer.print_vacancy(vacancy)
            print("\n" + "=" * 50 + "\n")

    # Преобразование в объекты Vacancy
    vacancies = [Vacancy.from_saved_dict(item) for item in data]
    # sorted_by_salary = sorted(vacancies, reverse=True)
    # print("Топ-5 вакансий по зарплате:")
    # for v in sorted_by_salary[:5]:
    #     print(f"{v.title} | {v.format_salary()}")

    vacancy_ids = input('Введите id вакансий для сохранения в избранное\n')
    favorite_category = input('Введите название категории (название папки) для добавления вакансий\n')
    favorites = JSONFavoritesStorage(vacancies1.vacancies_file, favorite_category)
    favorites.save_favorites(vacancies, vacancy_ids)
    favorites_data = favorites.get_favorites()
    Viewer.print_vacancies(favorites_data)
    vacancy_ids = input('Введите id вакансий для добавления в избранное\n')
    favorite_category = input('Введите название категории (название папки) для добавления вакансий\n')
    favorites.add_to_favorites(vacancies, vacancy_ids, favorite_category)

