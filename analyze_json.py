import json

# Загружаем JSON
with open("HealthAutoExport-latest.json","r",encoding="utf-8") as f:
    data = json.load(f)

metrics = {}

# Безопасная функция для получения последнего qty или Avg/totalSleep
def get_metric_value(m):
    d = m.get("data", [])
    if not d:
        return None
    last = d[-1]
    # 1. qty
    if "qty" in last:
        return last["qty"]
    # 2. value (на всякий случай)
    if "value" in last:
        return last["value"]
    # 3. sleep_analysis special case
    if m.get("name") == "sleep_analysis":
        return last.get("totalSleep", 0)
    # 4. heart_rate special case
    if m.get("name") == "heart_rate":
        return last.get("Avg", last.get("qty", 0))
    return None

# Составляем словарь с последними значениями
for m in data.get("data", {}).get("metrics", []):
    metrics[m.get("name","unknown")] = get_metric_value(m)

# Функция расчета %
def percentage(value, min_value, max_value):
    if value is None:
        return 0
    return max(0, min(100, int((value - min_value)/(max_value - min_value)*100)))

# Проценты для отображения на ESP
heart = percentage(metrics.get("heart_rate",70), 60, 100)
sleep = percentage(metrics.get("sleep_analysis",7.4), 6, 9)
active = percentage(metrics.get("active_energy",400), 300, 1000)

# Генерация советов
advice = []
if metrics.get("step_count",0) and metrics.get("step_count",0) < 4000:
    advice.append("Мало шагов, пройдись вечером")
if metrics.get("apple_stand_time",0) and metrics.get("apple_stand_time",0) < 6:
    advice.append("Встань с кресла на пару минут")
if metrics.get("sleep_analysis",0) and metrics.get("sleep_analysis",0) < 6:
    advice.append("Недосып, ляг раньше сегодня")

advice_text = " | ".join(advice) if advice else "Здоровье в порядке 👍"

# Сохраняем готовый JSON для ESP32
output = {
    "heart_rate": heart,
    "sleep": sleep,
    "active_energy": active,
    "advice": advice_text
}

with open("latest.json","w",encoding="utf-8") as f:
    json.dump(output,f,ensure_ascii=False)

print("latest.json created!")
