import json

# Загружаем JSON
with open("HealthAutoExport-latest.json", "r", encoding="utf-8") as f:
    data = json.load(f)

metrics = {}

def get_metric_value(m):
    d = m.get("data", [])
    if not d:
        return None
    
    last = d[-1]
    metric_name = m.get("name")
    
    # Специфичная логика для разных метрик
    if metric_name == "sleep_analysis":
        return last.get("totalSleep")
    elif metric_name == "heart_rate":
        return last.get("Avg")  # Только Avg, без fallback на qty
    else:
        # Для всех остальных метрик используем qty
        return last.get("qty")

# Составляем словарь с последними значениями
for m in data.get("data", {}).get("metrics", []):
    name = m.get("name", "unknown")
    value = get_metric_value(m)
    if value is not None:
        metrics[name] = value

# Функция расчета % с безопасным округлением
def percentage(value, min_value, max_value):
    if value is None:
        return 0
    # Защита от деления на 0 и выхода за границы
    if max_value <= min_value:
        return 50  # Значение по умолчанию
    return max(0, min(100, int((value - min_value) / (max_value - min_value) * 100)))

# Получаем значения с проверкой на None
heart_rate_val = metrics.get("heart_rate")
sleep_val = metrics.get("sleep_analysis") 
active_energy_val = metrics.get("active_energy")

# Проценты для отображения на ESP (с значениями по умолчанию)
heart = percentage(heart_rate_val, 60, 100) if heart_rate_val is not None else 50
sleep_goal = 7  # цель сна 7 часов
sleep = int(min(max(0, sleep_val / sleep_goal * 100), 100)) if sleep_val is not None else 50 
active = percentage(active_energy_val, 300, 1000) if active_energy_val is not None else 50

# Генерация советов (только если данные есть)
advice = []

step_count = metrics.get("step_count")
if step_count is not None and step_count < 4000:
    advice.append("Мало шагов, пройдись вечером")

stand_time = metrics.get("apple_stand_time") 
if stand_time is not None and stand_time < 6:
    advice.append("Встань с кресла на пару минут")

sleep_analysis = metrics.get("sleep_analysis")
# Обновил совет по сну - теперь сравниваем с целью 7 часов
if sleep_analysis is not None and sleep_analysis < sleep_goal:
    advice.append(f"Недосып, цель {sleep_goal}ч")

advice_text = " | ".join(advice) if advice else "Здоровье в порядке 👍"

# Дополнительная отладочная информация
print("Отладочная информация:")
print(f"Найдены метрики: {list(metrics.keys())}")
print(f"Значения: HR={heart_rate_val}, Sleep={sleep_val}, Steps={step_count}")
print(f"Процент сна: {sleep}% (цель: {sleep_goal} часов)")

# Сохраняем готовый JSON для ESP32
output = {
    "heart_rate": heart,
    "sleep": sleep, 
    "active_energy": active,
    "advice": advice_text
}

with open("latest.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("latest.json created successfully!")