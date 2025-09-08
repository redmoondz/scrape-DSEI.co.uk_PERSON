# DSEI Speaker Scraper

Парсер для извлечения информации о спикерах с сайта DSEI.co.uk

## Структура проекта

```
├── src/                    # Исходный код
│   ├── main.py            # Точка входа
│   ├── scraper.py         # Основной класс парсера
│   ├── models.py          # Модели данных
│   └── utils.py           # Вспомогательные функции
├── data/                  # Данные
│   └── speakers.csv       # Результат парсинга
├── logs/                  # Логи
├── config/                # Конфигурация
│   └── settings.py        # Настройки
└── requirements.txt       # Зависимости
```

## Установка и запуск

1. Установить зависимости:
```bash
pip install -r requirements.txt
```

2. Запустить парсер:
```bash
python src/main.py
```

## Описание работы

Парсер работает в 2 этапа:

1. **Этап 1**: Получение списка спикеров и их slug
2. **Этап 2**: Детальная информация по каждому спикеру

Результат сохраняется в CSV файл с полями:
- speaker_url
- speaker_slug
- name
- position
- company
- country
- description
- social_network
- session_date
- session_time
- session_location
- session_topic_link
- session_topic_title
