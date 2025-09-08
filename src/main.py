#!/usr/bin/env python3
"""
Главный файл для запуска парсера спикеров DSEI
"""

import sys
import os

# Добавляем корневую директорию в путь Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scraper import DSEISpeakerScraper


def main():
    """Главная функция"""
    print("🚀 Запуск парсера спикеров DSEI...")
    print("=" * 50)
    
    try:
        scraper = DSEISpeakerScraper()
        scraper.run()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Парсинг прерван пользователем")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n\n❌ Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
