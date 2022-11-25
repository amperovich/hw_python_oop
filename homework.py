import csv
from dataclasses import dataclass
from enum import Enum
from typing import List


class IncorrectInputDataError(Exception):
    """Сообщает о некоректных входных данных в пакете."""


@dataclass
class InfoMessage:
    """Информационное сообщение о тренировке.

    Возвращает данные, обработанные классом Training и его дочерними классами,
    в виде строки для последующей печати на экран.

    Attributes:
        training_type (str): тип тренировки (пример: "RUN", "SWM");
        duration (float): продолжительность тренировки (ч.);
        distance (float): расстояние, пройденное в течении тренировки (км);
        speed (float): средняя скорость тренирующегося (км/ч);
        calories (float): энергия, затраченная тренирующимся (ккал).

    """

    training_type: str
    duration: float
    distance: float
    speed: float
    calories: float

    def get_message(self) -> str:
        return (
            f'Тип тренировки: {self.training_type}; '
            f'Длительность: {self.duration:.3f} ч.; '
            f'Дистанция: {self.distance:.3f} км; '
            f'Ср. скорость: {self.speed:.3f} км/ч; '
            f'Потрачено ккал: {self.calories:.3f}.'
        )


class Training:
    """Базовый класс тренировки.

    Производит расчёт параметров на основе входных данных.

    Attributes:
        action (float): число шагов;
        duration (float): продолжительность тренировки (ч.);
        weight (float): вес тренирующегося (кг).

    """

    LEN_STEP = 0.65
    M_IN_KM = 1000
    MIN_IN_H = 60

    def __init__(
        self,
        action: float,
        duration: float,
        weight: float,
    ) -> None:
        self.action = action
        self.duration = duration
        self.weight = weight

    def get_distance(self) -> float:
        return self.action * self.LEN_STEP / self.M_IN_KM

    def get_mean_speed(self) -> float:
        return self.get_distance() / self.duration

    def get_spent_calories(self) -> float:
        """Расчитывает калории.

        Для каждого дочернего класса применяется своя отдельная формула.

        Raises:
            NotImplementedError: не переопределён метод в дочернем классе.

        """
        raise NotImplementedError

    def show_training_info(self) -> InfoMessage:
        return InfoMessage(
            type(self).__name__,
            self.duration,
            self.get_distance(),
            self.get_mean_speed(),
            self.get_spent_calories(),
        )


class Running(Training):
    CALORIES_MEAN_SPEED_MULTIPLIER = 18
    CALORIES_MEAN_SPEED_SHIFT = 1.79

    def get_spent_calories(self) -> float:
        return (
            (
                self.CALORIES_MEAN_SPEED_MULTIPLIER * self.get_mean_speed()
                + self.CALORIES_MEAN_SPEED_SHIFT
            )
            * self.weight
            / self.M_IN_KM
            * self.duration
            * self.MIN_IN_H
        )


class SportsWalking(Training):
    CALORIES_WEIGHT_MULTIPLIER = 0.035
    CALORIES_SPEED_HEIGHT_MULTIPLIER = 0.029
    KMH_IN_MSEC = 0.278  # Training.M_IN_KM / (Training.MIN_IN_H * 60)
    CM_IN_M = 100

    def __init__(
        self,
        action: float,
        duration: float,
        weight: float,
        height: float,
    ) -> None:
        super().__init__(action, duration, weight)
        self.height = height

    def get_spent_calories(self) -> float:
        return (
            (
                self.CALORIES_WEIGHT_MULTIPLIER * self.weight
                + (
                    (self.get_mean_speed() * self.KMH_IN_MSEC) ** 2
                    / (self.height / self.CM_IN_M)
                )
                * self.CALORIES_SPEED_HEIGHT_MULTIPLIER
                * self.weight
            )
            * self.duration
            * self.MIN_IN_H
        )


class Swimming(Training):
    MEAN_SPEED_SHIFT = 1.1
    WEIGHT_MULTIPLIER = 2
    LEN_STEP = 1.38

    def __init__(
        self,
        action: float,
        duration: float,
        weight: float,
        length_pool: float,
        count_pool: float,
    ) -> None:
        super().__init__(action, duration, weight)
        self.length_pool = length_pool
        self.count_pool = count_pool

    def get_mean_speed(self) -> float:
        return (
            self.length_pool * self.count_pool / self.M_IN_KM / self.duration
        )

    def get_spent_calories(self) -> float:
        return (
            (self.get_mean_speed() + self.MEAN_SPEED_SHIFT)
            * self.WEIGHT_MULTIPLIER
            * self.weight
            * self.duration
        )


class WorkoutTypes(Enum):
    RUN = Running
    WLK = SportsWalking
    SWM = Swimming


def read_package(workout_type: str, data: List[float]) -> Training:
    try:
        return WorkoutTypes[workout_type].value(*data)
    except (KeyError, TypeError) as err:
        raise IncorrectInputDataError(f'{err}')


def main(training: Training) -> None:
    print(training.show_training_info().get_message())  # noqa: T201


if __name__ == '__main__':
    with open('packages.csv') as reader:
        packages = csv.reader(reader)
        for row in packages:
            workout_type, *data = row
            try:
                main(
                    read_package(
                        workout_type,
                        [float(number) for number in data],
                    ),
                )
            except (ValueError, IncorrectInputDataError) as err:
                print(f'Неправильные входные данные: {err}')  # noqa: T201
