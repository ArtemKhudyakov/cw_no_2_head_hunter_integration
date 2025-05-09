import json
from src.vacancy import Vacancy, ExperienceLevel, ScheduleType
from src.viewer import Viewer
from src.external_api import HeadHunterApiVacancies


if __name__ == '__main__':
    params = {'text': 'Инженер по сварке', 'area': 'Екатеринбург', 'page': 0, 'per_page': 10}
    vacancies1 = HeadHunterApiVacancies('Инженер по сварке', params)

    vacancies1.vacancies_saver()
    with open(vacancies1.vacancies_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for vacancy in data:
            Viewer.print_vacancy(vacancy)
            print("\n" + "=" * 50 + "\n")

# Преобразование в объекты Vacancy
vacancies = [Vacancy.from_saved_dict(item) for item in data]
sorted_by_salary = sorted(vacancies, reverse=True)
print("Топ-5 вакансий по зарплате:")
for v in sorted_by_salary[:5]:
    print(f"{v.title} | {v.format_salary()}")
