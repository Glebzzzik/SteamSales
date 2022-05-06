import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import sqlite3

last_game = 0

salepage_url = "https://store.steampowered.com/search/results/?query&start={0}" \
               "&count=50&dynamic_data=&sort_by=_ASC&snr=1_7_7_2300_7&specials=1&infinite=1"

game_info_url = "https://store.steampowered.com/api/appdetails?appids="


def parse_salepage(url):

    games = []

    answer = requests.get(url.format(last_game)).json()
    for offset in tqdm(range(0, answer["total_count"], 50)):
        answer = requests.get(url.format(offset)).json()
        soup = BeautifulSoup(answer["results_html"], 'html.parser')
        links = soup.find_all("a")

        for i in links:
            appid = i.attrs.get("data-ds-appid")
            if appid:
                if len(appid.split(",")) == 1:
                    games.append(appid)
    return games


def get_info_about_games(url):
    games = []

    for appid in tqdm(parse_salepage(salepage_url)):
        answer = requests.get(url + appid).json()
        if answer:
            answer = answer[str(appid)]
            if answer["success"] and answer["data"]["type"] == "game" and not answer["data"]["is_free"]:
                name = answer["data"]["name"]
                short_description = answer["data"]["short_description"]
                discount_percent = answer["data"]["price_overview"]["discount_percent"]
                initial_price = answer["data"]["price_overview"]["initial_formatted"]
                final_formatted = answer["data"]["price_overview"]["final_formatted"]
                platforms = answer["data"]["platforms"]
                genres = [genre["description"] for genre in answer["data"]["genres"]]
                screenshots = [screenshot["path_thumbnail"] for screenshot in answer["data"]["screenshots"]]
                game_url = f"https://store.steampowered.com/app/{appid}"
                games.append({
                    "name": name,
                    "short_description": short_description,
                    "discount_percent": discount_percent,
                    "initial_price": initial_price,
                    "final_formatted": final_formatted,
                    "platforms": platforms,
                    "genres": genres,
                    "screenshots": screenshots,
                    "game_url": game_url,
                    "appid": appid
                })

    return games


def write_to_database():
    connection = sqlite3.connect("steam.db")
    for game in tqdm(get_info_about_games(game_info_url)):
        connection.execute(
            "INSERT INTO games ('appid', 'name', 'short_description', 'discount_percent', 'initial_price', 'final_formatted', 'windows', 'mac', 'linux', 'genres', 'screenshots', 'game_url') VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [game["appid"], game["name"], game["short_description"], game["discount_percent"], game["initial_price"],
             game["final_formatted"], game["platforms"]["windows"], game["platforms"]["mac"],
             game["platforms"]["linux"], ", ".join(game["genres"]),
             "\n".join(game["screenshots"]), game["game_url"]])
    connection.commit()
    connection.close()


if __name__ == "__main__":
    write_to_database()
