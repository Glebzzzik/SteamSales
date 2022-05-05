import requests, json

url = "http://api.steampowered.com/ISteamApps/GetAppList/v0002/?key=STEAMKEY&format=json"
game_info_url = "http://store.steampowered.com/api/appdetails?appids="


def get_games(url):
    games = requests.get(url).json()["applist"]["apps"]
    return games


def get_games_info(game_info_url):
    games = get_games(url)
    games = list(filter(lambda x: x["name"], games))

    for game in games:

        game_info_answer = requests.get(game_info_url + str(game["appid"])).json()

        if game_info_answer:

            if game_info_answer[str(game["appid"])]["success"]:

                if game_info_answer[str(game["appid"])]["data"]["type"] == "game":

                    if game_info_answer[str(game["appid"])]["data"]["is_free"] is False:
                        print(game_info_answer)


# for game in games:
#
#
#
#         game_info_answer = requests.get(game_info_url + str(game["appid"])).json()
#
#         if game_info_answer:
#             game_info_answer = game_info_answer[str(game["appid"])]
#
#             if game_info_answer["success"]:
#                 game_info_answer = game_info_answer["data"]
#
#                 if game_info_answer["is_free"] is False:
#
#                     if game_info_answer["release_date"]["coming_soon"] is False:
#                         print(str(game["appid"]))
#                         if game_info_answer["price_overview"]["discount_percent"] != 0:
#                             print(str(game["appid"]))
#                             name = game_info_answer["name"]
#                             print(name)
#                             print(game_info_answer["price_overview"])
#                             if game_info_answer["genres"]:
#                                 print(game_info_answer["genres"])
#                             print()
#
#

if __name__ == "__main__":
    get_games_info(game_info_url)
