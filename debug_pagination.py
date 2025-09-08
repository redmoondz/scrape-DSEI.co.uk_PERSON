import requests
from bs4 import BeautifulSoup

def check_pagination():
    """Проверяем структуру пагинации на сайте"""
    
    url = 'https://www.dsei.co.uk/forums/overview/speakers'
    params = {
        'sortby': 'personSurname asc',
        'searchgroup': 'A2A12251-speakers',
        'page': '1'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(url, params=params, headers=headers)
    print(f"URL запроса: {response.url}")
    print(f"Статус код: {response.status_code}")
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    print('=== ПОИСК ПАГИНАЦИИ ===')
    
    # Ищем все div с пагинацией по тексту
    all_divs = soup.find_all('div')
    pagination_divs = [div for div in all_divs if div.get('class') and any('pagination' in str(cls).lower() for cls in div.get('class', []))]
    print(f"Найдено div с pagination: {len(pagination_divs)}")
    for div in pagination_divs:
        print(f'  Классы: {div.get("class")}')
    
    # Ищем все ссылки с page= в href
    all_links = soup.find_all('a', href=True)
    page_links = [link for link in all_links if 'page=' in link.get('href', '')]
    print(f'\nНайдено ссылок с page=: {len(page_links)}')
    for i, link in enumerate(page_links[:10]):
        href = link.get('href', '')
        text = link.get_text().strip()
        print(f'  {i+1}. href={href} | text="{text}"')
    
    # Ищем спикеров - проверяем разные селекторы
    print(f'\n=== ПОИСК СПИКЕРОВ ===')
    
    # Вариант 1
    speaker_items1 = soup.find_all('div', class_='m-speakers-list__items__item')
    print(f'm-speakers-list__items__item: {len(speaker_items1)}')
    
    # Вариант 2
    speaker_items2 = soup.find_all('article', class_='m-speakers-list__item')
    print(f'article m-speakers-list__item: {len(speaker_items2)}')
    
    # Вариант 3
    speaker_items3 = soup.find_all('div', class_='m-speakers-list__item')
    print(f'div m-speakers-list__item: {len(speaker_items3)}')
    
    # Ищем все элементы со ссылками на speakers/
    speaker_links = soup.find_all('a', href=True)
    speaker_href_count = 0
    for link in speaker_links:
        href = link.get('href', '')
        if '/speakers/' in href:
            speaker_href_count += 1
            if speaker_href_count <= 5:  # Показываем первые 5
                print(f'  Ссылка на спикера: {href} | Текст: {link.get_text().strip()[:50]}')
    
    print(f'Всего ссылок на /speakers/: {speaker_href_count}')
    
    # Проверим страницу 2
    print('\n=== ПРОВЕРКА СТРАНИЦЫ 2 ===')
    params['page'] = '2'
    response2 = requests.get(url, params=params, headers=headers)
    soup2 = BeautifulSoup(response2.content, 'html.parser')
    
    speaker_links2 = soup2.find_all('a', href=True)
    speaker_href_count2 = sum(1 for link in speaker_links2 if '/speakers/' in link.get('href', ''))
    print(f'Ссылок на спикеров на странице 2: {speaker_href_count2}')
    
    # Найдем максимальный номер страницы
    all_page_nums = []
    for link in page_links:
        href = link.get('href', '')
        if 'page=' in href:
            try:
                page_num = int(href.split('page=')[1].split('&')[0])
                all_page_nums.append(page_num)
            except:
                continue
    
    if all_page_nums:
        max_page = max(all_page_nums)
        print(f'\nМаксимальный номер страницы: {max_page}')

if __name__ == "__main__":
    check_pagination()
