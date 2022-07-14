from bs4 import BeautifulSoup
import sqlite3
from sqlite3 import Error
import requests

DATABASE_PATH = 'wiki_city.db'
urls = ['https://ru.wikipedia.org/wiki/%D0%93%D0%BE%D1%80%D0%BE%D0%B4%D1%81%D0%BA%D0%B8%D0%B5_%D0%BD%D0%B0%D1%81%D0%B5%D0%BB%D1%91%D0%BD%D0%BD%D1%8B%D0%B5_%D0%BF%D1%83%D0%BD%D0%BA%D1%82%D1%8B_%D0%9C%D0%BE%D1%81%D0%BA%D0%BE%D0%B2%D1%81%D0%BA%D0%BE%D0%B9_%D0%BE%D0%B1%D0%BB%D0%B0%D1%81%D1%82%D0%B8']


def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except Error as e:
        raise e

    return connection


# Получить веб-страницу (текстовая информация)
def fetch(url):
    try:
        response = requests.get(url)
        return response.text
    except Exception as e:
        raise e


def parser(html):
    data = []
    soup = BeautifulSoup(html, "lxml")
    book_list = soup.find('table', class_="standard sortable")('td')

    for i in range(0, len(book_list), 8):
        name = book_list[i + 1].string
        population = book_list[i + 4].get('data-sort-value')
        link = 'https://ru.wikipedia.org' + book_list[i + 1].a.get('href')
        data.append((name, population, link))

    connection = create_connection(DATABASE_PATH)
    cursor = connection.cursor()
    query = "INSERT INTO City (name, population, link) VALUES (?, ?, ?)"
    exist_check = "SELECT * FROM City WHERE name=?"
    update = "UPDATE City SET population=?, link=? WHERE name=?"

    for row in data:
        check_update = cursor.execute(exist_check, (row[0], )).fetchone()
        if check_update:
            if not(check_update[2] == row[1] and check_update[3] == row[2]):
                cursor.execute(update, (row[1], row[2], row[0]))
        else:
            cursor.execute(query, row)
    connection.commit()


# Обработка веб-страницы
def download(url):
    html = fetch(url)
    parser(html)


def parser_main():
    download(urls[0])
    print('all data is parse')