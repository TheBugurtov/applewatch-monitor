import json

# Загружаем скачанный файл
with open("HealthAutoExport-latest.json","r",encoding="utf-8") as f:
    data = json.load(f)

# Функции для расчета процентов
def percentage(value, min_value, max_value):
    return max(0, min(100, int((value - min_value)/(max_value - min_value)*100)))

# Берем последние значения метрик
metrics = {m['name']: m['data'][-1]['qty'] for m in data['data']['metrics']}

heart = percentage(metrics.get('heart_rate',70), 60, 100)
sleep = percentage(metrics.get('sleep_analysis',8), 6, 9)
active = percentage(metrics.get('active_energy',400), 300, 1000)

# Генерируем советы
advice_list = []
if metrics.get('steps',0) < 4000:
    advice_list.append("Мало шагов, пройдись вечером")
if metrics.get('apple_stand_time',0) < 6:
    advice_list.append("Встань с кресла на пару минут")
if metrics.get('sleep_analysis',0) < 6:
    advice_list.append("Недосып, ляг раньше сегодня")

advice = " | ".join(advice_list) if advice_list else "Здоровье в порядке 👍"

# Сохраняем готовый JSON для ESP32
output = {
    "heart_rate": heart,
    "sleep": sleep,
    "active_energy": active,
    "advice": advice
}

with open("latest.json","w",encoding="utf-8") as f:
    json.dump(output,f,ensure_ascii=False)

print("latest.json created!")
