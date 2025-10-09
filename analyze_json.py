import json
from datetime import datetime

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
    if metric_name == "heart_rate":
        return last.get("Avg")  # Для пульса берем среднее значение
    elif metric_name == "heart_rate_variability":
        # Для HRV берем последнее значение (обычно это усредненное значение за измерение)
        return last.get("qty")
    elif metric_name == "blood_oxygen_saturation":
        return last.get("qty")
    elif metric_name == "resting_heart_rate":
        return last.get("qty")
    else:
        # Для всех остальных метрик используем qty
        return last.get("qty")

# Составляем словарь с последними значениями
for m in data.get("data", {}).get("metrics", []):
    name = m.get("name", "unknown")
    value = get_metric_value(m)
    if value is not None:
        metrics[name] = value

# Функция анализа метрик как профессиональный врач
def analyze_health_metrics(metrics):
    analysis = {
        "timestamp": datetime.now().isoformat(),
        "critical_metrics": {},
        "medical_analysis": "",
        "recommendations": [],
        "risk_level": "low",  # low, moderate, high
        "overall_score": 0
    }
    
    # Получаем ключевые метрики
    hrv = metrics.get("heart_rate_variability")
    spo2 = metrics.get("blood_oxygen_saturation")
    resting_hr = metrics.get("resting_heart_rate")
    heart_rate = metrics.get("heart_rate")
    
    # Анализ Вариабельности сердечного ритма (HRV)
    if hrv is not None:
        analysis["critical_metrics"]["hrv"] = {
            "value": hrv,
            "unit": "ms",
            "status": "normal"
        }
        if hrv < 20:
            analysis["critical_metrics"]["hrv"]["status"] = "poor"
            analysis["recommendations"].append("Критически низкая HRV - возможен сильный стресс или переутомление")
            analysis["risk_level"] = "high"
        elif hrv < 40:
            analysis["critical_metrics"]["hrv"]["status"] = "moderate"
            analysis["recommendations"].append("HRV ниже оптимального - рекомендуется отдых и снижение стресса")
            analysis["risk_level"] = "moderate"
        elif hrv > 100:
            analysis["critical_metrics"]["hrv"]["status"] = "excellent"
        else:
            analysis["critical_metrics"]["hrv"]["status"] = "good"
    
    # Анализ Кислорода в крови (SpO2)
    if spo2 is not None:
        analysis["critical_metrics"]["blood_oxygen"] = {
            "value": spo2,
            "unit": "%",
            "status": "normal"
        }
        if spo2 < 90:
            analysis["critical_metrics"]["blood_oxygen"]["status"] = "critical"
            analysis["recommendations"].append("КРИТИЧЕСКИЙ УРОВЕНЬ КИСЛОРОДА - НЕМЕДЛЕННО ОБРАТИТЕСЬ К ВРАЧУ")
            analysis["risk_level"] = "high"
        elif spo2 < 94:
            analysis["critical_metrics"]["blood_oxygen"]["status"] = "concerning"
            analysis["recommendations"].append("Низкий уровень кислорода - возможны нарушения дыхания во сне")
            analysis["risk_level"] = "moderate"
        elif spo2 < 96:
            analysis["critical_metrics"]["blood_oxygen"]["status"] = "borderline"
            analysis["recommendations"].append("Уровень кислорода на границе нормы - рекомендуется наблюдение")
        else:
            analysis["critical_metrics"]["blood_oxygen"]["status"] = "optimal"
    
    # Анализ Пульса в состоянии покоя
    resting_hr_to_use = resting_hr if resting_hr is not None else heart_rate
    if resting_hr_to_use is not None:
        analysis["critical_metrics"]["resting_heart_rate"] = {
            "value": resting_hr_to_use,
            "unit": "bpm",
            "status": "normal"
        }
        if resting_hr_to_use > 100:
            analysis["critical_metrics"]["resting_heart_rate"]["status"] = "tachycardia"
            analysis["recommendations"].append("Тахикардия в покое - рекомендуется консультация кардиолога")
            analysis["risk_level"] = "high"
        elif resting_hr_to_use > 85:
            analysis["critical_metrics"]["resting_heart_rate"]["status"] = "elevated"
            analysis["recommendations"].append("Повышенный пульс покоя - возможен стресс или недостаточное восстановление")
            analysis["risk_level"] = "moderate"
        elif resting_hr_to_use < 50:
            analysis["critical_metrics"]["resting_heart_rate"]["status"] = "bradycardia"
            analysis["recommendations"].append("Брадикардия - требуется наблюдение")
        else:
            analysis["critical_metrics"]["resting_heart_rate"]["status"] = "optimal"
    
    # Формируем общий медицинский анализ
    critical_count = sum(1 for metric in analysis["critical_metrics"].values() 
                        if metric["status"] in ["critical", "tachycardia"])
    concerning_count = sum(1 for metric in analysis["critical_metrics"].values() 
                          if metric["status"] in ["concerning", "elevated", "poor", "borderline"])
    
    if critical_count > 0:
        analysis["medical_analysis"] = "ТРЕБУЕТСЯ СРОЧНАЯ МЕДИЦИНСКАЯ КОНСУЛЬТАЦИЯ"
        analysis["overall_score"] = 20
    elif concerning_count > 0:
        analysis["medical_analysis"] = "Состояние требует внимания и наблюдения"
        analysis["overall_score"] = 50
    else:
        analysis["medical_analysis"] = "Показатели в пределах нормы"
        analysis["overall_score"] = 85
    
    # Добавляем общие рекомендации если нет специфических
    if not analysis["recommendations"]:
        analysis["recommendations"].append("Показатели в норме. Продолжайте мониторинг")
    
    return analysis

