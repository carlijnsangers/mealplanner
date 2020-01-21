import requests
import urllib.parse
import os

# link naar rapidapi met voorgeprogrammeerde functies
# https://goo.gl/9XTKTZ

def lookup(meal):
    try:
        api_key = os.environ.get("API_KEY")
        response = requests.get(f"https://api.spoonacular.com/food/products/search?query={(meal)}&apiKey={api_key}")
        response.raise_for_status()
        #print(api_key)
    except requests.RequestException:
        print("1")
        return None

    try:
        quote = response.json()
        return {
            "title": quote["title"],
            "image": float(quote["image"]),
        }
    except (KeyError, TypeError, ValueError):
        return None

print(lookup("yoghurt"))


