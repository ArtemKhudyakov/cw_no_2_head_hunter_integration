import json

from src.external_api import HeadHunterApiVacancies
from src.favorites_storage import JSONFavoritesStorage
from src.vacancy import Vacancy
from src.viewer import Viewer


def main() -> None:

    print(
        """Привет!
Хочешь сменить работу?
Давай поищем вакансии
"""
    )
    print("Начать поиск вакансий? Да/Нет")
    start_session = ""
    while True:
        start_session = input().lower()
        if start_session == "нет":
            exit()
        elif start_session == "да":
            break
        else:
            print('Введите "да" или "нет"')

    search_completed = False
    while not search_completed:
        params = HeadHunterApiVacancies.params_input()
        position = HeadHunterApiVacancies.position_input(params)
        api_vacancies = HeadHunterApiVacancies(position, params)
        api_vacancies.vacancies_saver()
        with open(api_vacancies.vacancies_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            Viewer.print_vacancies(data)

        while True:
            print("\nХотите повторить поиск вакансий с новыми параметрами? Да/Нет\n")
            repeat = input().lower()
            if repeat == "нет":
                search_completed = True
                break
            elif repeat == "да":
                break
            else:
                print('Введите "да" или "нет"')

        while True:
            print("\nВыбирите дальнейшие действия\n")
            next_action = input(
                """Введите номер операции:
1. Вывести топ N вакансий по зарплате из найденных;
2. Сохранить вакансии в избранное;
3. Посмотреть избранное;
4. Очистить избранное;
5. Удалить вакансии из избранного;
6. Повторить поиск вакансий;
7. Удалить файл категории из избранного
8. Выйти из программы.
"""
            ).lower()
            if next_action != "8":
                vacancies = [Vacancy.from_saved_dict(item) for item in data]

                if next_action == "1":
                    while True:
                        try:
                            n = int(input('\nвведите "N"\n'))
                            if n > 0:
                                break
                            else:
                                print("Ошибка ввода! N должен быть положительным числом")
                        except ValueError:
                            print("Ошибка ввода! Введите целое число для N")

                    sorted_by_salary = Vacancy.sort_by_salary(vacancies, n, True)
                    print(sorted_by_salary)

                elif next_action == "2":
                    vacancy_ids = input("Введите id вакансий для сохранения в избранное\n")
                    favorite_category = input("Введите название категории (название папки) для добавления вакансий\n")
                    favorites = JSONFavoritesStorage(api_vacancies.vacancies_file, favorite_category)
                    favorites.save_favorites(vacancy_ids)

                elif next_action == "3":
                    favorite_category = input("Введите название категории для просмотра избранного\n")
                    favorites = JSONFavoritesStorage(api_vacancies.vacancies_file, favorite_category)
                    favorites_data = favorites.get_favorites()
                    Viewer.print_vacancies(favorites_data)

                elif next_action == "4":
                    clear_favorites = input("Вы точно хотите полностью очистить избранное? Да/Нет\n")
                    if clear_favorites == "да":
                        favorite_category = input("Введите название категории для очистки\n")
                        favorites = JSONFavoritesStorage(api_vacancies.vacancies_file, favorite_category)
                        favorites.clear_favorites()
                    else:
                        continue

                elif next_action == "5":
                    favorite_category = input("Введите название категории (название папки) для удаления вакансий\n")
                    vacancy_ids = input("Введите id вакансий для удаления\n")
                    favorites = JSONFavoritesStorage(api_vacancies.vacancies_file, favorite_category)
                    favorites.remove_from_favorites(vacancy_ids)

                elif next_action == "6":
                    search_completed = False
                    break

                elif next_action == "7":
                    favorite_category = input("Введите название категории (название папки) для удаления\n")
                    favorites = JSONFavoritesStorage(api_vacancies.vacancies_file, favorite_category)
                    favorites.delete_favorites_file()

                else:
                    continue

            else:
                exit()


if __name__ == "__main__":
    main()
