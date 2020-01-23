import requests
import urllib.parse
import os
import random
import socket

# link naar rapidapi met voorgeprogrammeerde functies
# https://goo.gl/9XTKTZ

key = "1fa0943622124891a2991ba8f9a89e9c"


def get_meal(query, diet, intolerances):
    response = requests.get(f"https://api.spoonacular.com/recipes/complexSearch?query={(query)}&course&instructionsRequired=true&intolerances={(intolerances)}&diet={(diet)}&number=5&apiKey=966dd37a9cba411dbdf6c4d9c5575c64")
    quote = response.json()
    if len(quote['results']) >1:
        number = random.randint(1, len(quote['results'])) -1
    else:
        number = 0
    print(quote, len(quote['results']), number)
    if len(quote['results']) == 0:
        print("error")
        return "error"
    return {
        "id": quote["results"][number]["id"],
        "meal": quote["results"][number]["title"],
        "image": quote["results"][number]["image"],
        "title": quote["results"][number]["title"]
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
