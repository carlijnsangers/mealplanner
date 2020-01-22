import requests
import urllib.parse
import os
import random
import socket

# link naar rapidapi met voorgeprogrammeerde functies
# https://goo.gl/9XTKTZ

def get_meal(query, diet, intolerances):
    response = requests.get(f"https://api.spoonacular.com/recipes/complexSearch?query={(query)}&course&instructionsRequired=true&intolerances={(intolerances)}&diet={(diet)}&number=5&apiKey=966dd37a9cba411dbdf6c4d9c5575c64")
    quote = response.json()
    return {
        "id": quote["results"][0]["id"],
        "meal": quote["results"][0]["title"],
        "image": quote["results"][0]["image"]
    }



def lookup(idr):
    response = requests.get(f"https://api.spoonacular.com/recipes/{(idr)}/analyzedInstructions?apiKey=966dd37a9cba411dbdf6c4d9c5575c64")
    ingredients = requests.get(f"https://api.spoonacular.com/recipes/{(idr)}/ingredientWidget.json?apiKey=966dd37a9cba411dbdf6c4d9c5575c64")
    quote1 = response.json()
    quote2 = ingredients.json()
    return{
        "steps": quote1[0]["steps"],
        "ingredients": quote2["ingredients"]
    }

def get_IP():
    try:
        host_name = socket.gethostname()
        host_ip = socket.gethostbyname(host_name)
        return host_ip
    except:
        return

print(get_IP())
