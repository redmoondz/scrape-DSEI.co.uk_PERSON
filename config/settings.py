import os

# Настройки парсера
BASE_URL = "https://www.dsei.co.uk"
SPEAKERS_LIST_URL = "https://www.dsei.co.uk/forums/overview/speakers"
SPEAKER_DETAIL_URL = "https://www.dsei.co.uk/speakers"

# Параметры запросов
SPEAKERS_LIST_PARAMS = {
    "sortby": "personSurname asc",
    "searchgroup": "A2A12251-speakers"
}

SPEAKER_DETAIL_PARAMS = {
    "sortby": "personSurname asc", 
    "searchgroup": "libraryentry-speakers"
}

# Настройки HTTP
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

REQUEST_TIMEOUT = 30
DELAY_BETWEEN_REQUESTS = 1  # секунды

# Пути к файлам
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Создание директорий если не существуют
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Файлы результатов
SPEAKERS_CSV_FILE = os.path.join(DATA_DIR, "speakers.csv")
LOG_FILE = os.path.join(LOGS_DIR, "scraper.log")

# Максимальное количество попыток запроса
MAX_RETRIES = 3
