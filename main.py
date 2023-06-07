import asyncio
import csv
import json
import re
import sys

import aiohttp as aiohttp

from bs4 import BeautifulSoup
from packages.get_links_with_selenium import get_links


# переходим по полученной ссылке, получаем HTML и обрабатываем его с помощью BeautifulSoup
async def get_website(url):
    # определение заголовка User-Agent для использования в GET-запросе
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/113.0.0.0 Mobile Safari/537.36 "
    }
    # создание клиентской сессии с использованием aiohttp
    async with aiohttp.ClientSession() as session:
        # получение целевой веб-страницы
        async with session.get(url=url, headers=headers, ssl=False) as req:
            # обработка целевой веб-страницы с помощью Beautiful Soup
            soup = BeautifulSoup(await req.text(), 'lxml')  # html.parser

            return soup


# из полученной HTML-страницы находим текст и теги
async def get_website_data(soup):
    website_data = {}

    # получаем элемент заголовка по 'class="content-title"'
    try:
        title_element = soup.select_one('.content-title')
    except AttributeError:
        return False

    # в словарь добавляем полученный тег
    try:
        website_data[title_element.get_text(strip=True)] = title_element.name
    except AttributeError:
        return False

    # получаем элементы текста по 'class="content"'
    contents = soup.select_one('.content')

    # удаление ненужных элементов (тегов)
    for i in ('style', 'textarea', '.content-info',):
        tags = soup.select(i)
        for tag in tags:
            tag.extract()

    # проходимся по каждому элементу(тегу), найденные тексты и теги добавляем в словарь
    for tag in contents.find_all():
        # получением имя тега
        match_tag = re.search(r'<(\w+)', str(tag))
        # формируем логику для извлечения данных
        pattern = re.compile(r'<([^<>]+)>([^<>][а-яА-Яa-zA-Z0-9\s.,;:!?-]+)')  # (<([^<>]+)>([^<>]+))
        # исключение некоторых тегов
        if (re.match(pattern, str(tag))) and (match_tag.group(1) not in ['a', ]) and len(
                tag.get_text(strip=True).split()) > 1:
            website_data[tag.get_text(strip=True)] = tag.name

    return website_data


# получаем из функции get_website() данные, полученные данные записываем в файлы
async def get_data(links):
    # открываем файл JSON, читаем данные и записываем их в переменную 'data'
    # если файл не найден, создаем новую пустую переменную 'data'
    try:
        with open('data.json', "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}

    # итерируемся по каждой ссылке
    for url in links:
        # с помощью BeautifulSoup обработанный HTML возвращаем
        soup: BeautifulSoup = await get_website(url)
        # функция get_website_data() возвращает текст и теги
        content_data = await get_website_data(soup)
        if not content_data:
            continue

        # сортируем данные по значению
        content_data = dict(sorted(content_data.items(), key=lambda x: x[1]))
        # добавляем новые данные в переменную 'data'
        data[url] = content_data

        # записываем новые данные в файл 'data.csv'
        # создаем список с заголовками и текущим URL
        data_for_csv = [('Ссылка на статью', "Блок текста из статьи", "Формирование блока текста"), [url]]
        # добавляем в список отсортированные данные из content_data
        for text, tag in content_data.items():
            data_for_csv.append(['', text, tag])
        # открываем файл 'data.csv' в режиме добавления и записываем данные с помощью csv.writer
        with open('data.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerows(
                data_for_csv
            )

    # записываем новые данные в файл 'data.json'
    with open('data.json', "w") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


async def main():
    # главная страница
    url = "https://vc.ru/popular/"
    # получаем ссылки с помощью генератора для заданного URL
    generator_links = get_links(url)
    # 5 раз возвращаем новые ссылки
    for _ in range(5):
        # получаем все ссылки из генератора
        links = next(generator_links)

        # обрабатываем полученные ссылки
        # вызываем функцию get_data() и передаем ссылки
        try:
            await get_data(links)
        except TypeError:
            print(f'Данные не получен, ошибка: {sys.exc_info()[0]}, {sys.exc_info()[1]}')
            return


if '__main__' == __name__:
    asyncio.run(main())
