"""Гидравлический калькулятор.

Простые инженерные расчёты для гидроцилиндра, насоса и трубопровода.
Запуск: python hydro_calc.py
"""

import math


# ---------- Вспомогательные функции ----------

def _check_positive(**values):
    """Проверяет, что все переданные значения больше нуля."""
    for name, value in values.items():
        if not value > 0:
            raise ValueError(f"Значение '{name}' должно быть больше нуля")


def _check_efficiency(name, value):
    """КПД должен быть в пределах от 0 (не включая) до 1 (включительно)."""
    if not 0 < value <= 1:
        raise ValueError(f"'{name}' должен быть в диапазоне от 0 до 1")


# ---------- Гидроцилиндр ----------

def cylinder_area_m2(bore_mm, rod_mm=0):
    """Рабочая площадь поршня, м².

    Для хода выдвижения штока rod_mm = 0 (площадь всего поршня).
    Для хода втягивания передаётся диаметр штока (кольцевая площадь).
    """
    _check_positive(bore_mm=bore_mm)
    if rod_mm < 0 or rod_mm >= bore_mm:
        raise ValueError("Диаметр штока должен быть меньше диаметра поршня")
    bore_m = bore_mm / 1000
    rod_m = rod_mm / 1000
    return math.pi * (bore_m ** 2 - rod_m ** 2) / 4


def cylinder_force_kn(pressure_bar, bore_mm, rod_mm=0):
    """Усилие на штоке, кН: F = p * A."""
    _check_positive(pressure_bar=pressure_bar)
    area = cylinder_area_m2(bore_mm, rod_mm)
    force_n = pressure_bar * 1e5 * area  # 1 бар = 100 000 Па
    return force_n / 1000


def cylinder_speed_mm_s(flow_l_min, bore_mm, rod_mm=0):
    """Скорость штока, мм/с: v = Q / A."""
    _check_positive(flow_l_min=flow_l_min)
    area = cylinder_area_m2(bore_mm, rod_mm)
    flow_m3_s = flow_l_min / 60000  # л/мин -> м³/с
    return flow_m3_s / area * 1000


# ---------- Насос ----------

def pump_flow_l_min(displacement_cm3, rpm, volumetric_eff=1.0):
    """Подача насоса, л/мин: Q = V * n * η_об / 1000."""
    _check_positive(displacement_cm3=displacement_cm3, rpm=rpm)
    _check_efficiency("Объёмный КПД", volumetric_eff)
    return displacement_cm3 * rpm * volumetric_eff / 1000


def pump_power_kw(flow_l_min, pressure_bar, total_eff=1.0):
    """Мощность на валу насоса, кВт: P = Q * p / (600 * η)."""
    _check_positive(flow_l_min=flow_l_min, pressure_bar=pressure_bar)
    _check_efficiency("Общий КПД", total_eff)
    return flow_l_min * pressure_bar / (600 * total_eff)


# ---------- Трубопровод ----------

# Ориентировочные скорости потока масла, м/с. Для реальных проектов
# нужно сверяться с каталогами производителей и нормативами.
LINE_RANGES = {
    "suction": (0.5, 1.5),   # всасывающая линия
    "return": (1.5, 3.0),    # сливная линия
    "pressure": (3.0, 6.0),  # напорная линия
}


def pipe_velocity_m_s(flow_l_min, inner_diameter_mm):
    """Скорость потока в трубе, м/с: v = Q / A."""
    _check_positive(flow_l_min=flow_l_min, inner_diameter_mm=inner_diameter_mm)
    area = math.pi * (inner_diameter_mm / 1000) ** 2 / 4
    return flow_l_min / 60000 / area


def velocity_note(velocity, line_type):
    """Словесная оценка скорости для выбранной линии."""
    if line_type not in LINE_RANGES:
        raise ValueError("Тип линии: suction, return или pressure")
    low, high = LINE_RANGES[line_type]
    if velocity < low:
        return f"ниже ориентировочного диапазона {low}-{high} м/с"
    if velocity > high:
        return f"выше ориентировочного диапазона {low}-{high} м/с"
    return f"в пределах ориентировочного диапазона {low}-{high} м/с"


# ---------- Консольный интерфейс ----------

def ask_number(prompt, default=None):
    """Спрашивает число у пользователя, пока не будет введено корректное."""
    while True:
        text = input(prompt).strip().replace(",", ".")
        if text == "" and default is not None:
            return default
        try:
            return float(text)
        except ValueError:
            print("Введите число, например 12.5")


def menu_cylinder():
    pressure = ask_number("Давление, бар: ")
    bore = ask_number("Диаметр поршня, мм: ")
    rod = ask_number("Диаметр штока, мм (Enter, если не нужен): ", default=0)
    flow = ask_number("Расход, л/мин: ")
    print(f"Усилие при выдвижении: {cylinder_force_kn(pressure, bore):.2f} кН")
    print(f"Скорость выдвижения: {cylinder_speed_mm_s(flow, bore):.1f} мм/с")
    if rod > 0:
        print(f"Усилие при втягивании: {cylinder_force_kn(pressure, bore, rod):.2f} кН")
        print(f"Скорость втягивания: {cylinder_speed_mm_s(flow, bore, rod):.1f} мм/с")


def menu_pump():
    displacement = ask_number("Рабочий объём, см³/об: ")
    rpm = ask_number("Частота вращения, об/мин: ")
    vol_eff = ask_number("Объёмный КПД (Enter = 0.95): ", default=0.95)
    pressure = ask_number("Рабочее давление, бар: ")
    total_eff = ask_number("Общий КПД (Enter = 0.85): ", default=0.85)
    flow = pump_flow_l_min(displacement, rpm, vol_eff)
    power = pump_power_kw(flow, pressure, total_eff)
    print(f"Подача насоса: {flow:.1f} л/мин")
    print(f"Мощность на валу: {power:.2f} кВт")


def menu_pipe():
    flow = ask_number("Расход, л/мин: ")
    diameter = ask_number("Внутренний диаметр трубы, мм: ")
    print("Тип линии: 1 - всасывающая, 2 - сливная, 3 - напорная")
    choice = input("Выбор: ").strip()
    line_type = {"1": "suction", "2": "return", "3": "pressure"}.get(choice)
    if line_type is None:
        raise ValueError("Нужно выбрать 1, 2 или 3")
    velocity = pipe_velocity_m_s(flow, diameter)
    print(f"Скорость потока: {velocity:.2f} м/с, {velocity_note(velocity, line_type)}")


def main():
    actions = {"1": menu_cylinder, "2": menu_pump, "3": menu_pipe}
    while True:
        print("\n=== Гидравлический калькулятор ===")
        print("1 - Гидроцилиндр")
        print("2 - Насос")
        print("3 - Трубопровод")
        print("0 - Выход")
        choice = input("Выберите пункт: ").strip()
        if choice == "0":
            break
        action = actions.get(choice)
        if action is None:
            print("Нет такого пункта меню")
            continue
        try:
            action()
        except ValueError as error:
            print(f"Ошибка: {error}")


if __name__ == "__main__":
    main()
