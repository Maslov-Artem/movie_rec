import csv
import re

import requests
from bs4 import BeautifulSoup, Tag
from tqdm import tqdm


def scrape_mail_movies():
    """
    Scrape movie data from the mail.ru website and save it to a CSV file.
    """
    # Open CSV file for writing movie data
    with open("mail_movies.csv", "a", newline="", encoding="utf-8") as file:
        fieldnames = [
            "page_url",
            "img_url",
            "movie_title",
            "description",
            "genres",
            "year",
            "actors",
            "director",
            "imdb",
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        # Set HTTP headers to mimic a browser request
        headers = {
            "Content-Type": "text/html",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        }

        # Loop through pages of movies on the website
        for i in tqdm(range(1, 1301), desc="Processing"):
            # Fetch page content
            page = requests.get(
                f"https://kino.mail.ru/cinema/all/?page={i}", headers=headers
            ).text.encode("utf-8")
            soup = BeautifulSoup(page, "html.parser")

            # Find all movie links on the page
            links = soup.find_all(
                class_="link link_inline link-holder link-holder_itemevent link-holder_itemevent_small",
            )

            # Loop through movie links
            for link in tqdm(links, desc="Processing"):
                # Extract movie page URL
                movie_page_url = f'https://kino.mail.ru{link["href"]}'
                try:
                    # Fetch movie page content
                    movie_page = requests.get(movie_page_url).text
                    movie_soup = BeautifulSoup(movie_page, "html.parser")

                    # Extract movie data from the page
                    description = (
                        movie_soup.find(
                            class_="text text_inline text_light_medium text_fixed valign_baseline p-movie-info__description-text"
                        ).text.strip()
                        if movie_soup.find(
                            class_="text text_inline text_light_medium text_fixed valign_baseline p-movie-info__description-text"
                        )
                        else None
                    )

                    image_url = (
                        movie_soup.find(class_="picture p-framer__picture").find("img")[
                            "src"
                        ]
                        if movie_soup.find(class_="picture p-framer__picture")
                        else None
                    )

                    title_element = (
                        movie_soup.find(class_="p-movie-intro__content-inner").find(
                            "h1"
                        )
                        if movie_soup.find(class_="p-movie-intro__content-inner")
                        else None
                    )
                    title = title_element.text.strip() if title_element else None
                    year_match = re.search(r"\((\d+)\)", title)
                    year = year_match.group(1) if year_match else None
                    title = re.sub(r"\(\d+\)", "", title).strip() if title else None

                    genres = (
                        [
                            genre.text
                            for genre in movie_soup.find_all(class_="badge__text")
                        ]
                        if movie_soup.find_all(class_="badge__text")
                        else None
                    )

                    actors = (
                        [
                            actor.text
                            for actor in movie_soup.find_all(
                                "span",
                                class_="p-truncate__inner js-toggle__truncate-inner",
                            )[1]
                            if isinstance(actor, Tag) and actor.name == "a"
                        ]
                        if movie_soup.find_all(
                            "span", class_="p-truncate__inner js-toggle__truncate-inner"
                        )
                        else None
                    )

                    director_element = (
                        movie_soup.find(
                            class_="p-truncate__inner js-toggle__truncate-inner"
                        ).find("a")
                        if movie_soup.find(
                            class_="p-truncate__inner js-toggle__truncate-inner"
                        )
                        else None
                    )
                    director = (
                        director_element.text.strip() if director_element else None
                    )

                    imdb_element = (
                        movie_soup.find(
                            class_="p-movie-rates__item p-movie-rates__item_border_left nowrap"
                        )
                        if movie_soup.find(
                            class_="p-movie-rates__item p-movie-rates__item_border_left nowrap"
                        )
                        else None
                    )
                    imdb = imdb_element.text.strip("IMDb") if imdb_element else None

                    # Write movie data to CSV
                    writer.writerow(
                        {
                            "page_url": movie_page_url,
                            "img_url": image_url,
                            "movie_title": title,
                            "description": description,
                            "genres": genres,
                            "year": year,
                            "actors": actors,
                            "director": director,
                            "imdb": imdb,
                        }
                    )
                except Exception as e:
                    print(f"Error processing {movie_page_url}: {e}")


if __name__ == "__main__":
    scrape_mail_movies()
