import requests
from bs4 import BeautifulSoup
from pprint import pprint
from tqdm import tqdm
import sqlite3
PARAM_PATTERN = (
    'Количество комнат',
    'Площадь общая',
    'Год постройки',
    'Этаж / этажность',
    'Тип дома',
    'Область',
    'Населенный пункт',
    'Улица',
    'Район города',
    'Координаты'
)
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0'}
URL = 'https://realt.by/sale/flats/'

def get_last_page() -> int:
    response = requests.get(URL, headers=headers).text
    soup = BeautifulSoup(response, 'lxml')
    last_page = soup.find_all('a',
                              class_='focus:outline-none sm:focus:shadow-10bottom cursor-pointer select-none inline-flex font-normal text-body min-h-[2.5rem] min-w-[2.5rem] py-0 items-center !px-1.25 justify-center mx-1 hover:bg-basic-200 rounded-md disabled:text-basic-500')
    last_page = last_page[-1].text
    return int(last_page)


def get_all_links(last_page: int) -> list:
    links = []
    for page in tqdm(range(1, last_page + 1), desc='PARSER URLS: '):
        response = requests.get(f'{URL}?page={page}', headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        raw_links = soup.find_all('a', class_='z-1 absolute top-0 left-0 w-full h-full cursor-pointer', href=True)
        urls = [f'https://realt.by{el["href"]}' for el in raw_links]
        links.extend(urls)

    return links


def get_flats_data(links: list) -> dict:
    flats = {}
    for link in tqdm(links, desc='parsing data: '):
        flat = dict.fromkeys([
            'Количество комнат',
            'Площадь общая',
            'Год постройки',
            'Этаж / этажность',
            'Тип дома',
            'Область',
            'Населенный пункт',
            'Улица',
            'Район города',
            'Координаты',
            'title',
            'price',
            'image',
            'description'
        ])

        resp = requests.get(link, headers=headers)
        flat_id = resp.url.split('/')[-2]
        s = BeautifulSoup(resp.text, 'lxml')
        try:
            title = s.find('h1', {
                "class": "order-1 mb-0.5 md:-order-2 md:mb-4 block w-full !inline-block lg:text-h1Lg text-h1 font-raleway font-bold flex items-center"}).text
        except AttributeError:
            title = ""
        try:
            price = s.find('h2',
                           class_='!inline-block mr-1 lg:text-h2Lg text-h2 font-raleway font-bold flex items-center').text.replace(
                'р.', '').replace(' ', '')
        #
        except AttributeError:
            price = '-1'

        try:
            description = s.find('div', class_=['description_wrapper__tlUQE']).text
        except AttributeError:
            description = ''
        # pprint(description)

        try:
            image = s.find('div', class_='absolute inset-0').find_all('img')[1]['src']
        except AttributeError:
            image = ''
        # print(image)
        raw_params = s.find_all('li', class_='relative py-1')

        for param in raw_params:
            key = param.find('span').text
            if key not in PARAM_PATTERN:
                continue
            value = param.find(['p', 'a']).text.replace('г. ', '').replace(' м²', '')
            flat[key] = value

        flat['title'] = title
        flat['price'] = int(price)
        flat['image'] = image
        flat['description'] = description
        flats[flat_id] = flat
        global data
        data = flats.copy()
    return flats

def create_db():
    conn = sqlite3.connect('flats.db')
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS flats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        'Количество комнат' TEXT,
        'Площадь общая' TEXT,
        'Год постройки' TEXT,
        'Этаж / этажность' TEXT,
        'Тип дома' TEXT,
        'Область' TEXT,
        'Населенный пункт' TEXT,
        'Улица' TEXT,
        'Район города' TEXT,
        'Координаты' TEXT,
        title TEXT, 
        price INTEGER, 
        image TEXT, 
        description TEXT, 
        flat_id TEXT
    )""")
    conn.commit()
    conn.close()


def insert_db(flats: dict):

    conn = sqlite3.connect('flats.db')
    cur = conn.cursor()
    for key, flat in flats.items():
        cur.execute("""INSERT INTO flats (
        'Количество комнат',
        'Площадь общая',
        'Год постройки',
        'Этаж / этажность',
        'Тип дома',
        'Область',
        'Населенный пункт',
        'Улица',
        'Район города',
        'Координаты',
        title, 
        price, 
        image, 
        description, 
        flat_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        flat["Количество комнат"],
                        flat["Площадь общая"],
                        flat['Год постройки'],
                        flat["Этаж / этажность"],
                        flat["Тип дома"],
                        flat["Область"],
                        flat["Населенный пункт"],
                        flat["Улица"],
                        flat["Район города"],
                        flat["Координаты"],
                        flat['title'],
                        flat['price'],
                        flat['image'],
                        flat['description'],
                        key)
                    )
    conn.commit()
    conn.close()


def get_flats_from_db():
    conn = sqlite3.connect('flats.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM flats")
    flats = cur.fetchall()
    print(flats)

def run_parser():
    last_page = get_last_page()
    links = get_all_links(last_page)
    flats = get_flats_data(links)
    create_db()
    insert_db(flats)
    get_flats_from_db()

run_parser()