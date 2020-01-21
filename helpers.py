import requests
import urllib.parse
import os
import random

# link naar rapidapi met voorgeprogrammeerde functies
# https://goo.gl/9XTKTZ

def get_meal(query, diet, intolerances):
    response = requests.get(f"https://api.spoonacular.com/recipes/complexSearch?query={(query)}&course&instructionsRequired=true&intolerances={(intolerances)}&diet={(diet)}&number=5&apiKey=966dd37a9cba411dbdf6c4d9c5575c64")
    quote = response.json()
    choice = random.randrange(0, 5)
    return {
        "id": quote["results"][choice]["id"],
        "meal": quote["results"][choice]["title"],
        "image": quote["results"][choice]["image"]

    }



#print(lookup("rice", None, ["Dairy", "Egg"]))

#print(get_meal("macaroni", None, ["Dairy", "Egg"]))

