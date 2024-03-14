import csv
import re
from time import sleep

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

with open("movies.csv", "a", newline="", encoding="utf-8") as file:
    headers = [
        "page_url",
        "img_url",
        "movie_title",
        "description",
        "movie_type",
        "genres",
        "year",
        "actors",
        "director",
        "imdb",
        "kinopoisk",
    ]
    writer = csv.DictWriter(file, fieldnames=headers)
    # writer.writeheader()
    for i in tqdm(range(974, 1041), desc="Processing"):
        page = requests.get(f"https://kinogo.uk/page/{i}/").text
        soup = BeautifulSoup(page, "html.parser")
        links = soup.find_all("h2", class_="card__title")

        for link in links:
            sleep(0.5)
            film = requests.get(link.find("a")["href"]).text
            movie_soup = BeautifulSoup(film, "html.parser")
            try:
                title = movie_soup.find("h1").text
                title = re.sub(r"\((\d+)\)", "", title).strip()
            except AttributeError:
                pass
            try:
                description = movie_soup.find(
                    class_="page__text full-text clearfix"
                ).get_text()
            except AttributeError:
                pass
            try:
                img_source = f"kinogo.uk/{movie_soup.find(class_='page ignore-select pmovie').find('img')['src']}"
            except AttributeError:
                img_source = ""
            try:
                genres = movie_soup.find(
                    class_="pmovie__header-list flex-grow-1"
                ).find_all("span", itemprop="genre")
            except AttributeError:
                pass
            genres = [genre.text for genre in genres][0].split(",")
            if len(genres) > 1:
                movie_type = genres[0]
                genres = " ,".join(genres[1:])
            else:
                movie_type = genres[0].strip()
            try:
                actors = (
                    movie_soup.find(class_="pmovie__header-list flex-grow-1")
                    .find("span", itemprop="actor")
                    .text
                )
            except AttributeError:
                actors = "Нет"
            try:
                year = (
                    movie_soup.find(class_="pmovie__header-list flex-grow-1")
                    .find("span", itemprop="copyrightYear")
                    .text
                )
            except AttributeError:
                year = 0
            try:
                director = (
                    movie_soup.find(class_="pmovie__header-list flex-grow-1")
                    .find(itemprop="director")
                    .text
                )
            except AttributeError:
                director = "Нет"
            try:
                imdb = float(
                    re.sub(
                        r"\(\s*\d+(\s+\d+)*\s*(?:K)?\s*\)",
                        "",
                        movie_soup.find(class_="card__rating-ext imdb").text,
                    )
                )
            except AttributeError:
                imdb = 0.0
            try:
                kinopoisk = float(
                    re.sub(
                        r"\(\s*\d+(\s+\d+)*\s*(?:K)?\s*\)",
                        "",
                        movie_soup.find(class_="card__rating-ext kp").text,
                    )
                )
            except AttributeError:
                kinopoisk = 0.0
            writer.writerow(
                {
                    "page_url": link.find("a")["href"],
                    "img_url": img_source,
                    "movie_title": title,
                    "description": description,
                    "movie_type": movie_type,
                    "genres": genres,
                    "year": year,
                    "actors": actors,
                    "director": director,
                    "imdb": imdb,
                    "kinopoisk": kinopoisk,
                }
            )
