import requests
from bs4 import BeautifulSoup as BS
import csv

CSV = 'Gamestop_results.csv'
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
                'card_img': item.find('img', class_='image-16x9').get('src')
            }
        )
    return games


def save_results_to_csv(items, path):
    with open(path, 'w', newline='', encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Review name', 'Review link', 'Reviewer internet portal', 'Image link'])
        for item in items:
            writer.writerow([item['title'], item['review_link'], item['brand'], item['card_img']]) # writing data to .csv


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
