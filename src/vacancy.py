from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class ExperienceLevel(Enum):
    NO_EXPERIENCE = "Нет опыта"
    BETWEEN_1_3 = "От 1 года до 3 лет"
    BETWEEN_3_6 = "От 3 до 6 лет"
    MORE_6 = "Более 6 лет"


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

    def __post_init__(self) -> None:
        """Валидация данных при создании."""
        if not self.title.strip():
            raise ValueError("Название вакансии не может быть пустым")
        self.salary_from = self.salary_from if self.salary_from is not None else 0
        self.salary_to = self.salary_to if self.salary_to is not None else 0
        self.currency = self.currency or "RUR"

    def __str__(self) -> str:
        salary = self.format_salary()
        return (
            f"{self.title}\n"
            f"Компания: {self.employer}\n"
            f"Зарплата: {salary}\n"
            f"Город: {self.city}\n"
            f"Требования: {self.requirements}\n"
            f"Ссылка: {self.url}"
        )

    def __repr__(self) -> str:
        """Возвращает строковое представление вакансии."""
        return (
            f"Vacancy(id={self.id!r}, title={self.title!r}, "
            f"salary_from={self.salary_from}, salary_to={self.salary_to}, "
            f"currency={self.currency!r}, employer={self.employer!r}, "
            f"city={self.city!r}, requirements={self.requirements!r}, "
            f"experience={self.experience!r}, schedule={self.schedule!r}, "
            f"url={self.url!r})"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Возвращает словарь с данными вакансии."""
        return {
            "id": self.id,
            "vacancy": self.title,
            "salary": {"from": self.salary_from, "to": self.salary_to, "currency": self.currency},
            "employer": self.employer,
            "city": self.city,
            "requirements": self.requirements,
            "experience": self.experience,
            "schedule": self.schedule,
            "url": self.url,
        }

    def format_salary(self) -> str:
        """Форматирует зарплату для вывода."""
        if self.salary_from is None and self.salary_to is None:
            return "Не указана"

        parts = []
        if self.salary_from is not None:
            parts.append(f"от {self.salary_from}")
        if self.salary_to is not None:
            parts.append(f"до {self.salary_to}")
        if self.currency:
            parts.append(self.currency)
        return " ".join(parts)

    def __lt__(self, other: "Vacancy") -> bool:
        """Сравнение по минимальной зарплате."""
        self_salary = 0 if self.salary_from is None else self.salary_from
        other_salary = 0 if other.salary_from is None else other.salary_from
        return self_salary < other_salary

    def __gt__(self, other: "Vacancy") -> bool:
        """Сравнение по минимальной зарплате."""
        self_salary = 0 if self.salary_from is None else self.salary_from
        other_salary = 0 if other.salary_from is None else other.salary_from
        return self_salary > other_salary

    @classmethod
    def from_saved_dict(cls, saved_data: Dict[str, Any]) -> "Vacancy":
        """Создает Vacancy из сохраненных данных (из JSON/БД)."""
        salary_data = saved_data.get("salary", {}) or {}  # Добавляем fallback на пустой dict

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
            url=f"https://hh.ru/vacancy/{saved_data.get('id', '')}",
        )

    @property
    def experience_level(self) -> ExperienceLevel:
        """Преобразует текст опыта в стандартизированный Enum."""
        exp_text = self.experience.lower()
        if "нет опыта" in exp_text:
            return ExperienceLevel.NO_EXPERIENCE
        if "от 1 года" in exp_text:
            return ExperienceLevel.BETWEEN_1_3
        if "от 3" in exp_text or "до 6" in exp_text:
            return ExperienceLevel.BETWEEN_3_6
        if "более 6" in exp_text:
            return ExperienceLevel.MORE_6
        return ExperienceLevel.NO_EXPERIENCE

    @property
    def schedule_type(self) -> ScheduleType:
        """Определяет тип графика работы."""
        schedule_text = self.schedule.lower()
        if "вахт" in schedule_text:
            return ScheduleType.SHIFT_METHOD
        if "удален" in schedule_text:
            return ScheduleType.REMOTE
        if "смен" in schedule_text:
            return ScheduleType.SHIFT
        if "гибк" in schedule_text:
            return ScheduleType.FLEXIBLE
        return ScheduleType.FULL_DAY

    @staticmethod
    def filter_by_schedule(vacancies: List["Vacancy"], schedule: ScheduleType) -> List["Vacancy"]:
        """Фильтрует вакансии по графику работы."""
        return [v for v in vacancies if v.schedule_type == schedule]

    @staticmethod
    def filter_by_experience(vacancies: List["Vacancy"], experience: ExperienceLevel) -> List["Vacancy"]:
        """Фильтрует вакансии по опыту работы."""
        return [v for v in vacancies if v.experience_level == experience]

    @staticmethod
    def sort_by_experience(vacancies: List["Vacancy"], reverse: bool = False) -> List["Vacancy"]:
        """Сортирует вакансии по уровню опыта."""
        return sorted(vacancies, key=lambda x: x.experience_level.value, reverse=reverse)

    @staticmethod
    def sort_by_salary(vacancies: List["Vacancy"], n: int, reverse: bool = True) -> str:
        """Сортирует вакансии по минимальной зарплате и возвращает строку с результатами."""
        if not vacancies:
            return "Нет вакансий для сортировки"

        sorted_vacancies = sorted(vacancies, reverse=reverse)[:n]
        result = []
        for vacancy in sorted_vacancies:
            salary_str = vacancy.format_salary()
            result.append(
                "=" * 50 + f"\nID: {vacancy.id}\n"
                f"Вакансия: {vacancy.title}\n"
                f"Компания: {vacancy.employer}, город: {vacancy.city}\n"
                f"Зарплата: {salary_str}\n"
            )

        return "\n".join(result)
