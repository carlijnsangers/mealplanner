import requests
import urllib.parse
import os

# link naar rapidapi met voorgeprogrammeerde functies
# https://goo.gl/9XTKTZ

def lookup(query, diet, intolerances):
    response = requests.get(f"https://api.spoonacular.com/food/products/search?query={()}&instructionsRequired=true&intolerances={(intolerances)}&diet={(diet)}&number=5&ins&apiKey=966dd37a9cba411dbdf6c4d9c5575c64")
    quote = response.json()
    return {
        "meal": quote["products"][0]["title"],
        "image": quote["products"][0]["image"]
    }


print(lookup("rice", None, ["Dairy", "Egg"]))
