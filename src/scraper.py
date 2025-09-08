import requests
import time
import re
from typing import List, Optional, Union, Dict, Any
from urllib.parse import urljoin, urlencode
from bs4 import BeautifulSoup, Tag
from tqdm import tqdm

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import *
from src.models import Speaker, SpeakerSlug
from src.utils import (
    setup_logging, extract_slug_from_javascript, clean_text,
    parse_session_time, save_to_csv, delay_request
)


class DSEISpeakerScraper:
    """Основной класс для парсинга спикеров с сайта DSEI"""
    
    def __init__(self):
        self.logger = setup_logging(LOG_FILE)
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.speakers_slugs: List[SpeakerSlug] = []
        self.speakers_data: List[Speaker] = []
        
    def get_page(self, url: str, params: Optional[Dict[str, Any]] = None, retries: int = MAX_RETRIES) -> Optional[BeautifulSoup]:
        """Получает страницу и возвращает объект BeautifulSoup"""
        for attempt in range(retries):
            try:
                self.logger.info(f"Запрос к {url} (попытка {attempt + 1}/{retries})")
                
                response = self.session.get(
                    url, 
                    params=params, 
                    timeout=REQUEST_TIMEOUT
                )
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                self.logger.info(f"Успешно получена страница: {response.url}")
                return soup
                
            except requests.RequestException as e:
                self.logger.error(f"Ошибка запроса {url}: {e}")
                if attempt < retries - 1:
                    delay_request(2 ** attempt)  # Экспоненциальная задержка
                else:
                    self.logger.error(f"Не удалось получить страницу после {retries} попыток")
                    
        return None
    
    def extract_speakers_slugs_from_page(self, soup: BeautifulSoup) -> List[SpeakerSlug]:
        """Извлекает список slug спикеров со страницы"""
        slugs = []
        seen_slugs = set()  # Для более эффективной дедупликации по slug
        
        # Ищем все ссылки с JavaScript функцией openRemoteModal
        speaker_links = soup.find_all('a')
        
        for link in speaker_links:
            if not isinstance(link, Tag):
                continue
                
            href = link.get('href')
            if not href or 'openRemoteModal' not in str(href) or 'speakers/' not in str(href):
                continue
                
            slug = extract_slug_from_javascript(str(href))
            
            if slug and slug not in seen_slugs:  # Проверяем только по slug
                seen_slugs.add(slug)
                
                # Попробуем получить имя спикера
                name = ""
                # Ищем в aria-label
                aria_label = link.get('aria-label')
                if aria_label:
                    name = clean_text(str(aria_label))
                else:
                    # Ищем в тексте ссылки или рядом
                    text_content = link.get_text(strip=True)
                    if text_content:
                        name = clean_text(text_content)
                
                speaker_slug = SpeakerSlug(slug=slug, name=name)
                slugs.append(speaker_slug)
                self.logger.info(f"Найден спикер: {name} (slug: {slug})")
        
        return slugs
    
    def check_for_next_page(self, soup: BeautifulSoup, current_page: int) -> bool:
        """Проверяет есть ли следующая страница"""
        # Ищем все ссылки с page= в href
        all_links = soup.find_all('a', href=True)
        page_numbers = []
        
        for link in all_links:
            href = link.get('href', '')
            if 'page=' in href:
                try:
                    # Извлекаем номер страницы из href
                    page_num = int(href.split('page=')[1].split('&')[0])
                    page_numbers.append(page_num)
                except (ValueError, IndexError):
                    continue
        
        if page_numbers:
            max_page = max(page_numbers)
            self.logger.info(f"Максимальная страница: {max_page}, текущая: {current_page}")
            return current_page < max_page
        
        return False
    
    def scrape_speakers_list(self) -> List[SpeakerSlug]:
        """Этап 1: Получение списка всех спикеров и их slug"""
        self.logger.info("=== ЭТАП 1: Получение списка спикеров ===")
        
        all_slugs = []
        seen_slugs = set()  # Глобальная дедупликация между страницами
        page = 1
        
        while True:
            self.logger.info(f"Обработка страницы {page}")
            
            # Формируем параметры запроса
            params = SPEAKERS_LIST_PARAMS.copy()
            params['page'] = str(page)
            
            soup = self.get_page(SPEAKERS_LIST_URL, params)
            if not soup:
                self.logger.error(f"Не удалось получить страницу {page}")
                break
            
            # Извлекаем slug со страницы
            page_slugs = self.extract_speakers_slugs_from_page(soup)
            
            if not page_slugs:
                self.logger.info(f"На странице {page} не найдено спикеров. Завершение.")
                break
            
            # Фильтруем дубликаты между страницами
            new_slugs = []
            for speaker_slug in page_slugs:
                if speaker_slug.slug not in seen_slugs:
                    seen_slugs.add(speaker_slug.slug)
                    new_slugs.append(speaker_slug)
            
            all_slugs.extend(new_slugs)
            self.logger.info(f"На странице {page} найдено {len(page_slugs)} спикеров ({len(new_slugs)} новых)")
            
            # Проверяем есть ли следующая страница
            if not self.check_for_next_page(soup, page):
                self.logger.info("Достигнута последняя страница")
                break
                
            page += 1
            delay_request(DELAY_BETWEEN_REQUESTS)
        
        self.logger.info(f"Всего найдено {len(all_slugs)} уникальных спикеров")
        return all_slugs
    
    def extract_speaker_details(self, soup: BeautifulSoup, slug: str) -> Speaker:
        """Извлекает детальную информацию о спикере"""
        speaker = Speaker()
        speaker.speaker_slug = slug
        speaker.speaker_url = f"{SPEAKER_DETAIL_URL}/{slug}"
        
        # Имя спикера
        title_elem = soup.find('h2', class_='m-speaker-entry__item__title')
        if title_elem:
            speaker.name = clean_text(title_elem.get_text())
        
        # Детали (позиция, компания, страна)
        details_elem = soup.find('div', class_='m-speaker-entry__item__details')
        if details_elem and isinstance(details_elem, Tag):
            # Позиция
            position_elem = details_elem.find('span', class_='m-speaker-entry__item__details__position')
            if position_elem:
                speaker.position = clean_text(position_elem.get_text()).rstrip(',')
            
            # Компания
            company_elem = details_elem.find('span', class_='m-speaker-entry__item__details__company')
            if company_elem:
                speaker.company = clean_text(company_elem.get_text())
            
            # Страна
            country_elem = details_elem.find('div', class_='m-speaker-entry__item__details__company__country')
            if country_elem:
                speaker.country = clean_text(country_elem.get_text())
        
        # Описание
        description_elem = soup.find('div', class_='m-speaker-entry__item__description')
        if description_elem:
            # Получаем весь текст, очищаем от HTML тегов
            description_text = description_elem.get_text()
            speaker.description = clean_text(description_text)
        
        # Социальные сети
        social_list = soup.find('ul', class_='m-speaker-entry__item__social')
        if social_list and isinstance(social_list, Tag):
            social_links = []
            for social_item in social_list.find_all('li'):
                if isinstance(social_item, Tag):
                    link = social_item.find('a')
                    if link and isinstance(link, Tag):
                        href = link.get('href')
                        if href:
                            social_links.append(str(href))
            speaker.social_network = '; '.join(social_links)
        
        # Информация о сессиях
        sessions_info = self.extract_session_info(soup)
        if sessions_info:
            speaker.session_date = sessions_info.get('date', '')
            speaker.session_time = sessions_info.get('time', '')
            speaker.session_location = sessions_info.get('location', '')
            speaker.session_topic_link = sessions_info.get('topic_link', '')
            speaker.session_topic_title = sessions_info.get('topic_title', '')
        
        return speaker
    
    def extract_session_info(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Извлекает информацию о сессиях"""
        session_info = {
            'date': '',
            'time': '',
            'location': '',
            'topic_link': '',
            'topic_title': ''
        }
        
        # Дата сессии
        date_elem = soup.find('div', class_='m-speaker-entry__item__sessions__list__item__date')
        if date_elem:
            session_info['date'] = clean_text(date_elem.get_text())
        
        # Время сессии  
        time_elem = soup.find('div', class_='m-speaker-entry__item__sessions__list__item__time')
        if time_elem:
            session_info['time'] = parse_session_time(time_elem.get_text())
        
        # Локация
        location_elem = soup.find('div', class_='m-speaker-entry__item__details__location')
        if location_elem:
            session_info['location'] = clean_text(location_elem.get_text())
        
        # Ссылка и название темы
        topic_link_elem = soup.find('a', class_='m-speaker-entry__item__sessions__list__item__title')
        if topic_link_elem and isinstance(topic_link_elem, Tag):
            href = topic_link_elem.get('href')
            if href:
                href_str = str(href)
                if href_str and not href_str.startswith('http'):
                    session_info['topic_link'] = urljoin(BASE_URL, href_str)
                else:
                    session_info['topic_link'] = href_str
            
            session_info['topic_title'] = clean_text(topic_link_elem.get_text())
        
        return session_info
    
    def scrape_speaker_details(self, speaker_slugs: List[SpeakerSlug]) -> List[Speaker]:
        """Этап 2: Получение детальной информации по каждому спикеру"""
        self.logger.info("=== ЭТАП 2: Получение детальной информации ===")
        
        speakers = []
        
        for speaker_slug in tqdm(speaker_slugs, desc="Обработка спикеров"):
            self.logger.info(f"Обработка спикера: {speaker_slug.slug}")
            
            # Формируем URL для детальной информации
            detail_url = f"{SPEAKER_DETAIL_URL}/{speaker_slug.slug}"
            
            soup = self.get_page(detail_url, SPEAKER_DETAIL_PARAMS)
            if not soup:
                self.logger.error(f"Не удалось получить данные для спикера {speaker_slug.slug}")
                continue
            
            speaker = self.extract_speaker_details(soup, speaker_slug.slug)
            
            # Если имя не удалось извлечь из детальной страницы, используем из списка
            if not speaker.name and speaker_slug.name:
                speaker.name = speaker_slug.name
            
            speakers.append(speaker)
            self.logger.info(f"Данные спикера {speaker.name} успешно извлечены")
            
            delay_request(DELAY_BETWEEN_REQUESTS)
        
        return speakers
    
    def run(self) -> None:
        """Запуск полного процесса парсинга"""
        self.logger.info("=== НАЧАЛО ПАРСИНГА СПИКЕРОВ DSEI ===")
        start_time = time.time()
        
        try:
            # Этап 1: Получение списка спикеров
            self.speakers_slugs = self.scrape_speakers_list()
            
            if not self.speakers_slugs:
                self.logger.error("Не найдено ни одного спикера. Завершение работы.")
                return
            
            # Этап 2: Получение детальной информации
            self.speakers_data = self.scrape_speaker_details(self.speakers_slugs)
            
            if not self.speakers_data:
                self.logger.error("Не удалось получить детальную информацию ни по одному спикеру.")
                return
            
            # Сохранение результатов
            speakers_dict = [speaker.to_dict() for speaker in self.speakers_data]
            save_to_csv(speakers_dict, SPEAKERS_CSV_FILE)
            
            # Итоги
            end_time = time.time()
            duration = end_time - start_time
            
            self.logger.info("=== ПАРСИНГ ЗАВЕРШЕН ===")
            self.logger.info(f"Всего найдено спикеров: {len(self.speakers_slugs)}")
            self.logger.info(f"Успешно обработано: {len(self.speakers_data)}")
            self.logger.info(f"Время выполнения: {duration:.2f} секунд")
            self.logger.info(f"Результат сохранен в: {SPEAKERS_CSV_FILE}")
            
            print(f"\n✅ Парсинг успешно завершен!")
            print(f"📊 Обработано спикеров: {len(self.speakers_data)}")
            print(f"💾 Результат сохранен в: {SPEAKERS_CSV_FILE}")
            print(f"⏱️  Время выполнения: {duration:.2f} сек")
            
        except Exception as e:
            self.logger.error(f"Критическая ошибка при парсинге: {e}", exc_info=True)
            print(f"❌ Ошибка: {e}")
        
        finally:
            self.session.close()
