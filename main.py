import requests
from tqdm import tqdm

all_games_url = "https://api.steampowered.com/ISteamApps/GetAppList/v0002/?key=STEAMKEY&format=json"
game_info_url = "https://store.steampowered.com/api/appdetails?appids="


def get_games(url):
    games = requests.get(url).json()["applist"]["apps"]
    return games


def get_games_info(url):
    games = get_games(all_games_url)
    games = list(filter(lambda x: x["name"], games))

    data = []

    for game in tqdm(games):

        game_info_answer = requests.get(url + str(game["appid"])).json()

        if game_info_answer and game_info_answer[str(game["appid"])]["success"]:

            if game_info_answer[str(game["appid"])]["data"]["type"] == "game":

                if not game_info_answer[str(game["appid"])]["data"]["is_free"]:

                    if not game_info_answer[str(game["appid"])]["data"]["release_date"]["coming_soon"]:

                        if game_info_answer[str(game["appid"])]["data"].get("price_overview"):

                            if game_info_answer[str(game["appid"])]["data"]["price_overview"]["discount_percent"] != 0:

                                if game_info_answer[str(game["appid"])]["data"].get("genres"):
                                    genres = [i["description"] for i in
                                              game_info_answer[str(game["appid"])]["data"]["genres"]]
                                else:
                                    genres = []

                                if game_info_answer[str(game["appid"])]["data"].get("screenshots"):
                                    screenshots = [i["path_thumbnail"] for i in
                                                   game_info_answer[str(game["appid"])]["data"]["screenshots"]]
                                else:
                                    screenshots = []

                                name = game_info_answer[str(game["appid"])]["data"]["name"]
                                short_description = game_info_answer[str(game["appid"])]["data"][
                                    "short_description"]
                                discount = game_info_answer[str(game["appid"])]["data"]["price_overview"][
                                    "discount_percent"]
                                base_price = game_info_answer[str(game["appid"])]["data"]["price_overview"][
                                    "initial_formatted"]
                                current_price = game_info_answer[str(game["appid"])]["data"]["price_overview"][
                                    "final_formatted"]
                                platforms = game_info_answer[str(game["appid"])]["data"]["platforms"]

                                data.append({
                                    "name": name,
                                    "short_description": short_description,
                                    "discount": discount,
                                    "base_price": base_price,
                                    "current_price": current_price,
                                    "platforms": platforms,
                                    "screenshots": screenshots,
                                    "genres": genres
                                })


if __name__ == "__main__":
    get_games_info(game_info_url)
