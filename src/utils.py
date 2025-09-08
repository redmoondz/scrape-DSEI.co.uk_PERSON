import logging
import time
import csv
import re
from typing import List
from datetime import datetime


def setup_logging(log_file: str) -> logging.Logger:
    """Настройка логирования"""
    logger = logging.getLogger('dsei_scraper')
    logger.setLevel(logging.INFO)
    
    # Создаем форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Файловый хендлер
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Консольный хендлер
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def extract_slug_from_javascript(js_text: str) -> str:
    """Извлекает slug из JavaScript кода"""
    # Ищем паттерн 'speakers/slug'
    pattern = r"speakers/([^'\"]+)"
    match = re.search(pattern, js_text)
    if match:
        return match.group(1)
    return ""


def clean_text(text: str) -> str:
    """Очищает текст от лишних символов и пробелов"""
    if not text:
        return ""
    
    # Убираем лишние пробелы и переносы строк
    text = re.sub(r'\s+', ' ', text.strip())
    # Убираем HTML entities
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', "'")
    
    return text.strip()


def parse_session_time(time_text: str) -> str:
    """Парсит время сессии из HTML"""
    if not time_text:
        return ""
    
    # Ищем паттерн времени HH:MM - HH:MM
    time_pattern = r'(\d{2}:\d{2})\s*[–-]\s*(\d{2}:\d{2})'
    match = re.search(time_pattern, time_text)
    if match:
        return f"{match.group(1)} – {match.group(2)}"
    
    return clean_text(time_text)


def save_to_csv(speakers: List[dict], filename: str) -> None:
    """Сохраняет данные спикеров в CSV файл"""
    if not speakers:
        return
    
    # Упорядочиваем колонки
    columns_order = [
        'speaker_url', 'speaker_slug', 'name', 'position', 'company',
        'country', 'description', 'social_network', 'session_date',
        'session_time', 'session_location', 'session_topic_link',
        'session_topic_title'
    ]
    
    # Сохраняем в CSV
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns_order)
        writer.writeheader()
        
        for speaker in speakers:
            # Убеждаемся что все поля есть
            row = {}
            for col in columns_order:
                row[col] = speaker.get(col, "")
            writer.writerow(row)


def get_current_timestamp() -> str:
    """Возвращает текущую временную метку"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def delay_request(seconds: int = 1) -> None:
    """Делает паузу между запросами"""
    time.sleep(seconds)
