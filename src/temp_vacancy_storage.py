import json
import os
import tempfile
from typing import Any, Optional, Type

class TempVacancyStorage:
    def __init__(self) -> None:
        """Создает временный файл при инициализации"""
        self.temp_file = tempfile.NamedTemporaryFile(
            mode="w+",
            encoding="utf-8",
            suffix="_vacancies.json",
            delete=False,  # Отключаем автоудаление, будем удалять вручную
        )
        # print(f"Создан временный файл: {os.path.basename(self.temp_file.name)}")

    @property
    def file_path(self) -> Any:
        """Возвращает полный путь к временному файлу"""
        return self.temp_file.name

    def save(self, data: dict) -> None:
        """Сохраняет данные в файл"""
        self.temp_file.seek(0)
        json.dump(data, self.temp_file, ensure_ascii=False, indent=2)
        self.temp_file.flush()  # Принудительно записываем на диск
        # print(f"Данные сохранены в {os.path.basename(self.temp_file.name)}")

    def load(self) -> Any:
        """Читает данные из файла"""
        self.temp_file.seek(0)
        return json.load(self.temp_file)

    def close(self) -> None:
        """Закрывает и удаляет файл"""
        if not self.temp_file.closed:
            self.temp_file.close()
            os.unlink(self.temp_file.name)  # Удаляем файл
            # print(f"Файл {os.path.basename(self.temp_file.name)} удален")

    # Вызовется автоматически при выходе из with
    def __enter__(self) -> "TempVacancyStorage":
        """Реализация протокола контекстного менеджера."""
        return self

    # Вызовется автоматически при завершении блока with
    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> None:
        """Завершение работы контекстного менеджера."""
        self.close()

    # Вызовется при удалении объекта сборщиком мусора
    def __del__(self) -> None:
        """Удаление объекта."""
        self.close()