# Проверяем наличие ключевых метрик перед анализом
required_metrics = ["heart_rate_variability", "blood_oxygen_saturation"]
available_metrics = [metric for metric in required_metrics if metric in metrics]

print("Доступные ключевые метрики:")
for metric in available_metrics:
    print(f"- {metric}: {metrics[metric]}")

if len(available_metrics) >= 2:
    # Проводим медицинский анализ
    health_analysis = analyze_health_metrics(metrics)
    
    # Сохраняем полный анализ
    with open("health_analysis.json", "w", encoding="utf-8") as f:
        json.dump(health_analysis, f, ensure_ascii=False, indent=2)
    
    # Создаем упрощенную версию для вывода
    simplified_output = {
        "timestamp": health_analysis["timestamp"],
        "overall_score": health_analysis["overall_score"],
        "risk_level": health_analysis["risk_level"],
        "medical_analysis": health_analysis["medical_analysis"],
        "top_recommendations": health_analysis["recommendations"][:3],  # Первые 3 рекомендации
        "critical_metrics_summary": {}
    }
    
    # Добавляем сводку по ключевым метрикам
    for name, metric in health_analysis["critical_metrics"].items():
        simplified_output["critical_metrics_summary"][name] = {
            "value": metric["value"],
            "status": metric["status"]
        }
    
    # Сохраняем упрощенную версию
    with open("latest.json", "w", encoding="utf-8") as f:
        json.dump(simplified_output, f, ensure_ascii=False, indent=2)
    
    print("\nМЕДИЦИНСКИЙ АНАЛИЗ ЗАВЕРШЕН:")
    print(f"Общая оценка: {health_analysis['overall_score']}/100")
    print(f"Уровень риска: {health_analysis['risk_level']}")
    print(f"Заключение: {health_analysis['medical_analysis']}")
    print("\nРекомендации:")
    for rec in health_analysis["recommendations"]:
        print(f"- {rec}")
    
    print("\nФайлы сохранены: health_analysis.json (полный анализ), latest.json (упрощенный)")
    
else:
    print(f"\nВНИМАНИЕ: Недостаточно данных для анализа.")
    print(f"Найдено ключевых метрик: {len(available_metrics)} из {len(required_metrics)}")
    print("Убедитесь, что в данных присутствуют:")
    print("- heart_rate_variability (вариабельность сердечного ритма)")
    print("- blood_oxygen_saturation (кислород в крови)")
    
    # Сохраняем базовую информацию о доступных метриках
    basic_info = {
        "timestamp": datetime.now().isoformat(),
        "available_metrics": available_metrics,
        "error": "Недостаточно данных для медицинского анализа"
    }
    
    with open("latest.json", "w", encoding="utf-8") as f:
        json.dump(basic_info, f, ensure_ascii=False, indent=2)