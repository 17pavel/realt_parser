import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import sqlite3
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0"
}
URL = "https://realt.by/sale/flats/"


def get_last_page() -> int:
    response = requests.get(URL, headers=headers).text
    soup = BeautifulSoup(response, "lxml")
    last_page = soup.find_all(
        "a",
        class_="focus:outline-none sm:focus:shadow-10bottom cursor-pointer select-none inline-flex font-normal text-body min-h-[2.5rem] min-w-[2.5rem] py-0 items-center !px-1.25 justify-center mx-1 hover:bg-basic-200 rounded-md disabled:text-basic-500",
    )
    last_page = last_page[-1].text
    return int(last_page)


def get_all_flats(last_page: int) -> dict:
    flats = {}
    for page in tqdm(range(1, last_page + 1), desc="PARSER URLS: "):
        response = requests.get(f"{URL}?page={page}", headers=headers)
        soup = (
            BeautifulSoup(response.text, "lxml").find("script", id="__NEXT_DATA__").text
        )
        data = json.loads(soup)
        list_obj = data["props"]["pageProps"]["initialState"]["objectsListing"][
            "objects"
        ]
        for el in list_obj:
            flats[str(el["code"])] = {
                "rooms": el["rooms"],
                "areaTotal": el["areaTotal"],
                "buildingYear": el["buildingYear"],
                "title": el["title"],
                "description": el["description"],
                "price": el["price"],
                "pricePerM2": el["pricePerM2"],
                "contactPhones": str(el["contactPhones"]),
                "images": str(el["images"]),
                "flat_id": el["code"],
                "region": el["stateRegionName"],
                "city": el["townName"],
                "address": el["address"],
                "location": str(el["location"]),
                "storeys": el["storeys"],
                "storey": el["storey"],
                "houseType": el["houseType"],
            }
    return flats


def create_db():
    conn = sqlite3.connect("realt.db")
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS flats")
    cur.execute(
        """CREATE TABLE IF NOT EXISTS flats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        flat_id INTEGER unique,
        title TEXT,
        contactPhones TEXT,
        images TEXT,
        rooms TEXT,
        areaTotal INTEGER,
        buildingYear INTEGER,
        description TEXT,
        price INTEGER,
        pricePerM2 INTEGER,
        region TEXT,
        city TEXT,
        address TEXT,
        location TEXT,
        storeys INTEGER,
        storey INTEGR,
        houseType INTEGER
    )"""
    )
    conn.commit()
    conn.close()


def insert_db(flats: dict):
    conn = sqlite3.connect("realt.db")
    cur = conn.cursor()
    for flat in flats.values():
        col = ",".join(flat.keys())
        insert = f":{',:'.join(flat.keys())}"
        query = f"INSERT INTO flats ({col}) VALUES ({insert})"
        cur.execute(query, flat)
    conn.commit()
    conn.close()


def get_flats_from_db():
    conn = sqlite3.connect("realt.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM flats limit 10")
    flats = cur.fetchall()
    print(flats)


def run_parser():
    last_page = get_last_page()
    flats = get_all_flats(last_page)
    create_db()
    insert_db(flats)
    get_flats_from_db()


run_parser()
