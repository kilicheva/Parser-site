import asyncio
import csv
import json
import re
import sys

import aiohttp as aiohttp
import requests

from bs4 import BeautifulSoup
from packages.get_links_with_selenium import get_links

data = dict()


async def get_website(url):
    print(1)
    # defining the User-Agent header to use in the GET request
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Mobile Safari/537.36"
    }
    async with aiohttp.ClientSession() as session:
        # retrieving the target web page
        async with session.get(url=url, headers=headers, ssl=False) as req:
            # parsing the target web page with Beautiful Soup
            soup = BeautifulSoup(await req.text(), 'lxml')  # html.parser

            return req, soup


async def get_website_data(soup):
    website_data = {}

    # get data(title: text, tag) and add to dict
    try:
        title_element = soup.select_one('.content-title')
    except AttributeError:
        return False

    try:
        website_data[title_element.get_text(strip=True)] = title_element.name
    except AttributeError:
        return False

    contents = soup.select_one('.content')

    # remove unnecessary tags
    for i in ['style', 'textarea', '.content-info', ]:
        tags = soup.select(i)
        for tag in tags:
            tag.extract()

    # retrieve each tag
    for tag in contents.find_all():
        # retrieve the tag name
        match_tag = re.search(r'<(\w+)', str(tag))
        # build logic for retrieving data (<([^<>]+)>([^<>]+))
        pattern = re.compile(r'<([^<>]+)>([^<>][а-яА-Яa-zA-Z0-9\s.,;:!?-]+)')
        # exclude the tags
        if (re.match(pattern, str(tag))) and (match_tag.group(1) not in ['a', ]) and len(
                tag.get_text(strip=True).split()) > 1:
            website_data[tag.get_text(strip=True)] = tag.name

    return website_data


# retrieve data and write to file
async def get_data(links):
    global data

    # Iterates over each link
    for url in links:
        # retrieve HTML
        soup = await get_website(url)
        print(135)
        # retrieve text and tags
        content_data = await get_website_data(soup[1])
        if not content_data:
            continue

        sorted_dict = dict(sorted(content_data.items(), key=lambda x: x[1]))
        data[url] = sorted_dict

        # write to file(csv and json)
        data_for_csv = [('Ссылка на статью', "Блок текста из статьи", "Формирование блока текста"), [url]]
        # add data to a list
        for text, tag in sorted_dict.items():
            data_for_csv.append(['', text, tag])
        # with open('data.csv', 'w', encoding='cp1251') as f: # for Windows
        with open('data.csv', 'a') as f:
            writer = csv.writer(f)  # delimiter=";" - (for Windows)
            writer.writerows(
                data_for_csv
            )

    # write to file(csv and json)
    # with open('data.json', 'w', encoding='utf-8') as f:
    with open('data.json', 'w') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


async def main():
    # home page
    url = "https://vc.ru/popular/"
    links = get_links(url)
    while True:
        # retrieve links from get_links_with_selenium
        link = next(links)

        # retrieve data and write to file
        # await get_data(link)
        try:
            await get_data(link)
        except TypeError:
            print(f'Данные не получен, ошибка: {sys.exc_info()[0]}, {sys.exc_info()[1]}')
            return


if '__main__' == __name__:
    asyncio.run(main())




