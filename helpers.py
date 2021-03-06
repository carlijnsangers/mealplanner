import requests
import urllib.parse
import os
import random
import socket

# Sends a query to spoonacular api with a query, intolerances and diet
def get_meal(query, diet, intolerances):
    response = requests.get(f"https://api.spoonacular.com/recipes/complexSearch?query={(query)}&type=main%20course&instructionsRequired=true&intolerances={(intolerances)}&diet={(diet)}&number=5&apiKey=66782ca4d8e24d71a170b2629ecd82fb")
    meal = response.json()

    # Selects a random result
    if "results" in meal:
        if len(meal['results']) >1:
            number = random.randint(1, len(meal['results'])) -1
        else:
            number = 0

        # If there are 0 results then it sends another query and tries again
        if len(meal['results']) == 0:
            query = get_query(diet)
            return get_meal(query, diet, intolerances)

        # Return result in specific format
        return {
            "id": meal["results"][number]["id"],
            "meal": meal["results"][number]["title"],
            "image": meal["results"][number]["image"],
            "title": meal["results"][number]["title"]
        }
    return

# Query for the ingredients en steps of recipe
def lookup(idr):
    response = requests.get(f"https://api.spoonacular.com/recipes/{(idr)}/analyzedInstructions?apiKey=66782ca4d8e24d71a170b2629ecd82fb")
    ingredients = requests.get(f"https://api.spoonacular.com/recipes/{(idr)}/ingredientWidget.json?apiKey=66782ca4d8e24d71a170b2629ecd82fb")

    # Return results in a specific format
    rep = response.json()
    ing = ingredients.json()
    return{
        "steps": rep[0]["steps"],
        "ingredients": ing["ingredients"]
    }

# Get the ip of the user so results can be saved
def get_IP():
    try:
        host_name = socket.gethostname()
        host_ip = socket.gethostbyname(host_name)
        return host_ip
    except:
        return

# Returns a random recipe ingredient and removes ingredients which conflict with diet
def get_query(diet):
    querys = ["pasta", "burger", "salad", "chicken", "potatoes", "rice", "pizza", "lasagne", "nasi", "risotto", "schnitzel", "cauliflower", "spinach", "spaghetti", "chili", "steak", "broccoli"]
    vegan = ["burger", "chicken", "schnitzel", "steak"]
    pescatarian = ['burger', 'chicken', "schnitzel", "steak"]

    if diet == "vegan" or diet == "vegetarian":
        for option in vegan:
            querys.remove(option)

    elif diet == 'pescatarian':
        for option in pescatarian:
            querys.remove(option)

    return random.choice(querys)