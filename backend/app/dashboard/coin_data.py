from backend.app.utils.api import fetch_coin_data


def get_live_top_10_coins():
    coins, error = fetch_coin_data()
    if error:
        raise Exception(error)
    return coins