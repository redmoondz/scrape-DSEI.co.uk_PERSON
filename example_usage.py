#!/usr/bin/env python3
"""
Пример использования парсера с дополнительными настройками
"""

import sys
import os
import csv

# Добавляем текущую директорию в путь Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.scraper import DSEISpeakerScraper
from config.settings import SPEAKERS_CSV_FILE


def analyze_results():
    """Анализирует результаты парсинга"""
    if not os.path.exists(SPEAKERS_CSV_FILE):
        print("❌ Файл с результатами не найден. Запустите сначала парсер.")
        return
    
    speakers = []
    with open(SPEAKERS_CSV_FILE, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        speakers = list(reader)
    
    companies = {}
    countries = {}
    with_social = 0
    with_sessions = 0
    
    for speaker in speakers:
        company = speaker.get('company', '').strip()
        if company:
            companies[company] = companies.get(company, 0) + 1
            
        country = speaker.get('country', '').strip()
        if country:
            countries[country] = countries.get(country, 0) + 1
            
        if speaker.get('social_network', '').strip():
            with_social += 1
            
        if speaker.get('session_date', '').strip():
            with_sessions += 1
    
    print(f"\n📊 АНАЛИЗ РЕЗУЛЬТАТОВ:")
    print(f"=" * 40)
    print(f"Всего спикеров: {len(speakers)}")
    print(f"Уникальных компаний: {len(companies)}")
    print(f"Уникальных стран: {len(countries)}")
    print(f"Спикеров с социальными сетями: {with_social}")
    print(f"Спикеров с информацией о сессиях: {with_sessions}")
    
    print(f"\n🏢 ТОП-5 КОМПАНИЙ:")
    top_companies = sorted(companies.items(), key=lambda x: x[1], reverse=True)[:5]
    for company, count in top_companies:
        print(f"  • {company}: {count} спикер(ов)")
    
    print(f"\n🌍 ТОП-5 СТРАН:")
    top_countries = sorted(countries.items(), key=lambda x: x[1], reverse=True)[:5]
    for country, count in top_countries:
        print(f"  • {country}: {count} спикер(ов)")


def main():
    """Главная функция с расширенным функционалом"""
    print("🚀 Запуск расширенного парсера спикеров DSEI...")
    print("=" * 50)
    
    try:
        # Запускаем парсер
        scraper = DSEISpeakerScraper()
        scraper.run()
        
        # Анализируем результаты
        analyze_results()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Парсинг прерван пользователем")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n\n❌ Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
