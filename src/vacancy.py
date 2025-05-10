from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

# Перечисление для стандартизации опыта работы
class ExperienceLevel(Enum):
    NO_EXPERIENCE = "Нет опыта"
    BETWEEN_1_3 = "От 1 года до 3 лет"
    BETWEEN_3_6 = "От 3 до 6 лет"
    MORE_6 = "Более 6 лет"

# Перечисление для графиков работы
class ScheduleType(Enum):
    FULL_DAY = "Полный день"
    SHIFT = "Сменный график"
    FLEXIBLE = "Гибкий график"
    REMOTE = "Удаленная работа"
    SHIFT_METHOD = "Вахтовый метод"


@dataclass
class Vacancy:
    id: str
    title: str
    salary_from: Optional[int]
    salary_to: Optional[int]
    currency: str
    employer: str
    city: str
    requirements: str
    experience: str
    schedule: str
    url: str

    def __post_init__(self):
        """Валидация данных при создании."""
        if not self.title.strip():
            raise ValueError("Название вакансии не может быть пустым")
        self.salary_from = self.salary_from or 0
        self.salary_to = self.salary_to or 0
        self.currency = self.currency or "RUR"

    def __str__(self):
        salary = self.format_salary()
        return (
            f"{self.title}\n"
            f"Компания: {self.employer}\n"
            f"Зарплата: {salary}\n"
            f"Город: {self.city}\n"
            f"Требования: {self.requirements[:100]}...\n"
            f"Ссылка: {self.url}"
        )

    def format_salary(self) -> str:
        """Форматирует зарплату для вывода."""
        if not (self.salary_from or self.salary_to):
            return "Не указана"
        parts = []
        if self.salary_from:
            parts.append(f"от {self.salary_from}")
        if self.salary_to:
            parts.append(f"до {self.salary_to}")
        if self.currency:
            parts.append(self.currency)
        return " ".join(parts)

    # Методы сравнения (по минимальной зарплате)
    def __lt__(self, other: 'Vacancy') -> bool:
        return self.salary_from < other.salary_from

    def __gt__(self, other: 'Vacancy') -> bool:
        return self.salary_from > other.salary_from


    @classmethod
    def from_saved_dict(cls, saved_data: Dict[str, Any]) -> 'Vacancy':
        """Создает Vacancy из сохраненных данных (из JSON/БД)."""

        salary_data = saved_data.get("salary") or {}

        return cls(
            id=saved_data.get("id", ""),
            title=saved_data.get("vacancy", ""),
            salary_from=salary_data.get("from"),
            salary_to=salary_data.get("to"),
            currency=salary_data.get("currency", "RUR"),
            employer=saved_data.get("employer", ""),
            city=saved_data.get("city", ""),
            requirements=saved_data.get("requirements", ""),
            experience=saved_data.get("experience", ""),
            schedule=saved_data.get("schedule", ""),
            url=f"https://hh.ru/vacancy/{saved_data.get('id', '')}"
        )


    # Методы для сортировки и фильтрации
    @property
    def experience_level(self) -> ExperienceLevel:
        """Преобразует текст опыта в стандартизированный Enum."""
        exp_text = self.experience.lower()
        if "нет опыта" in exp_text:
            return ExperienceLevel.NO_EXPERIENCE
        elif "от 1 года" in exp_text:
            return ExperienceLevel.BETWEEN_1_3
        elif "от 3" in exp_text or "до 6" in exp_text:
            return ExperienceLevel.BETWEEN_3_6
        elif "более 6" in exp_text:
            return ExperienceLevel.MORE_6
        else:
            return ExperienceLevel.NO_EXPERIENCE

    @property
    def schedule_type(self) -> ScheduleType:
        """Определяет тип графика работы."""
        schedule_text = self.schedule.lower()
        if "вахт" in schedule_text:
            return ScheduleType.SHIFT_METHOD
        elif "удален" in schedule_text:
            return ScheduleType.REMOTE
        elif "смен" in schedule_text:
            return ScheduleType.SHIFT
        elif "гибк" in schedule_text:
            return ScheduleType.FLEXIBLE
        else:
            return ScheduleType.FULL_DAY

    # Методы для фильтрации
    @staticmethod
    def filter_by_schedule(vacancies: List['Vacancy'], schedule: ScheduleType) -> List['Vacancy']:
        """Фильтрует вакансии по графику работы."""
        return [v for v in vacancies if v.schedule_type == schedule]

    @staticmethod
    def filter_by_experience(vacancies: List['Vacancy'], experience: ExperienceLevel) -> List['Vacancy']:
        """Фильтрует вакансии по опыту работы."""
        return [v for v in vacancies if v.experience_level == experience]

    # Методы для сортировки
    @staticmethod
    def sort_by_experience(vacancies: List['Vacancy'], reverse: bool = False) -> List['Vacancy']:
        """Сортирует вакансии по уровню опыта."""
        return sorted(
            vacancies,
            key=lambda x: x.experience_level.value,
            reverse=reverse
        )