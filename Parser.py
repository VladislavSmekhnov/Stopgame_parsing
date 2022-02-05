import requests
from bs4 import BeautifulSoup as BS
import csv
import pymysql

from config import host, user, password, db_name


CSV = 'Stopgame_results.csv'
HOST = 'https://stopgame.ru'
URL = 'https://stopgame.ru/review/new/izumitelno/'
HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'
}


def get_html(url, pageNumber, params=''):
    correct_url = url + str(pageNumber)
    req = requests.get(correct_url, headers=HEADERS, params=params)
    return req


def get_content(html):
    soup = BS(html, 'html.parser')
    items = soup.find_all('div', class_='item article-summary') # find all reviews on page
    games = []
    for item in items:
        games.append(
            {
                'title': item.find('div', class_='caption caption-bold').get_text(strip=True),
                'review_link': HOST + item.find('div', class_='caption caption-bold').find('a').get('href'),
                'brand': HOST,
                'image': item.find('img', class_='image-16x9').get('src')
            }
        )
    return games


def save_results_to_csv(items, path):
    with open(path, 'w', newline='', encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Review name', 'Review link', 'Reviewer internet portal', 'Image link'])
        for item in items:
            writer.writerow([item['title'], item['review_link'], item['brand'], item['image']])


def parser():
    games = []
    PAGENATION = input('Specify the quantity of pages to parse: ')
    PAGENATION = int(PAGENATION.strip())
    html = get_html(URL, 1)
    if html.status_code == 200: # check the connection and if successfully:
        print('The parsing process has started successfully...')
        for page in range(1, PAGENATION + 1):
            print(f'Page: {page}')
            html = get_html(URL, pageNumber=page)
            games.extend(get_content(html.text))
        print('Parsing has finished successfully!')
        #print(games)
    else: # or:
        print('Error! -> ' + URL)
    save_results_to_csv(games, CSV) # saving results in .csv in the path of your project
    print('Your results successfully saved in ' + CSV)


parser()


try:
    connection = pymysql.connect(
        host=host,
        port=3306,
        user=user,
        password=password,
        database=db_name,
        cursorclass=pymysql.cursors.DictCursor
    )
    print("Successfully connected...")
    try:
        with connection.cursor() as cursor:
            create_table_query = "CREATE TABLE `stopgame_db`(id int unsigned NOT NULL AUTO_INCREMENT," \
                                 " title varchar(150)," \
                                 " review_link varchar(256)," \
                                 " brand varchar(256)," \
                                 " image varchar(256), PRIMARY KEY (id));"
            cursor.execute(create_table_query)
            print("Table created successfully...")
            with open(CSV) as csv_file:
                csvfile = csv.reader(csv_file, delimiter=';')
                all_values = []
                for row in csvfile:
                    value = (row[0], row[1], row[2], row[3])
                    all_values.append(value)

            query = "INSERT INTO `stopgame_db`(`title`, `review_link`, `brand`, `image`) VALUES (%s, %s, %s, %s)"
            mycursor = connection.cursor()
            mycursor.executemany(query, all_values)
            connection.commit()
    finally:
        connection.close()
except Exception as ex:
    print("Connection refused...")
    print(ex)





