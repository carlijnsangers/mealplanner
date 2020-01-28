import requests
import urllib.parse
import os
import random
import socket

key = "1fa0943622124891a2991ba8f9a89e9c"


def get_meal(query, diet, intolerances):
    response = requests.get(f"https://api.spoonacular.com/recipes/complexSearch?query={(query)}&type=main%20course&instructionsRequired=true&intolerances={(intolerances)}&diet={(diet)}&number=5&apiKey=20f24d7da4b84efc97fad19457e5e9f2")
    meal = response.json()

    if "results" in meal:
        if len(meal['results']) >1:
            number = random.randint(1, len(meal['results'])) -1
        else:
            number = 0

        if len(meal['results']) == 0:
            print("error")
            return
        return {
            "id": meal["results"][number]["id"],
            "meal": meal["results"][number]["title"],
            "image": meal["results"][number]["image"],
            "title": meal["results"][number]["title"]
        }
    return


def lookup(idr):
    response = requests.get(f"https://api.spoonacular.com/recipes/{(idr)}/analyzedInstructions?apiKey=20f24d7da4b84efc97fad19457e5e9f2")
    ingredients = requests.get(f"https://api.spoonacular.com/recipes/{(idr)}/ingredientWidget.json?apiKey=20f24d7da4b84efc97fad19457e5e9f2")
    rep = response.json()
    ing = ingredients.json()
    return{
        "steps": rep[0]["steps"],
        "ingredients": ing["ingredients"]
    }

def get_IP():
    try:
        host_name = socket.gethostname()
        host_ip = socket.gethostbyname(host_name)
        return host_ip
    except:
        return

