# pip install requests
# pip install beautifulsoup4
# pip install lxml
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
flats = []
import requests
from bs4 import BeautifulSoup
from pprint import pprint
from requests_html import HTMLSession

url = 'https://realt.by/sale/flats/'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0'}
# response = HTMLSession().get(url, headers=headers)
# response.html.render()
# with open('test.html', 'w', encoding='utf-8') as f:
#     f.write(response.text)
#
with open('test.html', encoding='utf-8') as f:
    data = f.read()
soup = BeautifulSoup(data, 'lxml')
raw_links = soup.find_all('a', class_='z-1 absolute top-0 left-0 w-full h-full cursor-pointer', href=True)
links = []
tel = []
raw_tel = soup.find_all("a",
                        class_="focus:outline-none transition-colors cursor-pointer text-inherit hover:text-inherit active:text-inherit",
                        href=True)
for el in raw_links:
    link = f'https://realt.by{el["href"]}'
    links.append(link)
# for el in raw_tel:
#     tel_ = f'tel: {el["href"]}'
#     tel.append(tel_)
print(raw_tel)
for link in links:
    resp = requests.get(link, headers=headers)
    s = BeautifulSoup(resp.text, 'lxml')
    title = s.find('h1', {
        "class": "order-1 mb-0.5 md:-order-2 md:mb-4 block w-full !inline-block lg:text-h1Lg text-h1 font-raleway font-bold flex items-center"}).text
    try:
        price = s.find('h2',
                       class_='!inline-block mr-1 lg:text-h2Lg text-h2 font-raleway font-bold flex items-center').text.replace(
            'р.', '').replace(' ', '')
    #
    except Exception as e:
        price = ''
    try:
        descr = s.find("div", class_=["description_wrapper__tlUQE"]).text
    except Exception as e:
        descr = ""
    pprint(resp.url)
    # pprint(descr)
    try:
        image = s.find("div", class_="absolute inset-0").find_all("img")[1]["src"]
    except:
        image = ""
    pprint(image)
    raw_params = s.find_all("li", class_="relative py-1")
    params = {}
    for param in raw_params:
        key = param.find("span").text
        if key not in PARAM_PATTERN:
            continue
        value = param.find(["a", "p"]).text.replace("г. ", "").replace(" м²", "")
        params[key] = value
    flat = {
        "title": title,
        "price": int(price),
        "link": link,
        "descr": descr,
        "image": image,
        "params": params,

    }
    flats.append(flat)
    pprint(flats)
