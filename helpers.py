import requests
import urllib.parse
import os
import random
import socket

key = "1fa0943622124891a2991ba8f9a89e9c"


def get_meal(query, diet, intolerances):
    response = requests.get(f"https://api.spoonacular.com/recipes/complexSearch?query={(query)}&type=main%20course&instructionsRequired=true&intolerances={(intolerances)}&diet={(diet)}&number=5&apiKey=66782ca4d8e24d71a170b2629ecd82fb")
    meal = response.json()

    if "results" in meal:
        if len(meal['results']) >1:
            number = random.randint(1, len(meal['results'])) -1
        else:
            number = 0

        if len(meal['results']) == 0:
            return {"id":158185,"title":"Chickpea and Broccoli Bowl with Tahini Sauce","image":"https://spoonacular.com/recipeImages/158185-312x231.jpg","imageType":"jpg"}
        return {
            "id": meal["results"][number]["id"],
            "meal": meal["results"][number]["title"],
            "image": meal["results"][number]["image"],
            "title": meal["results"][number]["title"]
        }
    return


def lookup(idr):
    response = requests.get(f"https://api.spoonacular.com/recipes/{(idr)}/analyzedInstructions?apiKey=66782ca4d8e24d71a170b2629ecd82fb")
    ingredients = requests.get(f"https://api.spoonacular.com/recipes/{(idr)}/ingredientWidget.json?apiKey=66782ca4d8e24d71a170b2629ecd82fb")
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

def get_query(diet):
    querys = ["pasta", "burger", "salad", "chicken", "potatoes", "rice", "pizza", "lasagne", "nasi", "risotto", "schnitzel", "cauliflower", "spinach", "spaghetti", "chili"]
    vegan = ["burger", "chicken", "schnitzel"]
    pescatarian = ['burger', 'chicken', "schnitzel"]
    if diet == "vegan" or diet == "vegetarian":
        for option in vegan:
            querys.remove(option)
    elif diet == 'pescatarian':
        for option in pescatarian:
            querys.remove(option)
    return random.choice(querys)