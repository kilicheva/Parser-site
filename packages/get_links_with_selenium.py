import asyncio
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def get_links(url):
    chrome_options = Options()
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Mobile Safari/537.36")
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(options=chrome_options)

    driver.get("https://vc.ru/popular/")
    time.sleep(1)

    # scroll for page
    while True:
        # scroll to top
        driver.execute_script("window.scrollTo(0, 0);")
        # scroll to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        asyncio.sleep(10)
        # print(i)

        # parsing the target web page with Beautiful Soup
        soup = BeautifulSoup(driver.page_source, 'lxml')  # html.parser

        elements = soup.select('.feed__chunk')
        # print(elements)
        elements = elements[-1].select('.content-link')

        links = []
        for element in elements:
            # print(element.get('href'))
            if element.get('href') not in links:
                links.append(element.get('href'))

        yield links

