import gdown
import os
from datetime import datetime

# Публичная папка Google Drive
folder_url = "https://drive.google.com/drive/folders/1TIO-pvMaTW62cmq6rdn4t4FvYZEwA8b_?usp=sharing"

# Скачиваем все файлы из папки
gdown.download_folder(folder_url, output="downloaded", quiet=True)

# Находим все JSON-файлы
files = [f for f in os.listdir("downloaded") if f.endswith(".json")]

# Находим самый свежий файл по дате в имени
latest_file = max(
    files,
    key=lambda f: datetime.strptime('-'.join(f.split('-')[1:4]).replace('.json',''), '%Y-%m-%d')
)

# Полный путь к последнему файлу
latest_path = os.path.join("downloaded", latest_file)

# Копируем в корень репо для анализа
os.replace(latest_path, "HealthAutoExport-latest.json")
print(f"Latest file: {latest_file}")
