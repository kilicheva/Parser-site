import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


# получаем все теги
def get_links(url):
    # настройка параметров Chrome-драйвера
    chrome_options = Options()
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Mobile Safari/537.36")
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(options=chrome_options)

    driver.get(url)
    time.sleep(5)

    # прокрутка страницы
    for _ in range(5):
        # прокрутка верх
        driver.execute_script("window.scrollTo(0, 0);")
        # прокрутка вниз
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # обработка целевой веб-страницы с помощью Beautiful Soup
        soup = BeautifulSoup(driver.page_source, 'lxml')  # html.parser

        # получаем элементы по 'class="feed__chunk"'
        elements = soup.select('.feed__chunk')
        # получаем последний элемент из списка "elements", содержащий ссылки
        elements = elements[-1].select('.content-link')

        # итерируемся по каждому элементу и проверяем наличие ссылки
        links = []
        for element in elements:
            if element.get('href') not in links:
                links.append(element.get('href'))

        yield links

